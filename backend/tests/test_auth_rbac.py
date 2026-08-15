from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)



def test_anonymous_access_headers():
    response = client.get("/api/v1/trending")
    assert response.status_code == 200
    assert response.headers.get("X-RateLimit-Limit") == "60"


def test_api_key_creation_and_usage():
    # 1. Create a free developer API key
    create_res = client.post(
        "/api/v1/auth/api-keys",
        json={"name": "Test Suite App", "tier": "free"}
    )
    assert create_res.status_code == 200
    key_data = create_res.json()
    assert "raw_key" in key_data
    raw_key = key_data["raw_key"]
    key_id = key_data["id"]
    assert raw_key.startswith("pk_live_")
    assert key_data["rate_limit"] == 120

    # 2. Use the new API key on an endpoint
    usage_res = client.get("/api/v1/auth/tier", headers={"X-API-Key": raw_key})
    assert usage_res.status_code == 200
    tier_info = usage_res.json()
    assert tier_info["tier"] == "free"
    assert tier_info["rate_limit"] == 120

    # 3. List API keys and verify masking
    list_res = client.get("/api/v1/auth/api-keys")
    assert list_res.status_code == 200
    keys = list_res.json()
    matched = next((k for k in keys if k["id"] == key_id), None)
    assert matched is not None
    assert "..." in matched["prefix"]
    assert "raw_key" not in matched

    # 4. Revoke the API key
    del_res = client.delete(f"/api/v1/auth/api-keys/{key_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 5. Using revoked key now returns 403 Forbidden
    revoked_res = client.get("/api/v1/auth/tier", headers={"X-API-Key": raw_key})
    assert revoked_res.status_code == 403


def test_admin_rbac_protection():
    # 1. Anonymous attempt to delete a meme -> 403
    anon_del = client.delete("/api/v1/admin/memes/test-id")
    assert anon_del.status_code == 403

    # 2. Free developer key attempt to delete a meme -> 403
    free_del = client.delete(
        "/api/v1/admin/memes/test-id",
        headers={"X-API-Key": "memegpt_dev_demo_key"}
    )
    assert free_del.status_code == 403

    # 3. Admin key has permission -> 404 (because ID doesn't exist, but passes RBAC)
    admin_del = client.delete(
        "/api/v1/admin/memes/non-existent-id",
        headers={"X-API-Key": "memegpt_admin_secret_key"}
    )
    assert admin_del.status_code == 404  # Not 403
