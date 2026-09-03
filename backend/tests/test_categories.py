"""
Tests for Categories and Stats endpoints from 14_Testing_Suite.md.
"""

def test_get_categories(client, sample_meme):
    """GET /api/categories returns list."""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0


def test_get_stats(client):
    """GET /api/stats returns count dict."""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_memes" in data
    assert isinstance(data["total_memes"], int)
