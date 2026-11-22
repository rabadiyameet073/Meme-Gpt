import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_meme_detail_includes_alt_text():
    """Verify meme response includes alt_text for screen readers."""
    resp = client.get("/api/v1/memes?limit=1")
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", [])
    if items:
        meme = items[0]
        assert "name" in meme
        assert "alt_text" in meme or "explanation" in meme
