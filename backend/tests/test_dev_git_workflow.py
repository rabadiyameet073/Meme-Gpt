"""Tests for Git Workflow from 09_Development/Git_Workflow.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.git_workflow_service import (
    get_git_branch_strategy,
    get_conventional_commit_types,
    get_pr_lifecycle_steps,
    get_pr_template_markdown,
    parse_and_validate_commit,
    validate_pr_submission,
)

client = TestClient(app)


def test_git_branch_strategy():
    strat = get_git_branch_strategy()
    branches = [b["branch"] for b in strat["branches"]]
    assert "main" in branches
    assert "develop" in branches
    assert "feature/*" in branches
    assert "fix/*" in branches
    assert "hotfix/*" in branches

    types = get_conventional_commit_types()
    assert len(types) == 9
    type_names = [t["type"] for t in types]
    assert "feat" in type_names
    assert "fix" in type_names
    assert "perf" in type_names
    assert "ci" in type_names


def test_parse_and_validate_commit():
    # Valid commits
    v1 = parse_and_validate_commit("feat(search): add emotion filtering")
    assert v1["is_valid"] is True
    assert v1["type"] == "feat"
    assert v1["scope"] == "search"

    v2 = parse_and_validate_commit("docs: update install steps")
    assert v2["is_valid"] is True
    assert v2["type"] == "docs"
    assert v2["scope"] is None

    # Invalid commit
    inv = parse_and_validate_commit("random unformatted commit")
    assert inv["is_valid"] is False
    assert inv["error"] is not None


def test_validate_pr_submission():
    valid_body = """
## What
Added suggestion chips to search bar.

## Why
Improves query discovery speed.

## How
Created dynamic time-aware chip component.

## Testing
- [x] Unit tests pass
- [x] Manual testing done
"""
    # Valid PR
    res_val = validate_pr_submission(
        branch_name="feature/search-chips",
        target_branch="develop",
        pr_body=valid_body,
    )
    assert res_val["is_valid"] is True

    # Invalid target
    res_bad_target = validate_pr_submission(
        branch_name="feature/search-chips",
        target_branch="main",
        pr_body=valid_body,
    )
    assert res_bad_target["is_valid"] is False

    # Incomplete body
    res_bad_body = validate_pr_submission(
        branch_name="feature/search-chips",
        target_branch="develop",
        pr_body="Just some quick changes",
    )
    assert res_bad_body["is_valid"] is False
    assert len(res_bad_body["missing_sections"]) > 0


def test_dev_git_api_endpoints():
    res_strat = client.get("/api/v1/dev/git/strategy")
    assert res_strat.status_code == 200
    assert len(res_strat.json()["branches"]) == 5

    res_tmpl = client.get("/api/v1/dev/git/pr-template")
    assert res_tmpl.status_code == 200
    assert "## What" in res_tmpl.json()["template"]

    res_comm = client.post("/api/v1/dev/git/validate-commit", json={
        "commit_message": "perf(search): add Redis caching"
    })
    assert res_comm.status_code == 200
    assert res_comm.json()["is_valid"] is True
