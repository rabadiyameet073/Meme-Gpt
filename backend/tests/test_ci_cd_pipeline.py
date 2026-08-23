"""Tests for CI/CD Pipeline Implementation from 12_Deployment/CI_CD_Pipeline.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.ci_cd_service import (
    get_pipeline_architecture,
    get_workflow_definitions,
    get_pipeline_durations,
    get_pipeline_secrets_spec,
    get_ci_cd_best_practices,
    run_smoke_test_validation,
    evaluate_ci_cd_pipeline_health,
)

client = TestClient(app)


def test_pipeline_architecture():
    arch = get_pipeline_architecture()
    assert "triggers" in arch
    assert "stages" in arch
    assert len(arch["stages"]) == 4
    triggers = arch["triggers"]
    assert "pull_request" in triggers
    assert "push_main" in triggers
    assert "schedule" in triggers


def test_workflow_definitions():
    workflows = get_workflow_definitions()
    assert workflows["total_workflows"] == 3
    files = [w["file"] for w in workflows["workflows"]]
    assert ".github/workflows/ci.yml" in files
    assert ".github/workflows/deploy.yml" in files
    assert ".github/workflows/cron.yml" in files


def test_pipeline_durations():
    durations = get_pipeline_durations()
    assert durations["total_steps"] == 6
    summary = durations["summary"]
    assert summary["total_ci_duration"] == "~3.5 min"
    assert summary["total_cd_duration"] == "~4 min"


def test_pipeline_secrets_spec():
    secrets = get_pipeline_secrets_spec()
    assert secrets["total_secrets"] == 6
    secret_names = [s["secret"] for s in secrets["secrets"]]
    assert "GROQ_API_KEY" in secret_names
    assert "QDRANT_URL" in secret_names
    assert "QDRANT_API_KEY" in secret_names
    assert "RAILWAY_TOKEN" in secret_names
    assert "VERCEL_TOKEN" in secret_names
    assert "DATABASE_URL" in secret_names


def test_ci_cd_best_practices():
    res = get_ci_cd_best_practices()
    assert res["total_practices"] == 5
    titles = [p["title"] for p in res["practices"]]
    assert "Block merge if CI fails" in titles
    assert "Run smoke tests after deploy" in titles
    assert "Use --detach for Railway" in titles
    assert "Cache pip and npm installs" in titles
    assert "Separate CI and CD workflows" in titles


def test_smoke_test_validation():
    res = run_smoke_test_validation()
    assert res["smoke_test_status"] == "PASSED"
    assert res["all_passed"] is True
    assert res["total_probes"] >= 1


def test_ci_cd_pipeline_health():
    health = evaluate_ci_cd_pipeline_health()
    assert health["status"] == "HEALTHY"
    assert health["workflows_directory_exists"] is True
    assert health["total_workflows_verified"] == 3


def test_ci_cd_api_endpoints():
    res_arch = client.get("/api/v1/deployment/ci-cd/architecture")
    assert res_arch.status_code == 200
    assert "triggers" in res_arch.json()

    res_wf = client.get("/api/v1/deployment/ci-cd/workflows")
    assert res_wf.status_code == 200
    assert res_wf.json()["total_workflows"] == 3

    res_dur = client.get("/api/v1/deployment/ci-cd/durations")
    assert res_dur.status_code == 200
    assert res_dur.json()["total_steps"] == 6

    res_sec = client.get("/api/v1/deployment/ci-cd/secrets")
    assert res_sec.status_code == 200
    assert res_sec.json()["total_secrets"] == 6

    res_prac = client.get("/api/v1/deployment/ci-cd/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 5

    res_smoke = client.post("/api/v1/deployment/ci-cd/smoke-test", json={"backend_url": "http://127.0.0.1:8000/api/v1/health"})
    assert res_smoke.status_code == 200
    assert res_smoke.json()["smoke_test_status"] == "PASSED"

    res_hlth = client.get("/api/v1/deployment/ci-cd/health")
    assert res_hlth.status_code == 200
    assert res_hlth.json()["status"] == "HEALTHY"
