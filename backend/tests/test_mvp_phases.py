"""Tests for MVP Phases & Sprint Planning from 13_Project_Management/MVP_Phases.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.mvp_phases_service import (
    get_all_sprints,
    get_sprint_by_id,
    get_definition_of_done,
    evaluate_dod_readiness,
    get_mvp_completion_summary,
)

client = TestClient(app)


def test_get_all_sprints():
    res = get_all_sprints()
    assert res["total_sprints"] == 4
    assert res["total_weeks"] == 8
    assert res["total_tasks"] == 30
    assert len(res["sprints"]) == 4


def test_get_sprint_by_id():
    # Sprint 1
    s1 = get_sprint_by_id(1)
    assert s1 is not None
    assert s1["sprint_id"] == 1
    assert s1["name"] == "Sprint 1: Backend Foundation"
    assert s1["total_tasks"] == 8

    # Sprint 2
    s2 = get_sprint_by_id(2)
    assert s2 is not None
    assert s2["sprint_id"] == 2
    assert s2["name"] == "Sprint 2: AI Integration"
    assert s2["total_tasks"] == 6

    # Sprint 3
    s3 = get_sprint_by_id(3)
    assert s3 is not None
    assert s3["sprint_id"] == 3
    assert s3["name"] == "Sprint 3: Frontend + Deploy"
    assert s3["total_tasks"] == 8

    # Sprint 4
    s4 = get_sprint_by_id(4)
    assert s4 is not None
    assert s4["sprint_id"] == 4
    assert s4["name"] == "Sprint 4: Polish + Feedback"
    assert s4["total_tasks"] == 8

    # Invalid sprint
    assert get_sprint_by_id(5) is None


def test_definition_of_done():
    dod = get_definition_of_done()
    assert dod["total_criteria"] == 6
    ids = [c["id"] for c in dod["criteria"]]
    assert "merged_develop" in ids
    assert "tests_pass" in ids
    assert "no_critical_bugs" in ids
    assert "code_reviewed" in ids
    assert "documentation_updated" in ids
    assert "staging_verified" in ids


def test_evaluate_dod_readiness():
    # Fully satisfied
    full_checks = {
        "merged_develop": True,
        "tests_pass": True,
        "no_critical_bugs": True,
        "code_reviewed": True,
        "documentation_updated": True,
        "staging_verified": True,
    }
    eval_full = evaluate_dod_readiness(full_checks)
    assert eval_full["is_done"] is True
    assert eval_full["status"] == "APPROVED_FOR_RELEASE"
    assert eval_full["passed_count"] == 6
    assert eval_full["missing_count"] == 0

    # Incomplete
    partial_checks = {
        "merged_develop": True,
        "tests_pass": False,
        "no_critical_bugs": True,
        "code_reviewed": False,
        "documentation_updated": True,
        "staging_verified": False,
    }
    eval_partial = evaluate_dod_readiness(partial_checks)
    assert eval_partial["is_done"] is False
    assert eval_partial["status"] == "INCOMPLETE_DOD"
    assert eval_partial["passed_count"] == 3
    assert eval_partial["missing_count"] == 3


def test_get_mvp_completion_summary():
    summary = get_mvp_completion_summary()
    assert summary["project"] == "MemeGPT MVP"
    assert summary["overall_status"] == "MVP_COMPLETE"
    assert summary["total_tasks"] == 30
    assert "Backend" in summary["owners_breakdown"]
    assert "ML" in summary["owners_breakdown"]
    assert "Frontend" in summary["owners_breakdown"]
    assert len(summary["milestones"]) == 4


def test_project_management_api_endpoints():
    res_sprints = client.get("/api/v1/project-management/sprints")
    assert res_sprints.status_code == 200
    assert res_sprints.json()["total_sprints"] == 4

    res_s1 = client.get("/api/v1/project-management/sprints/1")
    assert res_s1.status_code == 200
    assert res_s1.json()["sprint"]["name"] == "Sprint 1: Backend Foundation"

    res_dod = client.get("/api/v1/project-management/dod")
    assert res_dod.status_code == 200
    assert res_dod.json()["total_criteria"] == 6

    res_eval = client.post(
        "/api/v1/project-management/dod/evaluate",
        json={
            "merged_develop": True,
            "tests_pass": True,
            "no_critical_bugs": True,
            "code_reviewed": True,
            "documentation_updated": True,
            "staging_verified": True,
        },
    )
    assert res_eval.status_code == 200
    assert res_eval.json()["status"] == "APPROVED_FOR_RELEASE"

    res_summary = client.get("/api/v1/project-management/mvp-summary")
    assert res_summary.status_code == 200
    assert res_summary.json()["overall_status"] == "MVP_COMPLETE"
