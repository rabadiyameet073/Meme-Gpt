"""Tests for Rate Limiting Security from 11_Security/Rate_Limiting_Security.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.core.rate_limit import rate_limiter
from app.services.rate_limiting_security_service import (
    get_rate_limiting_architecture,
    get_rate_limit_policies,
    get_ddos_mitigation_layers,
    get_rate_limiting_best_practices,
    check_rate_limit_policy,
    resolve_policy_for_path,
    evaluate_rate_limiting_security_health,
)

client = TestClient(app)


def test_rate_limiting_architecture_spec():
    arch = get_rate_limiting_architecture()
    assert "Token Bucket" in arch["title"]
    assert len(arch["flow"]) == 7
    assert any("429 Too Many Requests" in step for step in arch["flow"])


def test_per_endpoint_rate_limit_policies():
    res = get_rate_limit_policies()
    assert res["total_policies"] == 5
    policies = {p["endpoint"]: p for p in res["policies"]}

    # POST /search
    assert policies["POST /search"]["limit"] == 30
    assert policies["POST /search"]["key_pattern"] == "rl:search:{ip}"

    # GET /trending
    assert policies["GET /trending"]["limit"] == 60
    assert policies["GET /trending"]["key_pattern"] == "rl:general:{ip}"

    # GET /memes/{slug}
    assert policies["GET /memes/{slug}"]["limit"] == 60

    # POST /feedback
    assert policies["POST /feedback"]["limit"] == 120
    assert policies["POST /feedback"]["key_pattern"] == "rl:feedback:{ip}"

    # GET /health (exempt)
    assert policies["GET /health"]["exempt"] is True
    assert policies["GET /health"]["limit"] is None


def test_ddos_mitigation_layers():
    res = get_ddos_mitigation_layers()
    assert res["total_layers"] == 4
    layers = [l["layer"] for l in res["layers"]]
    assert layers == [1, 2, 3, 4]
    providers = [l["provider"] for l in res["layers"]]
    assert "Cloudflare (automatic)" in providers


def test_rate_limiting_best_practices():
    res = get_rate_limiting_best_practices()
    assert res["total_practices"] == 6
    titles = [p["title"] for p in res["practices"]]
    assert "Rate limit by IP, not by cookie" in titles
    assert "Use Redis sorted sets" in titles
    assert "Include rate limit headers on every response" in titles
    assert "Different limits per endpoint" in titles
    assert "Exempt health checks" in titles
    assert "Log rate limit violations" in titles


def test_policy_resolution_and_health_exemption():
    # Search
    p_search = resolve_policy_for_path("/api/v1/search")
    assert p_search["limit"] == 30

    # Feedback
    p_feed = resolve_policy_for_path("/api/v1/feedback")
    assert p_feed["limit"] == 120

    # Health
    p_health = resolve_policy_for_path("/api/v1/health")
    assert p_health["exempt"] is True


def test_rate_limit_quota_and_blocking_behavior():
    test_ip = "192.168.1.99"
    rate_limiter.reset(f"rl:search:{test_ip}")

    # Exhaust quota of limit=3
    res1 = check_rate_limit_policy("/api/v1/search", test_ip, custom_limit=3)
    assert res1["allowed"] is True
    assert res1["remaining"] == 2

    res2 = check_rate_limit_policy("/api/v1/search", test_ip, custom_limit=3)
    assert res2["allowed"] is True
    assert res2["remaining"] == 1

    res3 = check_rate_limit_policy("/api/v1/search", test_ip, custom_limit=3)
    assert res3["allowed"] is True
    assert res3["remaining"] == 0

    # 4th request must be blocked
    res4 = check_rate_limit_policy("/api/v1/search", test_ip, custom_limit=3)
    assert res4["allowed"] is False
    assert res4["remaining"] == 0
    assert res4["retry_after"] > 0
    rate_limiter.reset(f"rl:search:{test_ip}")


def test_rate_limit_headers_on_responses():
    rate_limiter.reset()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert response.headers.get("X-RateLimit-Window") == "60"


def test_rate_limiting_api_endpoints():
    res_arch = client.get("/api/v1/rate-limiting/architecture")
    assert res_arch.status_code == 200
    assert "Token Bucket" in res_arch.json()["title"]

    res_pol = client.get("/api/v1/rate-limiting/policies")
    assert res_pol.status_code == 200
    assert res_pol.json()["total_policies"] == 5

    res_ddos = client.get("/api/v1/rate-limiting/ddos-layers")
    assert res_ddos.status_code == 200
    assert res_ddos.json()["total_layers"] == 4

    res_prac = client.get("/api/v1/rate-limiting/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 6

    res_chk = client.post("/api/v1/rate-limiting/check", json={
        "endpoint_path": "/api/v1/search",
        "client_ip": "10.0.0.1",
        "custom_limit": 50,
    })
    assert res_chk.status_code == 200
    assert res_chk.json()["allowed"] is True

    res_health = client.get("/api/v1/rate-limiting/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "COMPLIANT"
