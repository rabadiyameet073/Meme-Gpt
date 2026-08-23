"""Frontend Tests Management Service for MemeGPT.
Specification: 10_Testing/Frontend_Tests.md
"""

import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger("memegpt.services.frontend_tests")

FRONTEND_TEST_STACK = [
    {
        "tool": "vitest",
        "purpose": "Test runner (fast, Vite-native, ESM support)",
        "config_file": "frontend/vitest.config.ts",
    },
    {
        "tool": "React Testing Library",
        "purpose": "Component rendering, DOM queries, and user-centric assertions",
        "packages": ["@testing-library/react", "@testing-library/jest-dom"],
    },
    {
        "tool": "jsdom",
        "purpose": "Browser environment simulation for headless DOM testing",
        "environment": "jsdom",
    },
    {
        "tool": "MSW",
        "purpose": "API mocking (Mock Service Worker) for network-isolated tests",
        "package": "msw",
    },
]

FRONTEND_TEST_COMMANDS = [
    {"command": "npm run test", "description": "Run all frontend tests once via Vitest"},
    {"command": "npm run test:watch", "description": "Run frontend tests in interactive watch mode"},
    {"command": "npm run test:coverage", "description": "Run frontend tests with code coverage report"},
]

FRONTEND_COVERAGE_TARGETS = {
    "overall_target": ">70%",
    "components": [
        {"component": "SearchInput", "target": ">90%", "target_value": 0.90},
        {"component": "MemeCard", "target": ">85%", "target_value": 0.85},
        {"component": "ResultsGrid", "target": ">80%", "target_value": 0.80},
        {"component": "Custom hooks", "target": ">85%", "target_value": 0.85},
        {"component": "API client", "target": ">75%", "target_value": 0.75},
    ],
}


def get_frontend_test_stack() -> Dict[str, Any]:
    """Return frontend testing technology stack and tools."""
    return {
        "total_tools": len(FRONTEND_TEST_STACK),
        "stack": FRONTEND_TEST_STACK,
    }


def get_frontend_test_commands() -> List[Dict[str, str]]:
    """Return npm scripts for frontend testing."""
    return FRONTEND_TEST_COMMANDS


def get_frontend_coverage_targets() -> Dict[str, Any]:
    """Return frontend coverage targets per component/layer."""
    return FRONTEND_COVERAGE_TARGETS


def get_frontend_test_inventory(tests_dir: str = "frontend/src/tests") -> Dict[str, Any]:
    """Discover active test files in frontend test directory."""
    test_files = []
    if os.path.exists(tests_dir):
        for fname in sorted(os.listdir(tests_dir)):
            if fname.endswith(".test.ts") or fname.endswith(".test.tsx") or fname.endswith(".spec.ts"):
                fpath = os.path.join(tests_dir, fname)
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
