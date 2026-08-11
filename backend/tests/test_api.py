from fastapi.testclient import TestClient
from app.main import app

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
