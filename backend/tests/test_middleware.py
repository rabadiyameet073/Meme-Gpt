from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_cors_preflight_options():
    res = client.options(
        "/api/v1/search",
        headers={
            "Origin": "https://memegpt.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,X-API-Key",
        }
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "https://memegpt.com"
    assert "access-control-max-age" in res.headers


def test_security_headers_present():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert res.headers.get("x-frame-options") == "DENY"
    assert res.headers.get("x-xss-protection") == "1; mode=block"
    assert res.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


def test_request_timing_and_rate_limit_headers():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert "x-response-time" in res.headers
    assert "x-ratelimit-limit" in res.headers
    assert "x-ratelimit-remaining" in res.headers
