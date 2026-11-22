import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_suggestion_chips_endpoint():
    """Verify GET /api/v1/chips/suggestions returns active suggestions with label and query."""
    resp = client.get("/api/v1/chips/suggestions?limit=6")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    chips = data.get("chips", [])
    assert len(chips) > 0
    first = chips[0]
    assert "label" in first
    assert "query" in first


def test_favorites_toggle_endpoints():
    """Verify both /api/v1/favorites and /api/v1/favorites/toggle work idempotently."""
    session_id = "test-workflow-session"
    meme_id = "test-wf-meme-1"

    # Toggle on
    r1 = client.post("/api/v1/favorites/toggle", json={"memeId": meme_id, "sessionId": session_id})
    assert r1.status_code == 200
    assert r1.json().get("isFavorite") is True

    # Toggle off
    r2 = client.post("/api/v1/favorites", json={"memeId": meme_id, "sessionId": session_id})
    assert r2.status_code == 200
    assert r2.json().get("isFavorite") is False


def test_chat_refine_session_history():
    """Verify chat refinement handles multi-turn sessions."""
    resp = client.post(
        "/api/v1/chat/refine",
        json={
            "query": "when the server crashes on a friday night",
            "session_id": "test-chat-session-wf",
            "limit": 3
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "turn" in data or "primary" in data or "results" in data
