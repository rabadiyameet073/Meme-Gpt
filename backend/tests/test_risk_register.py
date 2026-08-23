"""Tests for Risk Register & Mitigation Matrix from 13_Project_Management/Risk_Register.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.risk_register_service import (
    get_all_risks,
    get_risk_by_id,
    get_risk_matrix_quadrants,
    get_risk_summary_stats,
    audit_risk_mitigation_health,
)

client = TestClient(app)


def test_get_all_risks():
    res = get_all_risks()
    assert res["total_risks"] == 12
    assert len(res["risks"]) == 12
    ids = [r["id"] for r in res["risks"]]
    assert "R1" in ids
    assert "R3" in ids
    assert "R8" in ids
    assert "R12" in ids


def test_get_risks_filtered_by_severity():
    high_res = get_all_risks(severity="High")
    assert high_res["total_risks"] == 1
    assert high_res["risks"][0]["id"] == "R3"

    med_res = get_all_risks(severity="Medium")
    assert med_res["total_risks"] == 8

    low_res = get_all_risks(severity="Low")
    assert low_res["total_risks"] == 3


def test_get_risk_by_id():
    r1 = get_risk_by_id("R1")
    assert r1 is not None
    assert r1["id"] == "R1"
    assert "Groq" in r1["risk"]
    assert "Ollama" in r1["mitigation"]

    r3 = get_risk_by_id("R3")
    assert r3 is not None
    assert r3["severity"] == "High"
    assert r3["quadrant"] == "Critical - Act Now"

    # Case insensitive
    r8 = get_risk_by_id("r8")
    assert r8 is not None
    assert r8["id"] == "R8"

    # Non-existent
    assert get_risk_by_id("R999") is None


def test_get_risk_matrix_quadrants():
    res = get_risk_matrix_quadrants()
    assert "quadrants" in res
    quads = res["quadrants"]
    assert "Critical - Act Now" in quads
    assert "Monitor Closely" in quads
    assert "Mitigate" in quads
    assert "Accept" in quads

    critical_ids = [item["id"] for item in quads["Critical - Act Now"]]
    assert "R3" in critical_ids


def test_get_risk_summary_stats():
    stats = get_risk_summary_stats()
    assert stats["total_risks"] == 12
    assert stats["by_severity"]["High"] == 1
    assert stats["by_severity"]["Medium"] == 8
    assert stats["by_severity"]["Low"] == 3
    assert len(stats["critical_risks"]) == 1


def test_audit_risk_mitigation_health():
    audit = audit_risk_mitigation_health()
    assert audit["status"] == "HEALTHY"
    assert audit["total_risks_audited"] == 12
    assert audit["all_risks_have_mitigation_plan"] is True
    assert audit["unmitigated_count"] == 0


def test_risk_register_api_endpoints():
    res_list = client.get("/api/v1/project-management/risks")
    assert res_list.status_code == 200
    assert res_list.json()["total_risks"] == 12

    res_filt = client.get("/api/v1/project-management/risks?severity=High")
    assert res_filt.status_code == 200
    assert res_filt.json()["total_risks"] == 1

    res_r1 = client.get("/api/v1/project-management/risks/R1")
    assert res_r1.status_code == 200
    assert res_r1.json()["risk"]["id"] == "R1"

    res_quad = client.get("/api/v1/project-management/risks/matrix/quadrants")
    assert res_quad.status_code == 200
    assert "quadrants" in res_quad.json()

    res_stats = client.get("/api/v1/project-management/risks/summary/stats")
    assert res_stats.status_code == 200
    assert res_stats.json()["total_risks"] == 12

    res_audit = client.get("/api/v1/project-management/risks/audit/health")
    assert res_audit.status_code == 200
    assert res_audit.json()["status"] == "HEALTHY"

    res_404 = client.get("/api/v1/project-management/risks/R99")
    assert res_404.status_code == 404
