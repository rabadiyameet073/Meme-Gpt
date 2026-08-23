"""Tests for SEO & Marketing Section Manifest & Diagnostic Health from 16_SEO_Marketing/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.marketing_manifest_service import (
    get_marketing_section_manifest,
    get_marketing_posture_summary,
    get_marketing_subsystem_health,
)

client = TestClient(app)


def test_marketing_section_manifest():
    manifest = get_marketing_section_manifest()
    assert manifest["section_id"] == "16_SEO_Marketing"
    assert manifest["total_documents"] == 5
    assert "navigation" in manifest
    assert manifest["navigation"]["previous"]["section"] == "15_Mobile"
    assert manifest["navigation"]["next"]["section"] == "17_Appendix"

    files = [d["file"] for d in manifest["documents"]]
    assert "App_Store_Optimization.md" in files
    assert "Launch_Strategy.md" in files
    assert "Marketing_Plan.md" in files
    assert "SEO_Strategy.md" in files
    assert "README.md" in files


def test_marketing_posture_summary():
    posture = get_marketing_posture_summary()
    assert "growth_readiness" in posture
    assert posture["growth_readiness"]["organic_channels_count"] == 5
    assert "$0" in posture["growth_readiness"]["total_marketing_budget"]
    assert "22.85M" in posture["growth_readiness"]["reddit_audience_reach"]
    assert posture["acquisition_mix"]["seo_share"] == "50%"
    assert posture["acquisition_mix"]["aso_share"] == "25%"
    assert posture["growth_milestones"]["scaled_growth_dau"] == 50000


def test_marketing_subsystem_health():
    health = get_marketing_subsystem_health()
    assert health["status"] == "HEALTHY"
    assert health["aso_strategy_loaded"] is True
    assert health["launch_playbooks_loaded"] is True
    assert health["growth_funnel_configured"] is True
    assert health["zero_cost_budget_compliant"] is True


def test_marketing_manifest_api_endpoints():
    res_man = client.get("/api/v1/marketing/manifest")
    assert res_man.status_code == 200
    assert res_man.json()["total_documents"] == 5

    res_post = client.get("/api/v1/marketing/posture")
    assert res_post.status_code == 200
    assert "growth_readiness" in res_post.json()

    res_health = client.get("/api/v1/marketing/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"
