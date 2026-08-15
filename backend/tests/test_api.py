from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "memeCount" in data

def test_categories_endpoint():
    response = client.get("/api/categories")
    assert response.status_code == 200
    cats = response.json()
    assert isinstance(cats, list)
    assert "coding" in cats

def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "totalMemes" in data
    assert "totalSearches" in data

def test_analyze_endpoint():
    response = client.post("/api/analyze", json={"query": "Production down at 3 AM because of my code"})
    assert response.status_code == 200
    data = response.json()
    assert "primary" in data
    assert "topFive" in data
    assert data["primary"]["name"] != ""

def test_memes_list_endpoint():
    response = client.get("/api/memes?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_export_endpoint():
    req_body = {
        "query": "Test error situation",
        "format": "txt",
        "result": {
            "primary": {
                "name": "Test Meme",
                "category": "coding",
                "dialogue": "Test Dialogue",
                "confidence": 0.95,
                "explanation": "Test explanation"
            },
            "topFive": [],
            "alternatives": []
        }
    }
    response = client.post("/api/export", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "memegpt-result.txt"
    assert "Test Dialogue" in data["content"]


def test_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v1_search():
    response = client.post(
        "/api/v1/search",
        json={"query": "when your code works first try", "format_preference": "gif", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query_id" in data
    assert "response_time_ms" in data


def test_v1_trending():
    response = client.get("/api/v1/trending")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_v1_feedback():
    # First get a meme ID
    memes_res = client.get("/api/v1/memes?limit=1")
    items = memes_res.json().get("items", [])
    if items:
        meme_id = items[0]["id"]
        response = client.post(
            "/api/v1/feedback",
            json={"meme_id": meme_id, "signal": "copy", "format": "gif"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "recorded"


def test_auth_anonymous_and_api_key():
    import asyncio
    from app.core.auth import verify_api_key
    from fastapi import HTTPException

    # Anonymous tier
    anon = asyncio.run(verify_api_key(None))
    assert anon.tier == "anonymous"
    assert anon.rate_limit == 60

    # Pro developer tier with valid demo key
    dev = asyncio.run(verify_api_key("memegpt_pro_demo_key"))
    assert dev.tier == "pro"
    assert dev.rate_limit == 300

    # Invalid key raises 401
    try:
        asyncio.run(verify_api_key("invalid_random_key_12345"))
        assert False, "Should raise 401"
    except HTTPException as e:
        assert e.status_code == 401



