"""Tests for Technology Stack Reference & Selection Rationale from 16_References/Technology_Stack.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.tech_stack_service import (
    get_all_tech_stack_components,
    get_tech_stack_by_id,
    search_tech_stack,
    get_tech_stack_tiers_summary,
    evaluate_tech_stack_compliance,
)

client = TestClient(app)


def test_get_all_tech_stack_components():
    all_techs = get_all_tech_stack_components()
    assert all_techs["total_technologies"] >= 20

    be_techs = get_all_tech_stack_components(tier="backend")
    assert be_techs["total_technologies"] == 3

    fe_techs = get_all_tech_stack_components(tier="frontend")
    assert fe_techs["total_technologies"] == 4

    ai_techs = get_all_tech_stack_components(tier="ai_ml")
    assert ai_techs["total_technologies"] == 4

    infra_techs = get_all_tech_stack_components(tier="infrastructure")
    assert infra_techs["total_technologies"] == 5

    dev_techs = get_all_tech_stack_components(tier="dev_tools")
    assert dev_techs["total_technologies"] == 7


def test_get_tech_stack_by_id():
    fastapi = get_tech_stack_by_id("TECH_BACKEND_FASTAPI")
    assert fastapi is not None
    assert fastapi["name"] == "FastAPI"
    assert "Pydantic" in fastapi["why_selected"]

    qdrant = get_tech_stack_by_id("tech_aiml_qdrant")
    assert qdrant is not None
    assert qdrant["name"] == "Qdrant"
    assert "HNSW" in qdrant["why_used"]

    assert get_tech_stack_by_id("TECH_UNKNOWN") is None


def test_search_tech_stack():
    res_vite = search_tech_stack("Vite")
    assert res_vite["total_matches"] >= 1
    assert any("Vite" in m["name"] for m in res_vite["matches"])

    res_docker = search_tech_stack("Docker")
    assert res_docker["total_matches"] >= 1

    res_hnsw = search_tech_stack("HNSW")
    assert res_hnsw["total_matches"] >= 1


def test_tech_stack_tiers_summary():
    tiers = get_tech_stack_tiers_summary()
    assert tiers["total_tiers"] == 5
    assert tiers["tier_distribution"]["backend"] == 3
    assert tiers["tier_distribution"]["frontend"] == 4
    assert tiers["tier_distribution"]["ai_ml"] == 4
    assert tiers["tier_distribution"]["infrastructure"] == 5
    assert tiers["tier_distribution"]["dev_tools"] == 7


def test_evaluate_tech_stack_compliance():
    comp = evaluate_tech_stack_compliance()
    assert comp["status"] == "COMPLIANT"
    assert comp["phase_6_requirement_met"] is True
    assert comp["compliance_percentage"] == "100.0%"
    assert len(comp["tiers_covered"]) == 5


def test_technology_stack_api_endpoints():
    res_all = client.get("/api/v1/references/tech-stack")
    assert res_all.status_code == 200
    assert res_all.json()["total_technologies"] >= 20

    res_filter = client.get("/api/v1/references/tech-stack?tier=infrastructure")
    assert res_filter.status_code == 200
    assert res_filter.json()["total_technologies"] == 5

    res_tiers = client.get("/api/v1/references/tech-stack/tiers")
    assert res_tiers.status_code == 200
    assert res_tiers.json()["total_tiers"] == 5

    res_search = client.get("/api/v1/references/tech-stack/search?q=Tailwind")
    assert res_search.status_code == 200
    assert res_search.json()["total_matches"] >= 1

    res_comp = client.get("/api/v1/references/tech-stack/compliance")
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "COMPLIANT"

    res_single = client.get("/api/v1/references/tech-stack/TECH_BACKEND_PYTHON")
    assert res_single.status_code == 200
    assert res_single.json()["technology"]["name"] == "Python 3.11"

    res_404 = client.get("/api/v1/references/tech-stack/INVALID_TECH_ID")
    assert res_404.status_code == 404
