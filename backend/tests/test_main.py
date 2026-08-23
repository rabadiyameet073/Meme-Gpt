"""API Endpoint Integration Tests from 10_Testing/Backend_Tests.md."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_valid():
    response = client.post("/api/v1/search", json={"query": "Monday vibes"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 5


def test_search_empty_query():
    response = client.post("/api/v1/search", json={"query": ""})
    assert response.status_code == 422


def test_search_max_length():
    response = client.post("/api/v1/search", json={"query": "a" * 2001})
    assert response.status_code == 422


def test_meme_not_found():
    response = client.get("/api/v1/memes/nonexistent_meme_id_12345")
    assert response.status_code == 404
