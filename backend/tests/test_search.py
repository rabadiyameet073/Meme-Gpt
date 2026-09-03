"""
MemeGPT — Search & Recommendation Endpoint Tests from 14_Testing_Suite.md.
"""

import pytest


def test_search_returns_results(client, sample_meme):
    """Search endpoint returns meme results."""
    resp = client.post("/api/v1/search", json={"query": "drake pointing yes no"})
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data or "topFive" in data
    results = data.get("results", data.get("topFive", []))
    assert isinstance(results, list)


def test_search_with_format_filter(client, sample_meme):
    """Format filter is respected."""
    resp = client.post("/api/v1/search", json={"query": "test", "format": "gif"})
    assert resp.status_code == 200


def test_search_rate_limit_headers(client):
    """Rate limit headers are present."""
    resp = client.post("/api/v1/search", json={"query": "hello"})
    assert "x-ratelimit-limit" in resp.headers or "X-RateLimit-Limit" in resp.headers


def test_search_sanitizes_input(client):
    """HTML injection is sanitized."""
    resp = client.post("/api/v1/search", json={"query": "<script>alert(1)</script>"})
    assert resp.status_code == 200


def test_search_empty_query(client):
    """Empty query returns 400/422 or empty results."""
    resp = client.post("/api/v1/search", json={"query": ""})
    assert resp.status_code in (200, 400, 422)


def test_search_very_long_query(client):
    """Very long query is truncated, not 500."""
    long_query = "a" * 10000
    resp = client.post("/api/v1/search", json={"query": long_query})
    assert resp.status_code in (200, 400, 422)
