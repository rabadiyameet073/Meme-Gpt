"""
MemeGPT — Integration Flow Tests.
"""

import pytest


def test_favorites_flow(client):
    """Test saving and retrieving favorites for a session."""
    session_id = "test-session-integration-123"

    # 1. Initially empty
    resp = client.get(f"/api/favorites?sessionId={session_id}")
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. Toggle favorite
    resp = client.post("/api/favorites/toggle", json={
        "memeId": "test-drake-001",
        "sessionId": session_id,
    })
    assert resp.status_code == 200
    assert resp.json().get("isFavorite") is True

    # 3. Retrieve favorites
    resp = client.get(f"/api/favorites?sessionId={session_id}")
    assert resp.status_code == 200
    favs = resp.json()
    assert len(favs) == 1
    assert favs[0]["id"] == "test-drake-001"

    # 4. Toggle again to unsave
    resp = client.post("/api/favorites/toggle", json={
        "memeId": "test-drake-001",
        "sessionId": session_id,
    })
    assert resp.status_code == 200
    assert resp.json().get("isFavorite") is False


def test_admin_meme_lifecycle(client):
    """Test creating and deleting a meme via admin API."""
    headers = {"X-API-Key": "memegpt_admin_secret_key"}

    # Create meme
    new_meme_payload = {
        "name": "Integration Test Meme",
        "slug": "integration-test-meme",
        "category": "testing",
        "emotions": ["confidence"],
        "dialogue": "When tests pass on first try",
        "explanation": "Pure satisfaction.",
        "keywords": ["test", "pass", "green"],
    }
    resp = client.post("/api/v1/admin/memes", json=new_meme_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    meme_id = data.get("id") or data.get("meme", {}).get("id")
    assert meme_id is not None

    # Delete meme
    del_resp = client.delete(f"/api/v1/admin/memes/{meme_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json().get("success") is True
