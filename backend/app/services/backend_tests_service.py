"""Backend Tests Management Service for MemeGPT.
Specification: 10_Testing/Backend_Tests.md
"""

import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger("memegpt.services.backend_tests")

TEST_SUITE_STRUCTURE = {
    "directory": "backend/tests/",
    "files": [
        {"name": "conftest.py", "purpose": "Shared pytest fixtures and database mocks"},
        {"name": "test_main.py", "purpose": "API endpoint integration tests (/health, /search, 422, 404)"},
        {"name": "test_meme_matcher.py", "purpose": "Pipeline orchestrator tests"},
        {"name": "test_rule_engine.py", "purpose": "Scoring algorithm & rule engine tests"},
        {"name": "test_semantic_search.py", "purpose": "Embedding dimensions (384-dim) & L2 normalization tests"},
        {"name": "test_database.py", "purpose": "Database CRUD & session tests"},
        {"name": "test_config.py", "purpose": "Configuration loading tests"},
    ],
}

TEST_EXECUTION_COMMANDS = [
    {"command": "python -m pytest tests/ -v", "description": "Run all tests with verbose output"},
    {"command": "python -m pytest tests/ -v --cov=app", "description": "Run all tests with pytest-cov code coverage report"},
    {"command": "python -m pytest tests/test_main.py -v", "description": "Run single integration test file"},
    {"command": "python -m pytest tests/ -k \"test_search\"", "description": "Run tests matching pattern"},
    {"command": "python -m pytest tests/ --tb=short", "description": "Run tests with concise tracebacks on failure"},
]

COVERAGE_TARGETS = {
    "overall_target": ">80%",
    "modules": [
        {"module": "main.py", "target": ">90%", "target_value": 0.90},
        {"module": "meme_matcher.py", "target": ">80%", "target_value": 0.80},
        {"module": "rule_engine.py", "target": ">95%", "target_value": 0.95},
        {"module": "semantic_search.py", "target": ">80%", "target_value": 0.80},
        {"module": "database.py", "target": ">85%", "target_value": 0.85},
    ],
}


def get_backend_test_suite_structure() -> Dict[str, Any]:
    """Return test directory hierarchy and structure."""
    return TEST_SUITE_STRUCTURE


def get_test_execution_commands() -> List[Dict[str, str]]:
    """Return pytest command examples and flags."""
    return TEST_EXECUTION_COMMANDS


def get_coverage_targets() -> Dict[str, Any]:
    """Return module-level and overall coverage target benchmarks."""
    return COVERAGE_TARGETS


def get_backend_tests_inventory(tests_dir: str = "backend/tests") -> Dict[str, Any]:
    """Inspect backend/tests directory and list all active test files."""
    resolved_dir = tests_dir
    candidates = [
        tests_dir,
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tests"),
        "tests",
        "backend/tests",
        "../backend/tests",
    ]
    for c in candidates:
        if os.path.isdir(c):
            resolved_dir = c
            break

    test_files = []
    if os.path.exists(resolved_dir):
        for fname in sorted(os.listdir(resolved_dir)):
            if fname.startswith("test_") and fname.endswith(".py"):
                fpath = os.path.join(resolved_dir, fname)
                size = os.path.getsize(fpath)
                test_files.append({
                    "filename": fname,
                    "path": fpath.replace("\\", "/"),
                    "size_bytes": size,
                })

    return {
        "tests_directory": tests_dir,
        "total_test_files": len(test_files),
        "test_files": test_files,
    }

