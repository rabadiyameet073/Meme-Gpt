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
    assert checklist["passed_items"] == 8
    assert checklist["compliance_percentage"] == 100.0


def test_evaluate_deployment_readiness():
    readiness = evaluate_deployment_readiness()
    assert readiness["status"] in ("READY", "NOT_READY")
    assert "checks" in readiness


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
    assert res_check.json()["compliance_percentage"] == 100.0

    res_ready = client.get("/api/v1/deployment/overview/readiness")
    assert res_ready.status_code == 200
    assert "readiness_score" in res_ready.json()
