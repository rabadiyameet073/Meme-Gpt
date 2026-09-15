"""
MemeGPT — Unit & Integration Tests for Monitoring, Observability, and Analytics (Guide 13).
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.monitoring import (
    init_monitoring,
    filter_transactions,
    capture_exception,
    capture_message,
)
from app.services.email_service import (
    send_email,
    send_welcome_email,
    send_collection_share_email,
    send_magic_link_email,
    send_account_alert_email,
)

client = TestClient(app)


# ── Sentry Monitoring Tests ───────────────────────────────────────────────────

def test_sentry_filter_transactions():
    """Verify filter_transactions excludes noisy endpoints."""
    # Health checks should be dropped
    assert filter_transactions({"transaction": "/health"}, None) is None
    assert filter_transactions({"transaction": "/api/v1/health"}, None) is None
    assert filter_transactions({"transaction": "GET /api/v1/health/status"}, None) is None
    assert filter_transactions({"transaction": "/favicon.ico"}, None) is None

    # Normal application endpoints must be retained
    event = {"transaction": "POST /api/v1/search"}
    assert filter_transactions(event, None) == event

    event2 = {"transaction": "GET /api/v1/memes/drake-pointing"}
    assert filter_transactions(event2, None) == event2


def test_sentry_init_without_dsn(monkeypatch):
    """Verify init_monitoring skips safely when no DSN configured."""
    from app.config import settings
    monkeypatch.setattr(settings, "SENTRY_DSN", "")

    mock_sentry = MagicMock()
    with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
        init_monitoring()
        mock_sentry.init.assert_not_called()


def test_sentry_init_with_dsn(monkeypatch):
    """Verify init_monitoring initializes sentry_sdk with valid settings."""
    from app.config import settings
    test_dsn = "https://public_key@sentry.example.com/42"
    monkeypatch.setattr(settings, "SENTRY_DSN", test_dsn)
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "APP_ENV", "production")

    mock_sentry = MagicMock()
    mock_fastapi = MagicMock()
    mock_sqlalchemy = MagicMock()
    mock_redis = MagicMock()

    with patch.dict("sys.modules", {
        "sentry_sdk": mock_sentry,
        "sentry_sdk.integrations.fastapi": mock_fastapi,
        "sentry_sdk.integrations.sqlalchemy": mock_sqlalchemy,
        "sentry_sdk.integrations.redis": mock_redis,
    }):
        init_monitoring()
        mock_sentry.init.assert_called_once()
        kwargs = mock_sentry.init.call_args[1]
        assert kwargs["dsn"] == test_dsn
        assert kwargs["environment"] == "production"
        assert kwargs["traces_sample_rate"] == 0.2
        assert kwargs["profiles_sample_rate"] == 0.1
        assert kwargs["before_send_transaction"] == filter_transactions


def test_sentry_capture_helpers():
    """Verify capture_exception and capture_message execute safely."""
    mock_sentry = MagicMock()
    with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
        capture_exception(ValueError("Test exception"))
        mock_sentry.capture_exception.assert_called_once()

        capture_message("Test message", level="warning")
        mock_sentry.capture_message.assert_called_once_with("Test message", level="warning")


# ── Health & Diagnostics Endpoints ───────────────────────────────────────────

def test_health_endpoint_response_contract():
    """Verify /api/v1/health satisfies the 99.5% uptime monitoring requirements."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "uptime_seconds" in data
    assert "services" in data
    assert data["services"]["database"] in ("connected", "ok", "error")


