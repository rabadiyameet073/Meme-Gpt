from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_endpoint():
    response = client.post("/api/v1/search", json={"query": "monday morning coffee"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
