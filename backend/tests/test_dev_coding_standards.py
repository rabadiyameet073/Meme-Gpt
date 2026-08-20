"""Tests for Coding Standards from 09_Development/Coding_Standards.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.coding_standards_service import (
    get_coding_standards_spec,
    get_linter_configurations,
    validate_source_code_standards,
)

client = TestClient(app)


def test_coding_standards_spec():
    spec = get_coding_standards_spec()
    assert "python_standards" in spec
    assert "typescript_standards" in spec
    assert "forbidden_patterns" in spec

    py = spec["python_standards"]
    assert py["linter"] == "ruff"
    assert "snake_case" in py["naming"]["files"]

    ts = spec["typescript_standards"]
    assert "PascalCase.tsx" in ts["naming"]["component_files"]

    forbid = spec["forbidden_patterns"]
    forbid_ids = [p["id"] for p in forbid]
    assert "forbid_eval_exec" in forbid_ids
    assert "forbid_wildcard_import" in forbid_ids
    assert "forbid_bare_except" in forbid_ids
    assert "forbid_ts_any" in forbid_ids


def test_linter_configurations():
    linters = get_linter_configurations()
    assert "ruff" in linters
    assert linters["ruff"]["line-length"] == 100
    assert "UP" in linters["ruff"]["select"]
    assert "eslint" in linters


def test_forbidden_patterns_validation_python():
    # Code with eval, wildcard import, and bare except
    bad_py = """
from app.services import *

def dangerous():
    eval("1 + 1")
    try:
        call()
    except:
        pass
"""
    res = validate_source_code_standards(bad_py, filename="bad.py")
    assert res["is_valid"] is False
    pattern_ids = [v["pattern_id"] for v in res["violations"]]
    assert "forbid_wildcard_import" in pattern_ids
    assert "forbid_eval_exec" in pattern_ids
    assert "forbid_bare_except" in pattern_ids


def test_forbidden_patterns_validation_typescript():
    # TS with any type
    bad_ts = """
export interface SearchProps {
    data: any;
}
"""
    res = validate_source_code_standards(bad_ts, filename="Search.tsx")
    assert res["is_valid"] is False
    pattern_ids = [v["pattern_id"] for v in res["violations"]]
    assert "forbid_ts_any" in pattern_ids


def test_clean_code_validation():
    clean_code = """
async def search_memes(query_text: str) -> list[dict]:
    try:
        return await do_search(query_text)
    except TimeoutError as e:
        logger.warning(f"Timeout: {e}")
        return []
"""
    res = validate_source_code_standards(clean_code, filename="service.py")
    assert res["is_valid"] is True
    assert res["total_violations"] == 0


def test_dev_coding_standards_api_endpoints():
    res_spec = client.get("/api/v1/dev/coding-standards/spec")
    assert res_spec.status_code == 200
    assert res_spec.json()["success"] is True

    res_linters = client.get("/api/v1/dev/coding-standards/linters")
    assert res_linters.status_code == 200
    assert res_linters.json()["linters"]["ruff"]["line-length"] == 100

    res_validate = client.post("/api/v1/dev/coding-standards/validate", json={
        "code_snippet": "from os import *",
        "filename": "test.py"
    })
    assert res_validate.status_code == 200
    assert res_validate.json()["is_valid"] is False
