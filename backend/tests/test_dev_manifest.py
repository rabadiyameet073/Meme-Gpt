"""Tests for Section 09 Development Manifest from 09_Development/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.dev_manifest_service import (
    get_development_section_manifest,
    verify_development_system_health,
)

client = TestClient(app)


def test_development_manifest_registry():
    manifest = get_development_section_manifest()
    assert manifest["section_id"] == "09_Development"
    assert manifest["total_documents"] == 7
    assert len(manifest["documents"]) == 7

    filenames = [d["filename"] for d in manifest["documents"]]
    assert "Code_Review.md" in filenames
    assert "Coding_Standards.md" in filenames
    assert "Contributing.md" in filenames
    assert "Debugging_Guide.md" in filenames
    assert "Development_Workflow.md" in filenames
    assert "Git_Workflow.md" in filenames
    assert "README.md" in filenames


def test_verify_development_system_health():
    health = verify_development_system_health()
    assert health["status"] == "healthy"
    assert health["total_modules"] == 6
    assert health["checks"]["code_review"]["status"] == "healthy"
    assert health["checks"]["coding_standards"]["status"] == "healthy"
    assert health["checks"]["contributing"]["status"] == "healthy"
    assert health["checks"]["debugging"]["status"] == "healthy"
    assert health["checks"]["workflow"]["status"] == "healthy"
    assert health["checks"]["git_workflow"]["status"] == "healthy"


def test_dev_manifest_api_endpoints():
    res_man = client.get("/api/v1/dev/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 7

    res_health = client.get("/api/v1/dev/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
