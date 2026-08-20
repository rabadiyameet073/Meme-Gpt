"""Code Review Service for MemeGPT.
Specification: 09_Development/Code_Review.md
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.code_review")

CODE_REVIEW_CHECKLIST = {
    "functionality": {
        "title": "Functionality",
        "items": [
            {"id": "func_works", "description": "Feature works as described in the PR", "required": True},
            {"id": "func_edge_cases", "description": "Edge cases handled (empty input, max length, special chars, unicode)", "required": True},
            {"id": "func_error_states", "description": "Error states display user-friendly messages", "required": True},
            {"id": "func_loading_states", "description": "Loading states implemented", "required": True},
            {"id": "func_no_regressions", "description": "No regressions in existing features", "required": True},
        ],
    },
    "code_quality": {
        "title": "Code Quality",
        "items": [
            {"id": "qual_standards", "description": "Follows coding standards (PEP 8 / ESLint)", "required": True},
            {"id": "qual_types", "description": "Type hints (Python) / TypeScript types used properly", "required": True},
            {"id": "qual_no_any", "description": "No 'any' types in TypeScript", "required": True},
            {"id": "qual_no_hardcoded", "description": "No hardcoded values — use config/env vars", "required": True},
            {"id": "qual_no_console", "description": "No console.log / print in production code", "required": True},
            {"id": "qual_single_resp", "description": "Functions are small and have single responsibility", "required": True},
            {"id": "qual_naming", "description": "Meaningful variable and function names", "required": True},
            {"id": "qual_comments", "description": "Comments explain *why*, not *what*", "required": False},
        ],
    },
    "performance": {
        "title": "Performance",
        "items": [
            {"id": "perf_no_nplus1", "description": "No N+1 database queries", "required": True},
            {"id": "perf_async_io", "description": "Async operations used for I/O (not blocking event loop)", "required": True},
            {"id": "perf_no_rerenders", "description": "No unnecessary re-renders in React (memo, useCallback)", "required": False},
            {"id": "perf_lazy_images", "description": "Images are lazy-loaded below the fold", "required": True},
            {"id": "perf_no_blocking_routes", "description": "No large synchronous computations in route handlers", "required": True},
        ],
    },
    "security": {
        "title": "Security",
        "items": [
            {"id": "sec_input_sanitization", "description": "User input is sanitized/validated", "required": True},
            {"id": "sec_no_pii_logs", "description": "No PII in log messages", "required": True},
            {"id": "sec_no_hardcoded_keys", "description": "API keys not hardcoded", "required": True},
            {"id": "sec_sqli_prevented", "description": "SQL injection prevented (parameterized queries)", "required": True},
            {"id": "sec_xss_prevented", "description": "XSS prevented (no dangerouslySetInnerHTML without sanitization)", "required": True},
            {"id": "sec_rate_limiting", "description": "Rate limiting applied to new endpoints", "required": True},
        ],
    },
    "testing": {
        "title": "Testing",
        "items": [
            {"id": "test_unit", "description": "Unit tests for new business logic", "required": True},
            {"id": "test_integration", "description": "Integration test for new API endpoints", "required": True},
            {"id": "test_edge_cases", "description": "Edge case tests included", "required": True},
            {"id": "test_regression_pass", "description": "All existing tests still pass", "required": True},
        ],
    },
    "documentation": {
        "title": "Documentation",
        "items": [
            {"id": "doc_docstrings", "description": "Docstrings on new public functions", "required": True},
            {"id": "doc_readme", "description": "README updated if setup steps changed", "required": False},
            {"id": "doc_api_docs", "description": "API docs updated if endpoints changed", "required": True},
            {"id": "doc_env_vars", "description": "Env vars documented if new ones added", "required": True},
        ],
    },
}


def get_code_review_checklist() -> Dict[str, Any]:
    """Return the complete 6-pillar code review checklist."""
    total_items = sum(len(cat["items"]) for cat in CODE_REVIEW_CHECKLIST.values())
    return {
        "total_categories": len(CODE_REVIEW_CHECKLIST),
        "total_items": total_items,
        "categories": CODE_REVIEW_CHECKLIST,
    }


def evaluate_code_compliance(code_snippet: str, filename: str = "code.py") -> Dict[str, Any]:
    """Perform static automated check for common code review checklist violations."""
    violations = []
    warnings = []
    passed_rules = []

    is_python = filename.endswith(".py")
    is_ts = filename.endswith(".ts") or filename.endswith(".tsx")

    lines = code_snippet.splitlines()

    # Rule: No raw print / console.log
    for i, line in enumerate(lines, 1):
        if is_python and re.search(r"^\s*print\s*\(", line):
            violations.append({"line": i, "rule": "qual_no_console", "message": "Avoid raw print() in production code; use logger"})
        if is_ts and re.search(r"console\.log\s*\(", line):
            violations.append({"line": i, "rule": "qual_no_console", "message": "Avoid console.log() in production code"})

    # Rule: No hardcoded secrets
    secret_pattern = re.compile(r"""(api_key|secret|password|auth_token)\s*=\s*['"][a-zA-Z0-9_-]{12,}['"]""", re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if secret_pattern.search(line):
            violations.append({"line": i, "rule": "sec_no_hardcoded_keys", "message": "Possible hardcoded API key/secret detected. Use environment variables."})

    # Rule: No any in TypeScript
    if is_ts:
        for i, line in enumerate(lines, 1):
            if re.search(r":\s*any\b", line) and not line.strip().startswith("//"):
                warnings.append({"line": i, "rule": "qual_no_any", "message": "Avoid ': any' type annotations in TypeScript"})

    # Rule: Prevent dangerouslySetInnerHTML
    if is_ts:
        for i, line in enumerate(lines, 1):
            if "dangerouslySetInnerHTML" in line:
                violations.append({"line": i, "rule": "sec_xss_prevented", "message": "dangerouslySetInnerHTML detected. Ensure strict sanitization (DOMPurify)."})

    # Rule: Docstrings on Python functions
    if is_python:
        def_count = len(re.findall(r"^\s*def\s+[a-zA-Z0-9_]+\s*\(", code_snippet, re.MULTILINE))
        docstring_count = len(re.findall(r'"""[\s\S]*?"""', code_snippet))
        if def_count > 0 and docstring_count == 0:
            warnings.append({"line": 1, "rule": "doc_docstrings", "message": "Missing docstrings on public functions"})

    total_issues = len(violations) + len(warnings)
    is_compliant = len(violations) == 0
    score = max(0, 100 - len(violations) * 20 - len(warnings) * 5)

    return {
        "filename": filename,
        "is_compliant": is_compliant,
        "score": score,
        "violations": violations,
        "warnings": warnings,
        "summary": "Passed all critical checks" if is_compliant else f"Found {len(violations)} violations and {len(warnings)} warnings",
    }
