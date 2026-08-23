"""Tests for Backend Tests Management from 10_Testing/Backend_Tests.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.backend_tests_service import (
    get_backend_test_suite_structure,
    get_test_execution_commands,
    get_coverage_targets,
    get_backend_tests_inventory,
)

client = TestClient(app)


def test_backend_test_suite_structure():
    struct = get_backend_test_suite_structure()
    assert struct["directory"] == "backend/tests/"
    assert len(struct["files"]) >= 7

    names = [f["name"] for f in struct["files"]]
    assert "conftest.py" in names
    assert "test_main.py" in names
    assert "test_meme_matcher.py" in names
    assert "test_rule_engine.py" in names
    assert "test_semantic_search.py" in names
    assert "test_database.py" in names
    assert "test_config.py" in names


def test_test_execution_commands():
    cmds = get_test_execution_commands()
    assert len(cmds) == 5
    cmd_strings = [c["command"] for c in cmds]
    assert any("--cov=app" in c for c in cmd_strings)
    assert any("-k" in c for c in cmd_strings)


def test_coverage_targets():
    cov = get_coverage_targets()
    assert cov["overall_target"] == ">80%"
    assert len(cov["modules"]) == 5
    mod_map = {m["module"]: m["target"] for m in cov["modules"]}
    assert mod_map["main.py"] == ">90%"
    assert mod_map["rule_engine.py"] == ">95%"


def test_backend_tests_inventory():
    inv = get_backend_tests_inventory(tests_dir="backend/tests")
    assert inv["total_test_files"] > 10
    fnames = [f["filename"] for f in inv["test_files"]]
    assert "test_main.py" in fnames
    assert "test_rule_engine.py" in fnames
    assert "test_semantic_search.py" in fnames
    assert "test_database.py" in fnames
    assert "test_config.py" in fnames


def test_backend_testing_api_endpoints():
    res_struct = client.get("/api/v1/test/backend/structure")
    assert res_struct.status_code == 200
    assert len(res_struct.json()["files"]) >= 7

    res_cmd = client.get("/api/v1/test/backend/commands")
    assert res_cmd.status_code == 200
    assert len(res_cmd.json()["commands"]) == 5

    res_cov = client.get("/api/v1/test/backend/coverage-targets")
    assert res_cov.status_code == 200
    assert res_cov.json()["overall_target"] == ">80%"

    res_inv = client.get("/api/v1/test/backend/inventory")
    assert res_inv.status_code == 200
    assert res_inv.json()["total_test_files"] > 10
