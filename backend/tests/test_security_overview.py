"""Tests for Security Overview & Threat Modeling from 11_Security/Security_Overview.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.security_overview_service import (
    get_defense_in_depth_layers,
    get_owasp_top_10_matrix,
    get_threat_model_matrix,
    get_master_security_checklist,
    evaluate_owasp_compliance_status,
)

client = TestClient(app)


def test_defense_in_depth_layers():
    res = get_defense_in_depth_layers()
    assert res["total_layers"] == 5
    names = [layer["name"] for layer in res["layers"]]
    assert names == [
        "Network Layer",
        "Application Layer",
        "Input Layer",
        "Data Layer",
        "Infrastructure Layer",
    ]


def test_owasp_top_10_matrix():
    res = get_owasp_top_10_matrix()
    assert res["total_risks"] == 10
    codes = [r["code"] for r in res["owasp_risks"]]
    assert codes == ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"]
    
    a01 = next(r for r in res["owasp_risks"] if r["code"] == "A01")
    assert a01["risk"] == "Broken Access Control"
    
    a03 = next(r for r in res["owasp_risks"] if r["code"] == "A03")
    assert a03["risk"] == "Injection"
    assert "ORM" in a03["mitigation"]


def test_threat_model_matrix():
    res = get_threat_model_matrix()
    assert res["total_threats"] == 7
    threat_names = [t["threat"] for t in res["threats"]]
    assert "DDoS attack" in threat_names
    assert "API key theft" in threat_names
    assert "SQL injection" in threat_names
    assert "XSS attack" in threat_names
    assert "Prompt injection" in threat_names
    assert "Data breach" in threat_names
    assert "Dependency vulnerability" in threat_names


def test_master_security_checklist():
    res = get_master_security_checklist()
    assert res["total_items"] == 12
    assert res["completed_items"] == 12
    assert res["completion_rate"] == 100.0


def test_owasp_compliance_status():
    status = evaluate_owasp_compliance_status()
    assert status["status"] == "COMPLIANT"
    assert status["owasp_coverage_percentage"] == 100.0
    assert status["total_risks"] == 10
    assert status["mitigated_risks"] == 10


def test_security_overview_api_endpoints():
    res_layers = client.get("/api/v1/security/overview/layers")
    assert res_layers.status_code == 200
    assert res_layers.json()["total_layers"] == 5

    res_owasp = client.get("/api/v1/security/overview/owasp")
    assert res_owasp.status_code == 200
    assert res_owasp.json()["total_risks"] == 10

    res_threat = client.get("/api/v1/security/overview/threat-model")
    assert res_threat.status_code == 200
    assert res_threat.json()["total_threats"] == 7

    res_audit = client.get("/api/v1/security/overview/audit-checklist")
    assert res_audit.status_code == 200
    assert res_audit.json()["completion_rate"] == 100.0

    res_status = client.get("/api/v1/security/overview/owasp-status")
    assert res_status.status_code == 200
    assert res_status.json()["owasp_coverage_percentage"] == 100.0
