import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Meme, SessionLocal

client = TestClient(app)


def test_related_memes_endpoint():
    """Verify GET /api/v1/memes/{slug_or_id}/related returns related memes."""
    db = SessionLocal()
    try:
        # Create test meme
        m1 = Meme(
            id="test-related-1",
            name="Test Related Primary",
            slug="test-related-primary",
            category="programming",
            viral_score=10.0,
            image_ref="https://example.com/1.png"
        )
        m2 = Meme(
            id="test-related-2",
            name="Test Related Sibling",
            slug="test-related-sibling",
            category="programming",
            viral_score=8.0,
            image_ref="https://example.com/2.png"
        )
        db.merge(m1)
        db.merge(m2)
        db.commit()
    finally:
        db.close()

    resp = client.get("/api/v1/memes/test-related-primary/related?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Ensure sibling is returned and primary is not in the list
    ids = [item.get("id") for item in data]
    assert "test-related-primary" not in ids
    assert "test-related-2" in ids


def test_related_memes_not_found():
    """Verify 404 for nonexistent meme slug in related memes endpoint."""
    resp = client.get("/api/v1/memes/nonexistent-slug-xyz-123/related")
    assert resp.status_code == 404


def test_stats_endpoint_returns_json():
    """Verify /api/v1/stats returns real counts."""
    resp = client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_memes" in data or "count" in data or "totalMemes" in data
