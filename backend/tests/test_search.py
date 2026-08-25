"""
MemeGPT — Search & Recommendation Endpoint Tests.
"""

import pytest


def test_health_endpoint(client):
    """Test health check returns status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") in ("ok", "healthy") or data.get("success") is True


def test_categories_endpoint(client):
    """Test /api/categories returns a list of category strings."""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    cats = resp.json()
    assert isinstance(cats, list)
    assert len(cats) > 0


def test_stats_endpoint(client):
    """Test /api/stats returns total memes count."""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_memes" in stats or "totalMemes" in stats


def test_search_endpoint_returns_results(client):
    """Test /api/v1/search returns recommended memes."""
    payload = {
        "query": "when everything is on fire and code is broken",
        "format_preference": "image",
        "limit": 5,
    }
    resp = client.post("/api/v1/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data or "topFive" in data
    assert "query_id" in data or "queryId" in data


def test_search_empty_query_rejected(client):
    """Test empty search query is rejected with 400."""
    resp = client.post("/api/v1/search", json={"query": ""})
    assert resp.status_code in (400, 422)


def test_search_latency_header(client):
    """Test response contains X-Response-Time header."""
    resp = client.post("/api/v1/search", json={"query": "happy celebration"})
    assert resp.status_code == 200
    assert "x-response-time" in resp.headers
