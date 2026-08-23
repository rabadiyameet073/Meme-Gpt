"""Tests for Deployment Section Manifest & Global Health from 12_Deployment/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.deployment_manifest_service import (
    get_deployment_section_manifest,
    get_deployment_posture_summary,
    get_deployment_subsystem_health,
)

client = TestClient(app)


def test_deployment_section_manifest():
    manifest = get_deployment_section_manifest()
    assert manifest["section_id"] == "12"
    assert manifest["section_name"] == "Deployment"
    assert manifest["total_documents"] == 7

    files = [doc["file"] for doc in manifest["documents"]]
    assert "CI_CD_Pipeline.md" in files
    assert "Deployment_Overview.md" in files
    assert "Infrastructure.md" in files
    assert "Monitoring.md" in files
    assert "Rollback_Strategy.md" in files
    assert "Scaling.md" in files
    assert "README.md" in files

    nav = manifest["navigation"]
    assert nav["previous_section"] == "11_Security"
    assert nav["next_section"] == "13_Project_Management"


def test_deployment_posture_summary():
    posture = get_deployment_posture_summary()
    assert "hosting_topology" in posture
    assert "automation_and_ci_cd" in posture
    assert "cost_and_capacity" in posture
    assert "monitoring_and_telemetry" in posture

    assert "Vercel" in posture["hosting_topology"]["frontend"]
    assert "Railway" in posture["hosting_topology"]["backend"]
    assert "GitHub Actions" in posture["automation_and_ci_cd"]["ci_pipeline"]
    assert "$0–$7" in posture["cost_and_capacity"]["mvp_monthly_burn"]


def test_deployment_subsystem_health():
    health = get_deployment_subsystem_health()
    assert health["status"] in ("HEALTHY", "DEGRADED")
    subsystems = health["subsystems"]
    assert "ci_cd_pipeline" in subsystems
    assert "deployment_readiness" in subsystems
    assert "infrastructure" in subsystems
    assert "monitoring_metrics" in subsystems


def test_deployment_manifest_api_endpoints():
    res_man = client.get("/api/v1/deployment/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["section_id"] == "12"
    assert res_man.json()["total_documents"] == 7

    res_post = client.get("/api/v1/deployment/posture")
    assert res_post.status_code == 200
    assert "hosting_topology" in res_post.json()

    res_hlth = client.get("/api/v1/deployment/health")
    assert res_hlth.status_code == 200
    assert "subsystems" in res_hlth.json()
