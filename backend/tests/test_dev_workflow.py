"""Tests for Development Workflow from 09_Development/Development_Workflow.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.development_workflow_service import (
    get_daily_workflow_overview,
    get_pre_commit_checklist_items,
    verify_pre_commit_status,
)

client = TestClient(app)


def test_workflow_overview_structure():
    overview = get_daily_workflow_overview()
    assert "workflow_steps" in overview
    assert len(overview["workflow_steps"]) == 10
    assert "local_dev_commands" in overview
    assert "branch_strategy" in overview
    assert "commit_conventions" in overview
    assert "pre_commit_checklist" in overview


def test_branch_strategy_and_commit_conventions():
    overview = get_daily_workflow_overview()
    branches = [b["branch"] for b in overview["branch_strategy"]]
    assert "main" in branches
    assert "feat/*" in branches
    assert "fix/*" in branches
    assert "docs/*" in branches

    prefixes = [c["prefix"] for c in overview["commit_conventions"]]
    assert "feat:" in prefixes
    assert "fix:" in prefixes
    assert "docs:" in prefixes
    assert "perf:" in prefixes
    assert "test:" in prefixes
    assert "chore:" in prefixes


def test_verify_pre_commit_status():
    # Pass all required
    pass_all = {
        "compiles": True,
        "tests_pass": True,
        "no_secrets": True,
        "linter_passes": True,
        "has_tests": True,
        "docs_updated": True,
    }
    res_pass = verify_pre_commit_status(pass_all)
    assert res_pass["is_ready_to_commit"] is True
    assert len(res_pass["missing_required"]) == 0

    # Fail some required
    fail_req = {
        "compiles": True,
        "tests_pass": False,
        "no_secrets": True,
        "linter_passes": False,
        "has_tests": True,
    }
    res_fail = verify_pre_commit_status(fail_req)
    assert res_fail["is_ready_to_commit"] is False
    assert len(res_fail["missing_required"]) == 2


def test_dev_workflow_api_endpoints():
    res_overview = client.get("/api/v1/dev/workflow/overview")
    assert res_overview.status_code == 200
    assert res_overview.json()["success"] is True

    res_check = client.get("/api/v1/dev/workflow/pre-commit-checklist")
    assert res_check.status_code == 200
    assert len(res_check.json()["checklist"]) == 6

    res_verify = client.post("/api/v1/dev/workflow/verify-pre-commit", json={
        "checks_completed": {
            "compiles": True,
            "tests_pass": True,
            "no_secrets": True,
            "linter_passes": True,
            "has_tests": True
        }
    })
    assert res_verify.status_code == 200
    assert res_verify.json()["is_ready_to_commit"] is True
