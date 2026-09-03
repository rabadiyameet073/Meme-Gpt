"""
Unit and integration tests for missing API routes from 07_Missing_API_Routes.md:
- /api/categories
- /api/stats
- /api/admin/memes
- /api/favorites & /api/favorites/toggle
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_categories_endpoint():
    # Test both /api/categories and /api/v1/categories
    resp1 = client.get("/api/categories")
    assert resp1.status_code == 200
    cats1 = resp1.json()
    assert isinstance(cats1, list)
    assert len(cats1) > 0
    assert "coding" in cats1 or "work" in cats1 or "general" in cats1

    resp2 = client.get("/api/v1/categories")
    assert resp2.status_code == 200
    assert resp2.json() == cats1


def test_get_stats_endpoint():
    # Test both /api/stats and /api/v1/stats
    resp1 = client.get("/api/stats")
    assert resp1.status_code == 200
    stats1 = resp1.json()
    assert "total_memes" in stats1
    assert "total_searches" in stats1
    assert "version" in stats1

    resp2 = client.get("/api/v1/stats")
    assert resp2.status_code == 200
    stats2 = resp2.json()
    assert stats2["total_memes"] == stats1["total_memes"]


def test_favorites_workflow():
    session_id = "test_session_xyz_999"
    meme_id = "meme_test_fav_01"

    # Initially empty or list
    resp_init = client.get(f"/api/favorites?sessionId={session_id}")
    assert resp_init.status_code == 200
    assert isinstance(resp_init.json(), list)

    # Toggle favorite ON
    resp_toggle_on = client.post(
        "/api/favorites/toggle",
        json={"memeId": meme_id, "sessionId": session_id},
    )
    assert resp_toggle_on.status_code == 200
    data_on = resp_toggle_on.json()
    assert data_on["isFavorite"] is True
    assert data_on["memeId"] == meme_id

    # Toggle favorite OFF
    resp_toggle_off = client.post(
        "/api/favorites/toggle",
        json={"memeId": meme_id, "sessionId": session_id},
    )
    assert resp_toggle_off.status_code == 200
    data_off = resp_toggle_off.json()
    assert data_off["isFavorite"] is False
    assert data_off["memeId"] == meme_id


def test_admin_memes_crud():
    unique_slug = "admin-test-meme-crud-123"
    admin_headers = {"X-API-Key": "memegpt_admin_secret_key"}

    # 1. Create Meme
    payload = {
        "name": "Admin Test Meme",
        "slug": unique_slug,
        "category": "testing",
        "categories": ["testing", "qa"],
        "emotions": ["joy"],
        "dialogue": "All tests green",
        "explanation": "When all tests pass on first try",
        "keywords": ["tests", "green", "qa"],
        "image_url": "https://cdn.memegpt.com/images/admin-test.jpg",
        "source": "admin_test",
        "nsfw": False,
    }

    create_resp = client.post("/api/v1/admin/memes", json=payload, headers=admin_headers)
    assert create_resp.status_code == 200
    created_data = create_resp.json()
    assert created_data["success"] is True
    created_meme = created_data["meme"]
    meme_id = created_meme["id"]

    # 2. List Memes
    list_resp = client.get("/api/v1/admin/memes?page=1&limit=10", headers=admin_headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert "total" in list_data
    assert "memes" in list_data
    assert any(m["id"] == meme_id or m["slug"] == unique_slug for m in list_data["memes"])

    # 3. Update Meme
    update_payload = {"dialogue": "Updated dialogue text"}
    update_resp = client.patch(f"/api/v1/admin/memes/{meme_id}", json=update_payload, headers=admin_headers)
    assert update_resp.status_code == 200
    updated_meme = update_resp.json()["meme"]
    assert updated_meme["dialogue"] == "Updated dialogue text"

    # 4. Delete Meme
    del_resp = client.delete(f"/api/v1/admin/memes/{meme_id}", headers=admin_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 5. Verify Deletion
    del_again_resp = client.delete(f"/api/v1/admin/memes/{meme_id}", headers=admin_headers)
    assert del_again_resp.status_code == 404

