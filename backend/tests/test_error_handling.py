from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)


def test_400_bad_request_envelope():
    from app.core.rate_limit import rate_limiter
    rate_limiter.reset()
    # Whitespace-only query triggers 400 after sanitization
    res = client.post("/api/v1/search", json={"query": "   "}, headers={"X-API-Key": "memegpt_dev_demo_key"})
    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert data["error"] == "invalid_request"
    assert "message" in data



def test_404_not_found_envelope():
    res = client.get("/api/v1/memes/completely-nonexistent-meme-uuid", headers={"X-API-Key": "memegpt_dev_demo_key"})
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert data["error"] == "not_found"
    assert "message" in data


def test_422_validation_error_structured_details():
    from app.core.rate_limit import rate_limiter
    rate_limiter.reset()
    # Negative limit invalid format
    res = client.post("/api/v1/search", json={"query": "test query", "limit": -5}, headers={"X-API-Key": "memegpt_dev_demo_key"})
    assert res.status_code == 422
    data = res.json()
    assert data["success"] is False
    assert data["error"] == "validation_error"
    assert "details" in data
    assert isinstance(data["details"], list)
    assert len(data["details"]) > 0
    assert "field" in data["details"][0]
    assert "message" in data["details"][0]


def test_429_rate_limit_envelope():
    from app.core.errors import RateLimitExceededError
    from app.core.rate_limit import rate_limiter

    # Simulate rate limiter exceeded
    rate_limiter.reset()
    for _ in range(65):
        rate_limiter.check("test-ip-rate", limit=60)

    allowed, rem, retry_after = rate_limiter.check("test-ip-rate", limit=60)
    assert not allowed
    assert retry_after > 0


def test_graceful_degradation_when_ml_pipeline_falls_back():
    # Search with unusual text succeeds via fallback pipeline
    res = client.post("/api/v1/search", json={"query": "12345 !@#$%^&*() fallback query test", "limit": 3})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "results" in data
