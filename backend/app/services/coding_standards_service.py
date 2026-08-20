"""Coding Standards Service for MemeGPT.
Specification: 09_Development/Coding_Standards.md
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.coding_standards")

FORBIDDEN_PATTERNS = [
    {
        "id": "forbid_eval_exec",
        "name": "eval() / exec()",
        "risk": "Security risk (remote code execution)",
        "alternative": "Use json.loads() or ast.literal_eval()",
    },
    {
        "id": "forbid_wildcard_import",
        "name": "import *",
        "risk": "Namespace pollution & shadowing",
        "alternative": "Use explicit named imports",
    },
    {
        "id": "forbid_bare_except",
        "name": "bare except:",
        "risk": "Catches KeyboardInterrupt, SystemExit, and hides bugs",
        "alternative": "Catch specific exceptions e.g. except (httpx.TimeoutException, json.JSONDecodeError):",
    },
    {
        "id": "forbid_console_log",
        "name": "console.log / print in production",
        "risk": "Noise, leaking data in production output",
        "alternative": "Use structured logger",
    },
    {
        "id": "forbid_hardcoded_secrets",
        "name": "Hardcoded secrets",
        "risk": "Security credential leak",
        "alternative": "Use environment variables / os.getenv()",
    },
    {
        "id": "forbid_ts_any",
        "name": "any type in TypeScript",
        "risk": "Defeats type safety",
        "alternative": "Use proper TypeScript interfaces and generics",
    },
    {
        "id": "forbid_raw_sql",
        "name": "Raw unparameterized SQL",
        "risk": "SQL injection vulnerability",
        "alternative": "Use SQLAlchemy ORM / parameterized queries",
    },
]

RUFF_CONFIG = {
    "target-version": "py311",
    "line-length": 100,
    "select": ["E", "W", "F", "I", "N", "UP"],
    "isort": {
        "known-first-party": ["app"],
    },
}

ESLINT_CONFIG = {
    "extends": ["next/core-web-vitals", "next/typescript"],
    "rules": {
        "no-console": "warn",
        "prefer-const": "error",
        "@typescript-eslint/no-unused-vars": "error",
    },
}


def get_coding_standards_spec() -> Dict[str, Any]:
    """Return coding standards naming conventions and required patterns."""
    return {
        "python_standards": {
            "linter": "ruff",
            "naming": {
                "files": "snake_case.py (e.g. recommendation.py)",
                "functions": "snake_case (e.g. recommend_memes())",
                "classes": "PascalCase (e.g. SearchRequest)",
                "constants": "UPPER_SNAKE (e.g. MAX_QUERY_LENGTH)",
                "variables": "snake_case (e.g. query_embedding)",
                "private": "_prefix (e.g. _default_intent())",
            },
            "required_patterns": [
                "Always use type hints",
                "Always use async/await for I/O",
                "Always use Pydantic models for request/response",
                "Catch specific exceptions (never bare except)",
            ],
        },
        "typescript_standards": {
            "linter": "ESLint + Next.js config",
            "naming": {
                "component_files": "PascalCase.tsx (e.g. MemeCard.tsx)",
                "util_files": "camelCase.ts (e.g. formatScore.ts)",
                "components": "PascalCase (e.g. SearchInput)",
                "hooks": "useCamelCase (e.g. useSearch)",
                "functions": "camelCase (e.g. formatScore())",
                "constants": "UPPER_SNAKE (e.g. API_BASE_URL)",
                "interfaces": "PascalCase (e.g. MemeResult)",
            },
            "required_patterns": [
                "Always use TypeScript interfaces",
                "Always use 'use client' for interactive components",
                "Always use const for components",
                "Never use 'any'",
            ],
        },
        "forbidden_patterns": FORBIDDEN_PATTERNS,
    }


def get_linter_configurations() -> Dict[str, Any]:
    """Return linter configuration objects for ruff and ESLint."""
    return {
        "ruff": RUFF_CONFIG,
        "eslint": ESLINT_CONFIG,
    }


def validate_source_code_standards(code_snippet: str, filename: str = "code.py") -> Dict[str, Any]:
    """Validate source code against forbidden patterns and required conventions."""
    violations = []
    is_python = filename.endswith(".py")
    is_ts = filename.endswith(".ts") or filename.endswith(".tsx")

    lines = code_snippet.splitlines()

    for i, line in enumerate(lines, 1):
        # eval / exec
        if re.search(r"\b(eval|exec)\s*\(", line) and not line.strip().startswith("#"):
            violations.append({
                "line": i,
                "pattern_id": "forbid_eval_exec",
                "message": "Forbidden eval() or exec() call. Use json.loads() or ast.literal_eval().",
            })

        # Wildcard import (from X import *)
        if is_python and re.search(r"^\s*from\s+[\w\.]+\s+import\s+\*", line):
            violations.append({
                "line": i,
                "pattern_id": "forbid_wildcard_import",
                "message": "Forbidden wildcard import ('from X import *'). Use explicit imports.",
            })

        # Bare except (except:)
        if is_python and re.search(r"^\s*except\s*:\s*$", line):
            violations.append({
                "line": i,
                "pattern_id": "forbid_bare_except",
                "message": "Forbidden bare 'except:'. Catch specific exceptions or 'except Exception:'.",
            })

        # Hardcoded secrets
        if re.search(r"""(api_key|secret|password|auth_token)\s*=\s*['"][a-zA-Z0-9_-]{12,}['"]""", line, re.IGNORECASE):
            violations.append({
                "line": i,
                "pattern_id": "forbid_hardcoded_secrets",
                "message": "Forbidden hardcoded secret. Use environment variables.",
            })

        # TypeScript any
        if is_ts and re.search(r":\s*any\b", line) and not line.strip().startswith("//"):
            violations.append({
                "line": i,
                "pattern_id": "forbid_ts_any",
                "message": "Forbidden ': any' type in TypeScript. Use proper interfaces.",
            })

        # Raw string SQL concatenation (SELECT * FROM ... + var)
        if re.search(r"""(SELECT|INSERT|UPDATE|DELETE)\s+.*['"]\s*\+\s*\w+""", line, re.IGNORECASE):
            violations.append({
                "line": i,
                "pattern_id": "forbid_raw_sql",
                "message": "Forbidden raw SQL string concatenation. Use ORM or parameterized queries.",
            })

    is_valid = len(violations) == 0
    return {
        "filename": filename,
        "is_valid": is_valid,
        "total_violations": len(violations),
        "violations": violations,
    }
