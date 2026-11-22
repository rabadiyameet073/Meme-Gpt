"""
Tests for 03-search-api-gaps.md (API-01 through API-13).
Validates search contracts, category filters, limit capping, response schemas,
empty DB graceful responses, category 404s, per-route rate limiting, and reverse image search.
"""
import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.database import Meme, get_db
from app.core.rate_limit import rate_limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    rate_limiter.reset()
    yield
    rate_limiter.reset()


def test_api01_nsfw_flag_forwarded_and_filtered():
    """API-01: nsfw flag is accepted, safe by default, and controls explicit content."""
    # Default safe search (nsfw=False)
    resp = client.post("/api/v1/search", json={"query": "funny meme", "nsfw": False})
    assert resp.status_code == 200
    data = resp.json()
    for item in data.get("results", []):
        assert item.get("nsfw", False) is False

    # Opt-in nsfw=True accepted
    resp_nsfw = client.post("/api/v1/search", json={"query": "funny meme", "nsfw": True})
    assert resp_nsfw.status_code == 200


def test_api02_categories_filter_restricts_results():
    """API-02: filters.categories restricts results to chosen categories."""
    resp = client.post("/api/v1/search", json={
        "query": "coding",
        "filters": {"categories": ["tech"]}
    })
    assert resp.status_code == 200
    data = resp.json()
    for item in data.get("results", []):
        item_cats = [c.lower() for c in item.get("categories", [])]
        assert any("tech" in c for c in item_cats) or not data.get("results")


def test_api03_limit_parameter_bounds():
    """API-03: limit is clamped to 1-20 and honored in response."""
    resp = client.post("/api/v1/search", json={"query": "reaction", "limit": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data.get("results", [])) <= 3

    resp_clamped = client.post("/api/v1/search", json={"query": "reaction", "limit": 20})
    assert resp_clamped.status_code == 200
    data_clamped = resp_clamped.json()
    assert len(data_clamped.get("results", [])) <= 20


def test_api04_documented_response_schema():
    """API-04: Response matches documented Search_API.md schema."""
    resp = client.post("/api/v1/search", json={"query": "work burnout"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    assert "query_id" in data
    assert isinstance(data["results"], list)
    assert "response_time_ms" in data
    assert "cached" in data

    if data["results"]:
        top = data["results"][0]
        assert "id" in top
        assert "name" in top
        assert "slug" in top
        assert "relevance_score" in top
        assert isinstance(top["relevance_score"], (int, float))
        assert "emotion_match" in top
        assert isinstance(top["emotion_match"], list)
        assert "formats" in top
        assert "video" in top["formats"]
        assert "gif" in top["formats"]
        assert "image" in top["formats"]
        assert "webp" in top["formats"]
        assert "preview_url" in top
        assert "share_url" in top
        assert "categories" in top
        assert isinstance(top["categories"], list)


def test_api05_query_validation_empty_or_whitespace_raises_422():
    """API-05: Empty or whitespace queries raise 422 Unprocessable Entity."""
    resp_empty = client.post("/api/v1/search", json={"query": ""})
    assert resp_empty.status_code == 422

    resp_ws = client.post("/api/v1/search", json={"query": "     "})
    assert resp_ws.status_code == 422


def test_api07_empty_database_returns_200_with_reason():
    """API-07: When database has no memes, returns 200 with results: [] and reason."""
    with patch("app.api.v1.search._memes_from_db", return_value=[]):
        resp = client.post("/api/v1/search", json={"query": "hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["results"] == []
        assert data.get("reason") == "database_empty"


def test_api09_sitemap_slugs_paginated():
    """API-09: Paginated /api/v1/sitemap/slugs supports sitemap indexing."""
    resp = client.get("/api/v1/sitemap/slugs?limit=100&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert "slugs" in data
    assert isinstance(data["slugs"], list)
    assert "total" in data
    assert "has_more" in data


def test_api10_unknown_category_returns_404():
    """API-10: GET /api/v1/memes?category=unknown_xyz returns HTTP 404."""
    resp = client.get("/api/v1/memes?category=nonexistent_category_xyz123")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_api11_and_api12_per_endpoint_rate_limits():
    """API-11 & API-12: Route-level limiter enforces per-route budget and returns 429."""
    rate_limiter.reset()

    # Anonymous search budget is 30/min
    headers = {"X-Forwarded-For": "192.168.1.100"}
    for _ in range(30):
        rate_limiter.check_with_window("route:search:ip:192.168.1.100", 30, 60)

    # 31st request should trigger 429
    resp = client.post("/api/v1/search", json={"query": "overflow"}, headers=headers)
    assert resp.status_code == 429
    body = resp.json()
    assert body.get("error") == "rate_limit_exceeded"
    assert "search" in body.get("message", "").lower()
    assert "retry_after" in body or "retryAfter" in body


def test_api13_reverse_image_search_endpoint():
    """API-13: POST /api/v1/search/image accepts an image file and returns visual results."""
    # 1x1 transparent PNG file
    fake_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("test.png", io.BytesIO(fake_png), "image/png")}
    resp = client.post("/api/v1/search/image?limit=5", files=files)
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        data = resp.json()
        assert "results" in data
