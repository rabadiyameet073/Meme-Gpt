"""Tests for Rollback Strategy & Disaster Recovery from 12_Deployment/Rollback_Strategy.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.rollback_service import (
    get_rollback_decision_tree,
    get_component_rollback_procedures,
    get_blue_green_deployment_spec,
    get_rollback_best_practices,
    simulate_rollback_scenario,
    evaluate_rollback_readiness,
)

client = TestClient(app)


def test_rollback_decision_tree():
    tree = get_rollback_decision_tree()
    assert "trigger_condition" in tree
    assert "workflow" in tree
    assert len(tree["workflow"]) == 5


def test_component_rollback_procedures():
    res = get_component_rollback_procedures()
    assert res["total_components"] == 4
    components = [c["component"] for c in res["components"]]
    assert "Frontend" in components
    assert "Backend" in components
    assert "Database" in components
    assert "Vector Index" in components

    fe = next(c for c in res["components"] if c["component"] == "Frontend")
    assert fe["rto"] == "<30 seconds"

    be = next(c for c in res["components"] if c["component"] == "Backend")
    assert be["rto"] == "2-5 minutes"


def test_blue_green_deployment_spec():
    bg = get_blue_green_deployment_spec()
    assert bg["phase"] == "Phase 3 (High-Scale Production)"
    assert "topology" in bg
    assert "verification_flow" in bg


def test_rollback_best_practices():
    res = get_rollback_best_practices()
    assert res["total_practices"] == 5
    titles = [p["title"] for p in res["practices"]]
    assert "Monitor for 5 minutes after every deploy" in titles
    assert "Keep previous 3 deployments" in titles
    assert "Database backups before migrations" in titles
    assert "Never roll forward" in titles
    assert "Document every rollback" in titles


def test_simulate_rollback_scenario():
    # Valid Frontend
    fe_sim = simulate_rollback_scenario("Frontend")
    assert fe_sim["success"] is True
    assert fe_sim["status"] == "ROLLBACK_READY"
    assert fe_sim["platform"] == "Vercel"
    assert "vercel rollback" in [opt["command"] for opt in fe_sim["runbook_options"]]

    # Valid Backend
    be_sim = simulate_rollback_scenario("Backend")
    assert be_sim["success"] is True
    assert be_sim["platform"] == "Railway"

    # Invalid component
    inv_sim = simulate_rollback_scenario("UnknownComponent")
    assert inv_sim["success"] is False
    assert "error" in inv_sim


def test_evaluate_rollback_readiness():
    readiness = evaluate_rollback_readiness()
    assert readiness["status"] == "HEALTHY"
    assert readiness["total_recovery_runbooks"] == 4
    assert readiness["immutable_deployments_retained"] is True


def test_rollback_api_endpoints():
    res_tree = client.get("/api/v1/deployment/rollback/decision-tree")
    assert res_tree.status_code == 200
    assert "workflow" in res_tree.json()

    res_proc = client.get("/api/v1/deployment/rollback/procedures")
    assert res_proc.status_code == 200
    assert res_proc.json()["total_components"] == 4

    res_bg = client.get("/api/v1/deployment/rollback/blue-green")
    assert res_bg.status_code == 200
    assert "topology" in res_bg.json()

    res_prac = client.get("/api/v1/deployment/rollback/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 5

    res_sim = client.post("/api/v1/deployment/rollback/simulate", json={"component": "Frontend"})
    assert res_sim.status_code == 200
    assert res_sim.json()["status"] == "ROLLBACK_READY"

    res_ready = client.get("/api/v1/deployment/rollback/readiness")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "HEALTHY"
