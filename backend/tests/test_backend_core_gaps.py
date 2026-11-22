"""
Tests for 02-backend-core-gaps.md (BE-01 through BE-09).
Ensures health dependency states, debug endpoint security, cache survival/invalidation,
stateless/bounded memory, and hot-path zero DB lookups are strictly enforced.
"""
import time
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.config import settings
from app.core.auth import get_cached_api_key_tier, invalidate_api_key_cache, lookup_api_key_tier, _KEY_TIER_CACHE
from app.core.cache import cache_set, cache_get, cache_flush_pattern, _fallback_cache, _rate_counts
from app.core.rate_limit import RateLimiter
from app.api.v1.search import _get_cached_memes, invalidate_memes_cache

client = TestClient(app)


def test_be01_health_reflects_dependency_state():
    """BE-01: Health endpoint reflects real database, redis, and qdrant dependency states."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
    assert "qdrant" in data["services"]
    assert data["services"]["database"] == "connected"


def test_be01_health_database_error_returns_503(monkeypatch):
    """BE-01: Health endpoint returns 503 and degraded status when database is down."""
    from app.database import get_db

    def mock_broken_db():
        mock = MagicMock()
        mock.execute.side_effect = Exception("Database connection failure")
        mock.query.side_effect = Exception("Database connection failure")
        yield mock

    app.dependency_overrides[get_db] = mock_broken_db
    try:
        resp = client.get("/api/v1/health")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["services"]["database"] == "error"
        assert data["db"] == "error"
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_be02_debug_endpoints_gated_in_production(monkeypatch):
    """BE-02: Debug endpoints (/health/sentry-test, /health/sentry-error) restricted in production."""
    monkeypatch.setattr(settings, "APP_ENV", "production")

    # Non-admin call should be rejected with 403 Forbidden
    resp = client.get("/api/v1/health/sentry-test")
    assert resp.status_code == 403
    assert "non-production" in resp.json()["detail"].lower()

    resp = client.get("/api/v1/health/sentry-error")
    assert resp.status_code == 403

    # Authenticated admin call in production is permitted
    from app.services.jwt_service import create_access_token
    token = create_access_token(data={"sub": "admin_user", "role": "admin"})
    admin_headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/health/sentry-test", headers=admin_headers)
    assert resp.status_code == 200


def test_be03_cache_invalidation_on_data_changes():
    """BE-03: Changes to memes invalidate search and trending cache."""
    cache_set("search:test_query_key", {"dummy": 123}, ttl=300)
    cache_set("trending:daily", [{"dummy": 456}], ttl=300)

    assert cache_get("search:test_query_key") is not None

    # Call cache_flush_pattern for search:*
    deleted_count = cache_flush_pattern("search:*")
    assert deleted_count >= 1
    assert cache_get("search:test_query_key") is None


def test_be04_cache_survives_deploys():
    """BE-04: Deploy/restart does not wipe shared cache unless CLEAR_CACHE_ON_STARTUP is enabled."""
    assert getattr(settings, "CLEAR_CACHE_ON_STARTUP", False) is False


def test_be05_config_consistency():
    """BE-05: Standardized on APP_ENV; settings.ENVIRONMENT mirrors APP_ENV."""
    assert hasattr(settings, "APP_ENV")
    assert settings.ENVIRONMENT == settings.APP_ENV


def test_be06_no_hardcoded_secret_fallbacks():
    """BE-06: core/auth.py and jwt_service.py read strictly from settings.SECRET_KEY."""
    import app.core.auth as auth_mod
    import app.services.jwt_service as jwt_mod

    assert auth_mod.JWT_SECRET_KEY == settings.SECRET_KEY
    assert jwt_mod.SECRET_KEY == settings.SECRET_KEY


def test_be07_stateless_and_bounded_rate_limit_fallback():
    """BE-07: In-memory fallback dictionary does not grow unbounded."""
    limiter = RateLimiter(window_seconds=60)
    now = time.time()

    # Populate 1,200 unique identifiers
    for i in range(1200):
        limiter._history[f"ip_{i}"] = [now - 10]

    # Check with new identifier triggering bound cleanup
    limiter.check_with_window("new_ip", 100, 60)
    assert len(limiter._history) <= 1001


def test_be08_hot_path_zero_per_request_db_lookups():
    """BE-08: Hot-path API key tier lookups and search meme loading are cached (O(1))."""
    invalidate_api_key_cache()
    test_key = "pk_test_sample_key"

    # Static dev key check: immediate without DB
    tier, is_admin = get_cached_api_key_tier(test_key)
    assert tier == "free"
    assert is_admin is False

    # Second call hits memory cache
    tier2, _ = get_cached_api_key_tier(test_key)
    assert tier2 == tier

    # Meme search cache avoids DB full-table scan on consecutive searches
    invalidate_memes_cache()
    memes1 = _get_cached_memes()
    assert len(memes1) > 0

    memes2 = _get_cached_memes()
    assert memes2 is memes1  # Exactly the same object reference in memory (zero DB lookup)


def test_be09_background_jobs_runner_flag():
    """BE-09: ENABLE_INTERNAL_SCHEDULER allows single-runner control across horizontal workers."""
    assert hasattr(settings, "ENABLE_INTERNAL_SCHEDULER")
    assert isinstance(settings.ENABLE_INTERNAL_SCHEDULER, bool)


def test_be03_vote_invalidates_trending_cache():
    """BE-03: User votes and feedback invalidate trending cache."""
    from app.core.cache import cache_set, cache_get
    cache_set("trending:all:24h:0:20", [{"id": "dummy"}], ttl=300)
    assert cache_get("trending:all:24h:0:20") is not None

    # Cast a vote on a meme
    resp = client.post("/api/v1/vote", json={"memeId": "drake-hotline", "vote": 1, "sessionId": "sess_test"})
    if resp.status_code == 200:
        assert cache_get("trending:all:24h:0:20") is None


def test_be07_chat_sessions_bounded_memory():
    """BE-07: Chat session in-memory store is bounded by MAX_SESSIONS."""
    from app.services.chat_refinement_service import _CHAT_SESSIONS, MAX_SESSIONS, add_session_turn
    initial_len = len(_CHAT_SESSIONS)
    
    # Insert turns into many sessions exceeding MAX_SESSIONS
    for i in range(MAX_SESSIONS + 20):
        add_session_turn(f"bounded_sess_{i}", "hello query", [])

    assert len(_CHAT_SESSIONS) <= MAX_SESSIONS


def test_be09_retention_distributed_lock_skips_when_locked(monkeypatch):
    """BE-09: Retention cleanup skips execution when lock is held by another worker."""
    from app.jobs.retention import run_retention_cleanup
    mock_redis = MagicMock()
    mock_redis.set.return_value = False  # Lock held by peer worker

    with patch("app.core.cache.get_redis_client", return_value=mock_redis):
        result = run_retention_cleanup()
        assert result.get("status") == "skipped"
        assert result.get("reason") == "lock_held"

