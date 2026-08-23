"""Tests for FAQ Section Manifest & Health from 15_FAQs/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.faq_manifest_service import (
    get_faq_section_manifest,
    get_faq_posture_summary,
    get_faq_subsystem_health,
)

client = TestClient(app)


def test_faq_section_manifest():
    manifest = get_faq_section_manifest()
    assert manifest["section_id"] == "15_FAQs"
    assert manifest["total_documents"] == 2
    assert manifest["completed_documents"] == 2
    assert "navigation" in manifest
    assert manifest["navigation"]["previous"]["section"] == "14_Troubleshooting"
    assert manifest["navigation"]["next"]["section"] == "15_Mobile"

    files = [d["file"] for d in manifest["documents"]]
    assert "General_FAQ.md" in files
    assert "README.md" in files


def test_faq_posture_summary():
    posture = get_faq_posture_summary()
    assert "knowledge_base_readiness" in posture
    assert posture["knowledge_base_readiness"]["total_indexed_faqs"] == 21
    assert posture["knowledge_base_readiness"]["total_categories"] == 3
    assert "technical_catalog" in posture
    assert posture["technical_catalog"]["total_ai_models_documented"] == 6


def test_faq_subsystem_health():
    health = get_faq_subsystem_health()
    assert health["status"] == "HEALTHY"
    assert health["knowledge_base_active"] is True
    assert health["search_engine_active"] is True
    assert health["total_faqs_indexed"] == 21


def test_faq_manifest_api_endpoints():
    res_man = client.get("/api/v1/faqs/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 2

    res_post = client.get("/api/v1/faqs/posture")
    assert res_post.status_code == 200
    assert "knowledge_base_readiness" in res_post.json()

    res_health = client.get("/api/v1/faqs/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"
