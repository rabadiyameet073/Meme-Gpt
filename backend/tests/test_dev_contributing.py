"""Tests for Contributing Guide from 09_Development/Contributing.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.contributing_service import (
    get_contributing_guide,
    validate_contribution_pr,
)

client = TestClient(app)


def test_contributing_guide_structure():
    guide = get_contributing_guide()
    assert len(guide["ways_to_contribute"]) == 6
    assert len(guide["first_contribution_checklist"]) == 9
    assert len(guide["good_first_issues"]) == 5
    assert len(guide["code_of_conduct"]) == 4
    assert guide["target_branch"] == "develop"


def test_validate_pr_valid():
    res = validate_contribution_pr(
        branch_name="feat/new-category-tags",
        commit_message="feat(search): support custom collection tags",
        target_branch="develop",
    )
    assert res["is_valid"] is True
    assert len(res["errors"]) == 0


def test_validate_pr_invalid():
    res = validate_contribution_pr(
        branch_name="my_random_branch",
        commit_message="updated files and stuff",
        target_branch="main",
    )
    assert res["is_valid"] is False
    assert len(res["errors"]) == 3  # Invalid branch prefix, non-conventional commit, targeting main instead of develop


def test_dev_contributing_api_endpoints():
    res_guide = client.get("/api/v1/dev/contributing/guide")
    assert res_guide.status_code == 200
    assert res_guide.json()["success"] is True

    res_val = client.post("/api/v1/dev/contributing/validate-pr", json={
        "branch_name": "fix/toast-animation",
        "commit_message": "fix(ui): smooth toast fadeout transition",
        "target_branch": "develop"
    })
    assert res_val.status_code == 200
    assert res_val.json()["is_valid"] is True
