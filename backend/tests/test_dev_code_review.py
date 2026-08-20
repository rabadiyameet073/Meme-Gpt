"""Tests for Code Review Checklist from 09_Development/Code_Review.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.code_review_service import (
    get_code_review_checklist,
    evaluate_code_compliance,
)

client = TestClient(app)


def test_code_review_checklist_structure():
    checklist = get_code_review_checklist()
    assert checklist["total_categories"] == 6
    assert checklist["total_items"] >= 20

    categories = checklist["categories"]
    assert "functionality" in categories
    assert "code_quality" in categories
    assert "performance" in categories
    assert "security" in categories
    assert "testing" in categories
    assert "documentation" in categories


def test_code_compliance_scanner_violations():
    # Python code with raw print and hardcoded key
    dirty_python = """
import os

def test_func():
    api_key = "sk_live_1234567890abcdef"
    print("Testing something")
    return True
"""
    res_py = evaluate_code_compliance(dirty_python, filename="bad_service.py")
    assert res_py["is_compliant"] is False
    rules = [v["rule"] for v in res_py["violations"]]
    assert "qual_no_console" in rules
    assert "sec_no_hardcoded_keys" in rules

    # TypeScript code with console.log, any type, and dangerouslySetInnerHTML
    dirty_ts = """
export function BadComponent(props: any) {
  console.log("Rendering component");
  return <div dangerouslySetInnerHTML={{ __html: props.rawHtml }} />;
}
"""
    res_ts = evaluate_code_compliance(dirty_ts, filename="BadComponent.tsx")
    assert res_ts["is_compliant"] is False
    ts_violations = [v["rule"] for v in res_ts["violations"]]
    ts_warnings = [w["rule"] for w in res_ts["warnings"]]
    assert "qual_no_console" in ts_violations
    assert "sec_xss_prevented" in ts_violations
    assert "qual_no_any" in ts_warnings


def test_code_compliance_clean_code():
    clean_python = '''"""Clean module demonstrating proper code review standards."""

import logging

logger = logging.getLogger("memegpt.clean")

def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
'''
    res_clean = evaluate_code_compliance(clean_python, filename="clean_service.py")
    assert res_clean["is_compliant"] is True
    assert res_clean["score"] == 100
    assert len(res_clean["violations"]) == 0


def test_dev_code_review_api_endpoints():
    res_list = client.get("/api/v1/dev/code-review/checklist")
    assert res_list.status_code == 200
    assert res_list.json()["total_categories"] == 6

    res_audit = client.post("/api/v1/dev/code-review/audit", json={
        "code_snippet": "def clean():\n    return 42\n",
        "filename": "service.py"
    })
    assert res_audit.status_code == 200
    assert res_audit.json()["success"] is True
