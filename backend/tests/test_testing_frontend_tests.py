"""Tests for Frontend Tests Management from 10_Testing/Frontend_Tests.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.frontend_tests_service import (
    get_frontend_test_stack,
    get_frontend_test_commands,
    get_frontend_coverage_targets,
    get_frontend_test_inventory,
)

client = TestClient(app)


def test_frontend_test_stack():
    stack = get_frontend_test_stack()
    assert stack["total_tools"] == 4
    tool_names = [t["tool"] for t in stack["stack"]]
    assert "vitest" in tool_names
    assert "React Testing Library" in tool_names
    assert "jsdom" in tool_names
    assert "MSW" in tool_names


def test_frontend_test_commands():
    cmds = get_frontend_test_commands()
    assert len(cmds) == 3
    cmd_strs = [c["command"] for c in cmds]
    assert "npm run test" in cmd_strs
    assert "npm run test:watch" in cmd_strs
    assert "npm run test:coverage" in cmd_strs


def test_frontend_coverage_targets():
    cov = get_frontend_coverage_targets()
    assert cov["overall_target"] == ">70%"
    assert len(cov["components"]) == 5
    comp_map = {c["component"]: c["target"] for c in cov["components"]}
    assert comp_map["SearchInput"] == ">90%"
    assert comp_map["MemeCard"] == ">85%"
    assert comp_map["ResultsGrid"] == ">80%"


def test_frontend_test_inventory():
    inv = get_frontend_test_inventory(tests_dir="frontend/src/tests")
    assert inv["total_test_files"] >= 2
    fnames = [f["filename"] for f in inv["test_files"]]
    assert "SearchInput.test.tsx" in fnames
    assert "useMemeSearch.test.ts" in fnames


def test_frontend_testing_api_endpoints():
    res_stack = client.get("/api/v1/test/frontend/stack")
    assert res_stack.status_code == 200
    assert res_stack.json()["total_tools"] == 4

    res_cmd = client.get("/api/v1/test/frontend/commands")
    assert res_cmd.status_code == 200
    assert len(res_cmd.json()["commands"]) == 3

    res_cov = client.get("/api/v1/test/frontend/coverage-targets")
    assert res_cov.status_code == 200
    assert res_cov.json()["overall_target"] == ">70%"

    res_inv = client.get("/api/v1/test/frontend/inventory")
    assert res_inv.status_code == 200
    assert res_inv.json()["total_test_files"] >= 2
