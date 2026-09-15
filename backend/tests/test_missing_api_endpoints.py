import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Meme, User
from app.core.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    db = SessionLocal()
    # Find or create a test user
    user = db.query(User).filter(User.email == "test_guide12@memegpt.com").first()
    if not user:
        user = User(
            email="test_guide12@memegpt.com",
            name="Guide 12 Tester",
            username="guide12tester",
            preferred_format="gif",
            theme="dark",
            nsfw_enabled=False,
            favourite_categories=["tech", "work"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    db.close()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_meme():
    db = SessionLocal()
    meme = db.query(Meme).first()
    if not meme:
        meme = Meme(
            name="Guide 12 Test Meme",
            slug="guide-12-test-meme",
            categories=["tech"],
            emotions=["joy"],
            dialogue="It works on my machine",
            image_url="https://cdn.memegpt.com/memes/guide12.jpg",
            gif_url="https://cdn.memegpt.com/memes/guide12.gif",
            mp4_url="https://cdn.memegpt.com/memes/guide12.mp4",
        )
        db.add(meme)
        db.commit()
        db.refresh(meme)
    slug = meme.slug or "guide-12-test-meme"
    meme_id = meme.id
    db.close()
    return {"slug": slug, "id": meme_id}


# ─── 1. Download Redirect Tests ───────────────────────────────────────────────

def test_download_meme_redirect(sample_meme):
    slug = sample_meme["slug"]
    response = client.get(f"/api/v1/memes/{slug}/download?format=gif", follow_redirects=False)
    assert response.status_code in (301, 307)
    assert "location" in response.headers

def test_download_meme_invalid_format(sample_meme):
    slug = sample_meme["slug"]
    response = client.get(f"/api/v1/memes/{slug}/download?format=flv")
    assert response.status_code in (400, 422)

def test_download_meme_not_found():
    response = client.get("/api/v1/memes/non-existent-super-random-slug-9999/download")
    assert response.status_code == 404


# ─── 2. User Profile & Preferences Tests ──────────────────────────────────────

def test_get_user_profile(auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_guide12@memegpt.com"
    assert "preferred_format" in data
    assert "theme" in data

def test_update_user_preferences(auth_headers):
    payload = {
        "preferred_format": "mp4",
        "theme": "light",
        "nsfw_enabled": True,
        "favourite_categories": ["gaming"],
    }
    response = client.put("/api/v1/users/me/preferences", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_format"] == "mp4"
    assert data["theme"] == "light"
    assert data["nsfw_enabled"] is True
    assert "gaming" in data["favourite_categories"]

def test_update_user_profile(auth_headers):
    payload = {
        "name": "Updated Guide 12 Tester",
        "preferred_format": "webp",
    }
    response = client.put("/api/v1/users/me", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_format"] == "webp"


# ─── 3. Collection CRUD Tests ─────────────────────────────────────────────────

def test_collection_lifecycle(auth_headers, sample_meme):
    collection_name = "Sprint Memes"
    meme_id = sample_meme["id"]

    # 1. Create collection
    create_res = client.post(
        "/api/v1/collections",
        json={"name": collection_name, "meme_ids": [meme_id]},
        headers=auth_headers,
    )
    assert create_res.status_code in (200, 201)

    # 2. List collections
    list_res = client.get("/api/v1/collections", headers=auth_headers)
    assert list_res.status_code == 200
    collections = list_res.json()
    assert any(c["collection_name"] == collection_name for c in collections)

    # 3. Get collection contents
    get_res = client.get(f"/api/v1/collections/{collection_name}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["item_count"] >= 1

    # 4. Remove item from collection
    rem_res = client.delete(
        f"/api/v1/collections/{collection_name}/items/{meme_id}",
        headers=auth_headers,
    )
    assert rem_res.status_code == 200

    # 5. Delete entire collection
    del_res = client.delete(f"/api/v1/collections/{collection_name}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"


# ─── 4. Share Feature Tests ───────────────────────────────────────────────────

def test_create_share(sample_meme):
    slug = sample_meme["slug"]
    response = client.post(
        "/api/v1/share",
        json={"meme_id": slug, "query_id": "qid_123", "platform": "whatsapp"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "share_url" in data
    assert "og_metadata" in data


# ─── 5. Developer Portal Tests ────────────────────────────────────────────────

def test_developer_usage_public():
    response = client.get("/api/v1/developer/usage")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["api_version"] == "2.0.0"
    assert "rate_limits" in data
    assert len(data["endpoints_available"]) > 0

def test_developer_status():
    response = client.get("/api/v1/developer/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
