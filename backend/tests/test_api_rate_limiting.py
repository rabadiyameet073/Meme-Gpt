"""Tests for API Rate Limiting from 07_APIs/Rate_Limiting.md."""

import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.rate_limit import rate_limiter
from app.services.rate_limit_service import (
    get_rate_limit_tier,
    get_rate_limit_for_request,
    get_rate_limit_tiers_catalog,
    simulate_token_bucket,
    get_rate_limiting_best_practices,
)

client = TestClient(app)


def test_rate_limit_response_headers():
    rate_limiter.reset()
    response = client.get("/api/v1/trending")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert "X-RateLimit-Window" in response.headers
    assert response.headers["X-RateLimit-Window"] == "60"


def test_rate_limit_tier_resolution():
    # 1. Anonymous -> Free (30 search / 60 general)
    tier, limit_search, _ = get_rate_limit_for_request("/api/v1/search", None)
    assert tier == "free"
    assert limit_search == 30

    _, limit_general, _ = get_rate_limit_for_request("/api/v1/memes", None)
    assert limit_general == 60

    # 2. Developer -> (100 search / 300 general)
    tier_dev, dev_search, _ = get_rate_limit_for_request("/api/v1/search", "mgpt_live_abcdef1234567890abcdef1234567890")
    assert tier_dev == "developer"
    assert dev_search == 100

    _, dev_gen, _ = get_rate_limit_for_request("/api/v1/memes", "mgpt_live_abcdef1234567890abcdef1234567890")
    assert dev_gen == 300

    # 3. Pro / Admin -> (500 search / 1000 general)
    tier_pro, pro_search, _ = get_rate_limit_for_request("/api/v1/search", "mgpt_live_admin_key_9999999999999999")
    assert tier_pro == "pro"
    assert pro_search == 500


def test_rate_limit_429_enforcement_and_response_envelope():
    rate_limiter.reset()
    
    # Free general limit is 60. Simulate hitting the limit
    for _ in range(60):
        rate_limiter.check_with_window("ip:testclient", limit=60, window_seconds=60)

    # The 61st request should trigger 429
    response = client.get("/api/v1/memes")
    assert response.status_code == 429
    data = response.json()

    assert data["success"] is False
    assert data["error"] == "rate_limit_exceeded"
    assert "requests per minute allowed" in data["message"]
    assert "retry_after" in data
    assert data["limit"] == 60
    assert data["window"] == "60s"

    assert "Retry-After" in response.headers
    assert response.headers["X-RateLimit-Remaining"] == "0"
    assert "X-RateLimit-Reset" in response.headers
    assert response.headers["X-RateLimit-Window"] == "60"

    # Reset limiter after test
    rate_limiter.reset()


def test_rate_limit_service_catalogs_and_token_bucket():
    catalog = get_rate_limit_tiers_catalog()
    assert len(catalog) == 3
    tiers = {c["tier"] for c in catalog}
    assert "Free" in tiers
    assert "Developer" in tiers
    assert "Pro" in tiers

    practices = get_rate_limiting_best_practices()
    assert len(practices) == 5
    assert any("Retry-After" in p for p in practices)

    # Token bucket simulation
    now = time.time()
    ts_history = [now - 10, now - 5, now - 1]
    res_allow = simulate_token_bucket(ts_history, now, limit=5, window_seconds=60)
    assert res_allow["allowed"] is True
    assert res_allow["remaining"] == 1

    res_block = simulate_token_bucket(ts_history, now, limit=3, window_seconds=60)
    assert res_block["allowed"] is False
    assert res_block["remaining"] == 0
    assert res_block["retry_after"] > 0
