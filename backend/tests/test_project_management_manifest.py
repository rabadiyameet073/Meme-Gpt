"""Tests for Project Management Manifest & Governance from 13_Project_Management/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.project_management_manifest_service import (
    get_project_management_section_manifest,
    get_project_management_posture_summary,
    get_project_management_subsystem_health,
)

client = TestClient(app)


def test_project_management_section_manifest():
    manifest = get_project_management_section_manifest()
    assert manifest["section_id"] == "13_Project_Management"
    assert manifest["total_documents"] == 4
    assert "navigation" in manifest
    assert manifest["navigation"]["previous"]["section"] == "12_Deployment"
    assert manifest["navigation"]["next"]["section"] == "14_Troubleshooting"

    files = [d["file"] for d in manifest["documents"]]
    assert "MVP_Phases.md" in files
    assert "Roadmap.md" in files
    assert "Risk_Register.md" in files
    assert "README.md" in files


def test_project_management_posture_summary():
    posture = get_project_management_posture_summary()
    assert "project_governance" in posture
    assert posture["project_governance"]["total_sprints"] == 4
    assert posture["project_governance"]["total_duration"] == "8 Weeks"
    assert "team_allocation" in posture
    assert "quality_gates" in posture
    assert posture["quality_gates"]["definition_of_done_criteria_count"] == 6


def test_project_management_subsystem_health():
    health = get_project_management_subsystem_health()
    assert health["status"] == "HEALTHY"
    assert health["sprint_roadmap_loaded"] is True
    assert health["definition_of_done_active"] is True
    assert health["active_sprints"] == 4


def test_project_management_manifest_api_endpoints():
    res_man = client.get("/api/v1/project-management/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 4

    res_post = client.get("/api/v1/project-management/posture")
    assert res_post.status_code == 200
    assert "project_governance" in res_post.json()

    res_health = client.get("/api/v1/project-management/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"
