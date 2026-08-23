"""Tests for Appendix Section Manifest & Health from 17_Appendix/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.appendix_manifest_service import (
    get_appendix_section_manifest,
    get_appendix_posture_summary,
    get_appendix_subsystem_health,
)

client = TestClient(app)


def test_appendix_section_manifest():
    manifest = get_appendix_section_manifest()
    assert manifest["section_id"] == "17_Appendix"
    assert manifest["total_documents"] == 4
    assert manifest["previous_section"]["title"] == "16_SEO_Marketing"

    doc_ids = [d["id"] for d in manifest["documents"]]
    assert "changelog" in doc_ids
    assert "glossary" in doc_ids
    assert "readme" in doc_ids
    assert "references" in doc_ids


def test_appendix_posture_summary():
    posture = get_appendix_posture_summary()
    assert posture["section"] == "17_Appendix"
    assert posture["status"] == "HEALTHY"
    assert posture["changelog_posture"]["current_version"] == "v1.0.0"
    assert posture["glossary_posture"]["total_terms"] == 41
    assert posture["references_posture"]["external_docs_count"] == 25


def test_appendix_subsystem_health():
    health = get_appendix_subsystem_health()
    assert health["subsystem"] == "appendix_reference_hub"
    assert health["status"] == "HEALTHY"
    assert health["score"] == 1.0
    assert len(health["checks"]) == 4
    assert all(c["status"] == "PASS" for c in health["checks"])


def test_appendix_manifest_api_endpoints():
    res_man = client.get("/api/v1/appendix/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 4

    res_post = client.get("/api/v1/appendix/posture")
    assert res_post.status_code == 200
    assert res_post.json()["status"] == "HEALTHY"

    res_hlth = client.get("/api/v1/appendix/health")
    assert res_hlth.status_code == 200
    assert res_hlth.json()["score"] == 1.0
