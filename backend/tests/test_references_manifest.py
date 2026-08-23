"""Tests for References Section Manifest & Diagnostic Health from 16_References/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.references_manifest_service import (
    get_references_section_manifest,
    get_references_posture_summary,
    get_references_subsystem_health,
)

client = TestClient(app)


def test_references_section_manifest():
    manifest = get_references_section_manifest()
    assert manifest["section_id"] == "16_References"
    assert manifest["total_documents"] == 3
    assert "navigation" in manifest
    assert manifest["navigation"]["previous"]["section"] == "15_FAQs"
    assert manifest["navigation"]["next"]["section"] == "17_Appendix"

    files = [d["file"] for d in manifest["documents"]]
    assert "Technology_Stack.md" in files
    assert "External_Resources.md" in files
    assert "README.md" in files


def test_references_posture_summary():
    posture = get_references_posture_summary()
    assert "resources_readiness" in posture
    assert posture["resources_readiness"]["grand_total_external_resources"] == 40
    assert posture["resources_readiness"]["official_documentation_links"] == 25
    assert posture["resources_readiness"]["foundational_research_papers"] == 6
    assert "citation_coverage" in posture


def test_references_subsystem_health():
    health = get_references_subsystem_health()
    assert health["status"] == "HEALTHY"
    assert health["external_resources_loaded"] is True
    assert health["grand_total_assets"] == 40


def test_references_manifest_api_endpoints():
    res_man = client.get("/api/v1/references/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 3

    res_post = client.get("/api/v1/references/posture")
    assert res_post.status_code == 200
    assert "resources_readiness" in res_post.json()

    res_health = client.get("/api/v1/references/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"
