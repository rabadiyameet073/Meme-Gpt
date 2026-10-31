"""Tests for Deployment Overview Implementation from 12_Deployment/Deployment_Overview.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.deployment_overview_service import (
    get_deployment_architecture,
    get_step_by_step_deployment_guide,
    get_infrastructure_cost_analysis,
    get_environment_configurations,
    get_cold_start_mitigation_spec,
    get_rollback_strategies,
    get_pre_deploy_security_checklist,
    evaluate_deployment_readiness,
)

client = TestClient(app)


def test_deployment_architecture():
    arch = get_deployment_architecture()
    assert "developer_machine" in arch
    assert "ci_cd_pipeline" in arch
    assert "production_topology" in arch
    assert len(arch["production_topology"]) == 6
    services = [s["service"] for s in arch["production_topology"]]
    assert "Frontend" in services
    assert "Backend" in services
    assert "Vector Database" in services
    assert "Relational Database" in services
    assert "Cache Layer" in services
    assert "Media Storage" in services


def test_step_by_step_deployment_guide():
    steps = get_step_by_step_deployment_guide()
    assert "backend_railway" in steps
    assert "frontend_vercel" in steps
    assert len(steps["backend_railway"]["steps"]) == 5
    assert len(steps["frontend_vercel"]["steps"]) == 5


def test_infrastructure_cost_analysis():
    costs = get_infrastructure_cost_analysis()
    assert costs["total_services"] == 10
    assert costs["mvp_monthly_total"] == "$0"
    assert costs["scaled_monthly_total_10k_dau"] == "~$42"


def test_environment_configurations():
    envs = get_environment_configurations()
    env_names = [e["environment"] for e in envs["environments"]]
    assert "Development" in env_names
    assert "Staging" in env_names
    assert "Production" in env_names


def test_cold_start_mitigation_spec():
    spec = get_cold_start_mitigation_spec()
    assert "problem" in spec
    assert "uptimerobot_config" in spec
    assert spec["uptimerobot_config"]["interval"] == "5 minutes"


def test_rollback_strategies():
    rollbacks = get_rollback_strategies()
    assert rollbacks["total_scenarios"] == 4
    targets = [s["target"] for s in rollbacks["strategies"]]
    assert "Vercel" in targets
    assert "Railway" in targets


def test_pre_deploy_security_checklist():
    checklist = get_pre_deploy_security_checklist()
    assert checklist["total_items"] == 8

    # The checklist is computed from repository state, so it must be internally
    # consistent and carry auditable evidence for every row.
    for item in checklist["checklist"]:
        assert item["status"] in ("VERIFIED", "FAILED", "UNVERIFIABLE")
        assert item["passed"] is (item["status"] == "VERIFIED")
        assert item["evidence"], f"row {item['id']} has no evidence"

    assert checklist["passed_items"] == sum(1 for i in checklist["checklist"] if i["passed"])
    assert checklist["failed_items"] + checklist["unverifiable_items"] + checklist["passed_items"] == 8


def test_pre_deploy_checklist_has_no_unresolved_gaps():
    """Every item must be genuinely verified, not merely present."""
    checklist = get_pre_deploy_security_checklist()
    unresolved = [
        f"{i['item']} -> {i['status']}: {i['evidence']}"
        for i in checklist["checklist"]
        if i["status"] != "VERIFIED"
    ]
    assert not unresolved, "unresolved pre-deploy checks: " + "; ".join(unresolved)
    assert checklist["compliance_percentage"] == 100.0


def test_single_worker_probe_matches_railway_config():
    """Item 6 must reflect railway.toml rather than a literal string."""
    from app.core import attestation

    counts = attestation._railway_worker_counts()
    assert counts, "no railway.toml declares a worker count"
    assert set(counts.values()) == {1}, f"railway worker counts are {counts}"

    item = get_pre_deploy_security_checklist()["checklist"][5]
    assert item["status"] == "VERIFIED"
    assert "workers" in item["evidence"] or "worker" in item["evidence"]


def test_evaluate_deployment_readiness():
    readiness = evaluate_deployment_readiness()
    assert readiness["status"] in ("READY", "NOT_READY")
    assert "checks" in readiness
    assert readiness["satisfied_checks"] <= readiness["total_checks"]
    assert readiness["readiness_score"] == round(
        readiness["satisfied_checks"] / readiness["total_checks"] * 100, 1
    )


def test_deployment_overview_api_endpoints():
    res_arch = client.get("/api/v1/deployment/overview/architecture")
    assert res_arch.status_code == 200
    assert "production_topology" in res_arch.json()

    res_steps = client.get("/api/v1/deployment/overview/steps")
    assert res_steps.status_code == 200
    assert "backend_railway" in res_steps.json()

    res_costs = client.get("/api/v1/deployment/overview/costs")
    assert res_costs.status_code == 200
    assert res_costs.json()["mvp_monthly_total"] == "$0"

    res_envs = client.get("/api/v1/deployment/overview/environments")
    assert res_envs.status_code == 200
    assert len(res_envs.json()["environments"]) == 3

    res_cold = client.get("/api/v1/deployment/overview/cold-start")
    assert res_cold.status_code == 200
    assert "uptimerobot_config" in res_cold.json()

    res_roll = client.get("/api/v1/deployment/overview/rollbacks")
    assert res_roll.status_code == 200
    assert res_roll.json()["total_scenarios"] == 4

    res_check = client.get("/api/v1/deployment/overview/pre-deploy-checklist")
    assert res_check.status_code == 200
    payload = res_check.json()
    assert payload["compliance_percentage"] == round(
        payload["passed_items"] / payload["total_items"] * 100, 1
    )
    assert all(item.get("evidence") for item in payload["checklist"])

    res_ready = client.get("/api/v1/deployment/overview/readiness")
    assert res_ready.status_code == 200
    assert "readiness_score" in res_ready.json()
