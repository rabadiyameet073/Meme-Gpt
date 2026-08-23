"""Tests for Security Section Manifest & Global Health from 11_Security/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.security_manifest_service import (
    get_security_section_manifest,
    get_security_posture_summary,
    get_security_subsystem_health,
)

client = TestClient(app)


def test_security_section_manifest():
    manifest = get_security_section_manifest()
    assert manifest["section_id"] == "11"
    assert manifest["section_name"] == "Security"
    assert manifest["total_documents"] == 6

    files = [doc["file"] for doc in manifest["documents"]]
    assert "API_Security.md" in files
    assert "Data_Privacy.md" in files
    assert "Input_Validation.md" in files
    assert "Rate_Limiting_Security.md" in files
    assert "Security_Overview.md" in files
    assert "README.md" in files

    nav = manifest["navigation"]
    assert nav["previous_section"] == "10_Testing"
    assert nav["next_section"] == "12_Deployment"


def test_security_posture_summary():
    posture = get_security_posture_summary()
    assert "transport_security" in posture
    assert "browser_security" in posture
    assert "application_security" in posture
    assert "data_privacy" in posture
    assert "ddos_and_rate_limiting" in posture
    assert "secret_management" in posture

    assert posture["transport_security"]["protocol"] == "TLS 1.3 / HTTPS"
    assert "max-age=31536000" in posture["transport_security"]["hsts"]
    assert posture["browser_security"]["x_frame_options"] == "DENY"
    assert posture["ddos_and_rate_limiting"]["search_quota"] == "30 req/min"


def test_security_subsystem_health_diagnostic():
    health = get_security_subsystem_health()
    assert health["status"] in ("HEALTHY", "DEGRADED")
    subsystems = health["subsystems"]
    assert "api_security" in subsystems
    assert "data_privacy" in subsystems
    assert "input_validation" in subsystems
    assert "rate_limiting" in subsystems


def test_security_manifest_api_endpoints():
    res_man = client.get("/api/v1/security/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["section_id"] == "11"
    assert res_man.json()["total_documents"] == 6

    res_post = client.get("/api/v1/security/posture")
    assert res_post.status_code == 200
    assert "transport_security" in res_post.json()

    res_health = client.get("/api/v1/security/health")
    assert res_health.status_code == 200
    assert "subsystems" in res_health.json()
