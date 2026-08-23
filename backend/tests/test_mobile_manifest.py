"""Tests for Mobile Section Manifest & Diagnostic Health from 15_Mobile/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.mobile_manifest_service import (
    get_mobile_section_manifest,
    get_mobile_posture_summary,
    get_mobile_subsystem_health,
)

client = TestClient(app)


def test_mobile_section_manifest():
    manifest = get_mobile_section_manifest()
    assert manifest["section_id"] == "15_Mobile"
    assert manifest["total_documents"] == 2
    assert manifest["completed_documents"] == 2
    assert "navigation" in manifest
    assert manifest["navigation"]["previous"]["section"] == "14_Troubleshooting"
    assert manifest["navigation"]["next"]["section"] == "16_References"

    files = [d["file"] for d in manifest["documents"]]
    assert "Mobile_Overview.md" in files
    assert "README.md" in files


def test_mobile_posture_summary():
    posture = get_mobile_posture_summary()
    assert "framework_and_tooling" in posture
    assert "React Native 0.74" in posture["framework_and_tooling"]["core_framework"]
    assert "screen_and_native_architecture" in posture
    assert len(posture["screen_and_native_architecture"]["screens"]) == 4
    assert len(posture["screen_and_native_architecture"]["native_modules"]) == 4
    assert posture["app_size_compliance"]["estimated_binary_size_mb"] == 29.0
    assert posture["phase_2_readiness"] == "READY"


def test_mobile_subsystem_health():
    health = get_mobile_subsystem_health()
    assert health["status"] == "HEALTHY"
    assert health["mobile_specs_loaded"] is True
    assert health["screens_configured"] == 4
    assert health["binary_size_compliant"] is True
    assert health["phase_2_delivery_status"] == "ON_TRACK"


def test_mobile_manifest_api_endpoints():
    res_man = client.get("/api/v1/mobile/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 2

    res_post = client.get("/api/v1/mobile/posture")
    assert res_post.status_code == 200
    assert "framework_and_tooling" in res_post.json()

    res_health = client.get("/api/v1/mobile/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"