def test_sentry_test_endpoint():
    """Verify /api/v1/health/sentry-test returns 200 OK."""
    resp = client.get("/api/v1/health/sentry-test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_sentry_error_endpoint():
    """Verify /api/v1/health/sentry-error triggers a 500 error for Sentry verification."""
    resp = client.get("/api/v1/health/sentry-error")
    assert resp.status_code == 500
    data = resp.json()
    assert "Intentional test error" in data["detail"]


# ── Resend Email Service Tests ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_email_no_key(monkeypatch):
    """Verify email is gracefully skipped when no RESEND_API_KEY is configured."""
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    from app.config import settings
    monkeypatch.setattr(settings, "RESEND_API_KEY", "")

    sent = await send_email("user@example.com", "Test", "<p>Hello</p>")
    assert sent is False


@pytest.mark.asyncio
async def test_send_email_mock_success(monkeypatch):
    """Verify email sends successfully when Resend returns HTTP 200."""
    monkeypatch.setenv("RESEND_API_KEY", "re_mock_test_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        sent = await send_email("user@example.com", "Welcome", "<h1>Welcome!</h1>")
        assert sent is True
        mock_post.assert_called_once()
        payload = mock_post.call_args[1]["json"]
        assert payload["to"] == ["user@example.com"]
        assert payload["subject"] == "Welcome"


@pytest.mark.asyncio
async def test_send_email_mock_failure(monkeypatch):
    """Verify email returns False when Resend returns an error code."""
    monkeypatch.setenv("RESEND_API_KEY", "re_mock_test_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        sent = await send_email("user@example.com", "Alert", "<h1>Alert</h1>")
        assert sent is False


@pytest.mark.asyncio
async def test_welcome_email_dispatch():
    """Verify send_welcome_email builds proper content."""
    with patch("app.services.email_service.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        res = await send_welcome_email("alice@example.com", "Alice")
        assert res is True
        mock_send.assert_called_once()
        to, subj, html = mock_send.call_args[0]
        assert to == "alice@example.com"
        assert "Welcome to MemeGPT" in subj
        assert "Alice" in html


@pytest.mark.asyncio
async def test_collection_share_email_dispatch():
    """Verify send_collection_share_email builds proper content."""
    with patch("app.services.email_service.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        res = await send_collection_share_email(
            "bob@example.com",
            sender_name="Alice",
            collection_name="Reaction Memes",
            share_url="https://app.memegpt.com/share/c/123",
        )
        assert res is True
        mock_send.assert_called_once()
        to, subj, html = mock_send.call_args[0]
        assert to == "bob@example.com"
        assert "Alice" in subj
        assert "Reaction Memes" in subj
        assert "https://app.memegpt.com/share/c/123" in html


@pytest.mark.asyncio
async def test_magic_link_and_alert_email_dispatch():
    """Verify magic link and alert emails build proper content."""
    with patch("app.services.email_service.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        res1 = await send_magic_link_email("carol@example.com", "https://memegpt.com/auth?token=123")
        assert res1 is True

        res2 = await send_account_alert_email("carol@example.com", "New Device Login", "Login from Tokyo")
        assert res2 is True
        assert mock_send.call_count == 2


# ── Transactional Email API Routes ───────────────────────────────────────────

def test_email_api_routes():
    """Verify all transactional email API routes respond properly."""
    with patch("app.api.v1.email.send_welcome_email", new_callable=AsyncMock) as mock_welcome:
        mock_welcome.return_value = True
        r = client.post("/api/v1/email/welcome", json={"email": "test@example.com", "username": "Tester"})
        assert r.status_code == 200
        assert r.json()["success"] is True

    with patch("app.api.v1.email.send_collection_share_email", new_callable=AsyncMock) as mock_share:
        mock_share.return_value = True
        r = client.post("/api/v1/email/share-collection", json={
            "to_email": "friend@example.com",
            "sender_name": "Dev",
            "collection_name": "Favorites",
            "share_url": "https://memegpt.com/share/c/favs",
        })
        assert r.status_code == 200
        assert r.json()["success"] is True

    with patch("app.api.v1.email.send_magic_link_email", new_callable=AsyncMock) as mock_magic:
        mock_magic.return_value = True
        r = client.post("/api/v1/email/magic-link", json={
            "to_email": "user@example.com",
            "magic_link": "https://memegpt.com/magic?tok=abc",
        })
        assert r.status_code == 200
        assert r.json()["success"] is True

    with patch("app.api.v1.email.send_account_alert_email", new_callable=AsyncMock) as mock_alert:
        mock_alert.return_value = True
        r = client.post("/api/v1/email/alert", json={
            "to_email": "user@example.com",
            "alert_title": "Password Changed",
            "alert_message": "Your password was recently changed.",
        })
        assert r.status_code == 200
        assert r.json()["success"] is True

    with patch("app.api.v1.email.send_email", new_callable=AsyncMock) as mock_generic:
        mock_generic.return_value = True
        r = client.post("/api/v1/email/test", json={
            "to_email": "user@example.com",
            "subject": "Ping",
            "html_content": "<p>Pong</p>",
        })
        assert r.status_code == 200
        assert r.json()["success"] is True
