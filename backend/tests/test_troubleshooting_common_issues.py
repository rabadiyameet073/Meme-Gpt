"""Tests for Common Issues & System Diagnostic Troubleshooting from 14_Troubleshooting/Common_Issues.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.troubleshooting_service import (
    get_diagnostic_flowchart,
    get_common_issues_catalog,
    get_issue_by_id,
    get_debugging_best_practices,
    diagnose_system_issue,
)

client = TestClient(app)


def test_diagnostic_flowchart():
    tree = get_diagnostic_flowchart()
    assert "root_step" in tree
    assert "question" in tree["root_step"]
    assert "curl /health" in tree["root_step"]["question"]
    assert "if_no" in tree["root_step"]
    assert "if_yes" in tree["root_step"]


def test_common_issues_catalog():
    res = get_common_issues_catalog()
    assert res["total_issues"] == 8
    assert len(res["issues"]) == 8
    ids = [i["id"] for i in res["issues"]]
    assert "ERR_MISSING_DEPENDENCY" in ids
    assert "ERR_CORS_BLOCKED" in ids
    assert "ERR_QDRANT_CONNECTION" in ids
    assert "ERR_REDIS_CONNECTION" in ids
    assert "ISSUE_ZERO_SEARCH_RESULTS" in ids
    assert "ISSUE_SLOW_SEARCH" in ids
    assert "ISSUE_FRONTEND_BUILD_FAILURE" in ids
    assert "ISSUE_RAILWAY_DEPLOY_FAILURE" in ids


def test_get_issue_by_id():
    issue = get_issue_by_id("ERR_CORS_BLOCKED")
    assert issue is not None
    assert issue["id"] == "ERR_CORS_BLOCKED"
    assert "ALLOWED_ORIGINS" in issue["fix_command"]

    # Case insensitive
    issue_lower = get_issue_by_id("issue_zero_search_results")
    assert issue_lower is not None
    assert issue_lower["id"] == "ISSUE_ZERO_SEARCH_RESULTS"
    assert len(issue_lower["troubleshooting_steps"]) == 5

    # Non-existent
    assert get_issue_by_id("NON_EXISTENT_ISSUE") is None


def test_debugging_best_practices():
    res = get_debugging_best_practices()
    assert res["total_practices"] == 5
    titles = [p["title"] for p in res["practices"]]
    assert "Check /health first" in titles
    assert "Read the error message" in titles
    assert "Check .env file" in titles
    assert "Test one service at a time" in titles
    assert "Check logs" in titles


def test_diagnose_system_issue():
    # Nominal case
    nominal = diagnose_system_issue(
        health_status_200=True,
        search_results_count=10,
        qdrant_connected=True,
        redis_connected=True,
        latency_seconds=1.2,
    )
    assert nominal["status"] == "ALL_SYSTEMS_OPERATIONAL"
    assert nominal["healthy"] is True
    assert nominal["detected_issues_count"] == 0

    # Backend down
    down = diagnose_system_issue(health_status_200=False)
    assert down["healthy"] is False
    assert any(i["issue_id"] == "ERR_BACKEND_DOWN" for i in down["diagnosed_issues"])

    # Qdrant down
    qdrant_down = diagnose_system_issue(qdrant_connected=False)
    assert any(i["issue_id"] == "ERR_QDRANT_CONNECTION" for i in qdrant_down["diagnosed_issues"])

    # Zero search results
    zero_results = diagnose_system_issue(
        health_status_200=True,
        search_results_count=0,
        qdrant_connected=True,
    )
    assert any(i["issue_id"] == "ISSUE_ZERO_SEARCH_RESULTS" for i in zero_results["diagnosed_issues"])

    # High latency
    slow = diagnose_system_issue(latency_seconds=4.5)
    assert any(i["issue_id"] == "ISSUE_SLOW_SEARCH" for i in slow["diagnosed_issues"])


def test_troubleshooting_api_endpoints():
    res_flow = client.get("/api/v1/troubleshooting/flowchart")
    assert res_flow.status_code == 200
    assert "root_step" in res_flow.json()

    res_issues = client.get("/api/v1/troubleshooting/issues")
    assert res_issues.status_code == 200
    assert res_issues.json()["total_issues"] == 8

    res_single = client.get("/api/v1/troubleshooting/issues/ERR_MISSING_DEPENDENCY")
    assert res_single.status_code == 200
    assert res_single.json()["issue"]["id"] == "ERR_MISSING_DEPENDENCY"

    res_prac = client.get("/api/v1/troubleshooting/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 5

    res_diag = client.post(
        "/api/v1/troubleshooting/diagnose",
        json={
            "health_status_200": True,
            "search_results_count": 0,
            "qdrant_connected": True,
            "redis_connected": True,
            "latency_seconds": 1.2,
        },
    )
    assert res_diag.status_code == 200
    assert res_diag.json()["healthy"] is False

    res_404 = client.get("/api/v1/troubleshooting/issues/NON_EXISTENT")
    assert res_404.status_code == 404
