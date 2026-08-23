"""Tests for API Security from 11_Security/API_Security.md."""

import os
from fastapi.testclient import TestClient
from app.main import app
from app.services.api_security_service import (
    get_security_layers,
    get_security_headers_spec,
    get_secret_management_matrix,
    get_cors_policy_spec,
    get_security_prelaunch_checklist,
    evaluate_security_compliance,
    mask_api_key,
)

client = TestClient(app)


def test_security_layers_pipeline():
    res = get_security_layers()
    assert res["total_layers"] == 6
    names = [layer["name"] for layer in res["layers"]]
    assert names == [
        "HTTPS Enforcement",
        "CORS Validation",
        "Rate Limiting",
        "Input Validation",
        "Authentication & RBAC",
        "Route Handler & Safe Execution",
    ]


def test_security_headers_spec_and_response_headers():
    spec = get_security_headers_spec()
    assert spec["total_headers"] == 5
    header_names = [h["header"] for h in spec["headers"]]
    assert "X-Content-Type-Options" in header_names
    assert "X-Frame-Options" in header_names
    assert "X-XSS-Protection" in header_names
    assert "Strict-Transport-Security" in header_names
    assert "Referrer-Policy" in header_names

    # Test actual live response headers from FastAPI
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_secret_management_matrix_and_rules():
    matrix = get_secret_management_matrix()
    secret_names = [s["secret"] for s in matrix["secrets"]]
    assert "GROQ_API_KEY" in secret_names
    assert "QDRANT_API_KEY" in secret_names
    assert "DATABASE_URL" in secret_names
    assert "UPSTASH_REDIS_URL" in secret_names
    assert "R2_ACCESS_KEY" in secret_names
    assert "API keys (user)" in secret_names

    assert len(matrix["rules"]) == 4
    rule_titles = [r["title"] for r in matrix["rules"]]
    assert "Never commit secrets to Git" in rule_titles
    assert "Never log secrets" in rule_titles
    assert "Never expose in responses" in rule_titles
    assert "Different keys per environment" in rule_titles


def test_api_key_masking():
    # Test prefix format
    assert mask_api_key("mgpt_live_abcdef123456") == "mgpt_****123456"
    assert mask_api_key("pk_live_sec9876543210") == "pk_****543210"
    
    # Generic format
    assert mask_api_key("customsecretkey9999") == "cus****9999"
    
    # Short / empty
    assert mask_api_key("") == ""
    assert mask_api_key("abc") == "mgpt_****"


def test_cors_policy_specification():
    dev_cors = get_cors_policy_spec(is_production=False)
    assert "https://memegpt.com" in dev_cors["allowed_origins"]
    assert "http://localhost:3000" in dev_cors["allowed_origins"]
    assert "*" not in dev_cors["allowed_origins"]

    prod_cors = get_cors_policy_spec(is_production=True)
    assert "https://memegpt.com" in prod_cors["allowed_origins"]
    assert "http://localhost:3000" not in prod_cors["allowed_origins"]
    assert "*" not in prod_cors["allowed_origins"]


def test_prelaunch_checklist_and_compliance():
    checklist = get_security_prelaunch_checklist()
    assert checklist["total_items"] == 12
    ids = [item["id"] for item in checklist["checklist"]]
    assert "SEC-01" in ids
    assert "SEC-12" in ids

    compliance = evaluate_security_compliance(is_production=False)
    assert compliance["status"] == "COMPLIANT"
    assert compliance["compliance_percentage"] == 100.0
    assert compliance["passed_items"] == 12


def test_security_api_endpoints():
    res_layers = client.get("/api/v1/security/layers")
    assert res_layers.status_code == 200
    assert res_layers.json()["total_layers"] == 6

    res_headers = client.get("/api/v1/security/headers")
    assert res_headers.status_code == 200
    assert res_headers.json()["total_headers"] == 5

    res_secrets = client.get("/api/v1/security/secrets")
    assert res_secrets.status_code == 200
    assert len(res_secrets.json()["secrets"]) == 6

    res_cors = client.get("/api/v1/security/cors?production=true")
    assert res_cors.status_code == 200
    assert res_cors.json()["policy"]["is_production"] is True

    res_check = client.get("/api/v1/security/checklist")
    assert res_check.status_code == 200
    assert res_check.json()["total_items"] == 12

    res_comp = client.get("/api/v1/security/compliance")
    assert res_comp.status_code == 200
    assert res_comp.json()["compliance_percentage"] == 100.0

    res_mask = client.post("/api/v1/security/mask-key", json={"api_key": "mgpt_live_9988776655"})
    assert res_mask.status_code == 200
    assert res_mask.json()["masked_key"] == "mgpt_****776655"
