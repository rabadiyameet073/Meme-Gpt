"""Tests for Troubleshooting Section Manifest & Diagnostic Health from 14_Troubleshooting/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.troubleshooting_manifest_service import (
    get_troubleshooting_section_manifest,
    get_troubleshooting_posture_summary,
    get_troubleshooting_subsystem_health,
)

client = TestClient(app)


def test_troubleshooting_section_manifest():
    manifest = get_troubleshooting_section_manifest()
    assert manifest["section_id"] == "14_Troubleshooting"
    assert manifest["total_documents"] == 3
    assert manifest["completed_documents"] == 3
    assert "navigation" in manifest
    assert manifest["navigation"]["previous"]["section"] == "13_Project_Management"
    assert manifest["navigation"]["next"]["section"] == "15_FAQs"

    files = [d["file"] for d in manifest["documents"]]
    assert "Common_Issues.md" in files
    assert "Debug_Guide.md" in files
    assert "README.md" in files


def test_troubleshooting_posture_summary():
    posture = get_troubleshooting_posture_summary()
    assert "diagnostic_readiness" in posture
    assert len(posture["diagnostic_readiness"]["flowcharts_configured"]) == 2
    assert posture["diagnostic_readiness"]["total_documented_issues"] == 8
    assert "component_debuggers" in posture
    assert "backend" in posture["component_debuggers"]
    assert "frontend" in posture["component_debuggers"]


def test_troubleshooting_subsystem_health():
    health = get_troubleshooting_subsystem_health()
    assert health["status"] == "HEALTHY"
    assert health["diagnostic_engine_active"] is True
    assert health["issue_catalog_loaded"] is True
    assert health["total_issues_indexed"] == 8


def test_troubleshooting_manifest_api_endpoints():
    res_man = client.get("/api/v1/troubleshooting/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 3

    res_post = client.get("/api/v1/troubleshooting/posture")
    assert res_post.status_code == 200
    assert "diagnostic_readiness" in res_post.json()

    res_health = client.get("/api/v1/troubleshooting/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"
