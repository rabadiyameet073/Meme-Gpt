"""Tests for API Overview from 07_APIs/API_Overview.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.api_service import (
    get_api_environments,
    get_api_overview_catalog,
    format_api_success_response,
    format_api_error_response,
    get_http_status_codes_catalog,
    get_endpoint_rate_limits,
)

client = TestClient(app)


def test_get_api_environments():
    envs = get_api_environments()
    assert envs["production"] == "https://api.memegpt.com"
    assert envs["staging"] == "https://api-staging.memegpt.com"
    assert envs["development"] == "http://localhost:8000"


def test_get_api_overview_catalog():
    catalog = get_api_overview_catalog()
    assert catalog["version"] == "v1"
    assert catalog["prefix"] == "/api/v1"

    endpoints = {ep["path"]: ep for ep in catalog["endpoints"]}
    assert "/api/v1/search" in endpoints
    assert "/api/v1/memes/{slug}" in endpoints
    assert "/api/v1/memes/{slug}/download" in endpoints
    assert "/api/v1/trending" in endpoints
    assert "/api/v1/feedback" in endpoints
    assert "/health" in endpoints

    assert endpoints["/api/v1/search"]["rate_limit"] == "30/min"
    assert endpoints["/api/v1/memes/{slug}"]["rate_limit"] == "60/min"
    assert endpoints["/api/v1/feedback"]["rate_limit"] == "120/min"


def test_format_api_responses():
    success = format_api_success_response({"meme": "drake"})
    assert success["success"] is True
    assert success["data"]["meme"] == "drake"

    error = format_api_error_response("meme_not_found", "Meme not found")
    assert error["success"] is False
    assert error["error"] == "meme_not_found"
    assert error["message"] == "Meme not found"


def test_get_http_status_codes_catalog():
    codes = get_http_status_codes_catalog()
    code_map = {c["status"]: c for c in codes}
    assert 200 in code_map
    assert 301 in code_map
    assert 400 in code_map
    assert 404 in code_map
    assert 422 in code_map
    assert 429 in code_map
    assert 500 in code_map
    assert 503 in code_map


def test_response_headers_on_live_request():
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers

    assert "X-Response-Time" in headers
    assert headers["X-Response-Time"].endswith("ms")
    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers
    assert "X-RateLimit-Reset" in headers
