from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal, Meme

init_db()
client = TestClient(app)


def test_health_controller_diagnostics():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert "uptime_seconds" in data
    assert "models" in data
    assert "text_model" in data["models"]
    assert "services" in data
    assert data["services"]["database"] == "connected"


def test_meme_detail_and_download_controller():
    # 1. Fetch any meme from list
    list_res = client.get("/api/v1/memes?limit=1")
    items = list_res.json().get("items", [])
    if items:
        meme_id = items[0]["id"]

        # 2. Get meme detail
        detail_res = client.get(f"/api/v1/memes/{meme_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == meme_id

        # 3. Download redirect
        dl_res = client.get(f"/api/v1/memes/{meme_id}/download?format=gif", follow_redirects=False)
        assert dl_res.status_code == 301
        assert "location" in dl_res.headers

        # 4. Invalid format validation (returns 422)
        invalid_dl = client.get(f"/api/v1/memes/{meme_id}/download?format=invalid_fmt", follow_redirects=False)
        assert invalid_dl.status_code == 422


def test_search_controller_response_contract():
    res = client.post(
        "/api/v1/search",
        json={"query": "when code works on the first try", "format_preference": "gif", "limit": 5}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "query_id" in data
    assert "results" in data
    assert "response_time_ms" in data
