"""Development Workflow Service for MemeGPT.
Specification: 09_Development/Development_Workflow.md
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.development_workflow")

WORKFLOW_STEPS = [
    {"step": 1, "name": "Sync main", "command": "git pull origin main"},
    {"step": 2, "name": "Branch", "command": "git checkout -b feat/xyz"},
    {"step": 3, "name": "Start servers", "command": "npm run dev (frontend) & uvicorn --reload (backend)"},
    {"step": 4, "name": "Code & Tests", "command": "Write application code and matching unit tests"},
    {"step": 5, "name": "Test locally", "command": "pytest / npm test"},
    {"step": 6, "name": "Commit changes", "command": "git add . && git commit -m \"feat(scope): description\""},
    {"step": 7, "name": "Push branch", "command": "git push origin feat/xyz"},
    {"step": 8, "name": "Open PR", "command": "Open PR targeting develop / main"},
    {"step": 9, "name": "CI checks", "command": "Automated GitHub Actions lint + build + test"},
    {"step": 10, "name": "Merge & Deploy", "command": "Merge to main -> Auto-deploy to production"},
]

LOCAL_DEV_COMMANDS = {
    "terminal_1_backend": {
        "title": "Terminal 1: Backend",
        "commands": [
            "cd services/api",
            "pip install -r requirements.txt",
            "uvicorn app.main:app --reload --port 8000",
        ],
        "url": "http://localhost:8000",
    },
    "terminal_2_frontend": {
        "title": "Terminal 2: Frontend",
        "commands": [
            "cd apps/web",
            "npm install",
            "npm run dev",
        ],
        "url": "http://localhost:5173",
    },
    "terminal_3_services": {
        "title": "Terminal 3: Local Services (Optional)",
        "commands": [
            "docker-compose up -d  # Redis + Qdrant",
        ],
        "url": "redis://localhost:6379 & http://localhost:6333",
    },
}

BRANCH_STRATEGY = [
    {"branch": "main", "purpose": "Production-ready code", "deploys_to": "Auto-deploy to prod"},
    {"branch": "feat/*", "purpose": "New features", "deploys_to": "PR -> main / develop"},
    {"branch": "fix/*", "purpose": "Bug fixes", "deploys_to": "PR -> main / develop"},
    {"branch": "docs/*", "purpose": "Documentation updates", "deploys_to": "PR -> main / develop"},
]

COMMIT_CONVENTIONS = [
    {"prefix": "feat:", "description": "New feature implementation", "example": "feat: add suggestion chips to search"},
    {"prefix": "fix:", "description": "Bug fix", "example": "fix: handle empty query validation"},
    {"prefix": "docs:", "description": "Documentation changes", "example": "docs: update API Architecture docs"},
    {"prefix": "perf:", "description": "Performance improvement", "example": "perf: cache trending results for 5 minutes"},
    {"prefix": "test:", "description": "Adding or refactoring tests", "example": "test: add emotion detection unit tests"},
    {"prefix": "chore:", "description": "Tooling and dependency updates", "example": "chore: update dependencies"},
]

PRE_COMMIT_CHECKLIST = [
    {"id": "compiles", "label": "Code compiles without errors", "required": True},
    {"id": "tests_pass", "label": "Tests pass locally (pytest / npm test)", "required": True},
    {"id": "no_secrets", "label": "No hardcoded API keys or secrets", "required": True},
    {"id": "linter_passes", "label": "Linter passes (ruff for Python, ESLint for TypeScript)", "required": True},
    {"id": "has_tests", "label": "New features have tests", "required": True},
    {"id": "docs_updated", "label": "Documentation updated (if API changed)", "required": False},
]


def get_daily_workflow_overview() -> Dict[str, Any]:
    """Return full daily development workflow specification."""
    return {
        "workflow_steps": WORKFLOW_STEPS,
        "local_dev_commands": LOCAL_DEV_COMMANDS,
        "branch_strategy": BRANCH_STRATEGY,
        "commit_conventions": COMMIT_CONVENTIONS,
        "pre_commit_checklist": PRE_COMMIT_CHECKLIST,
    }


def get_pre_commit_checklist_items() -> List[Dict[str, Any]]:
    """Return list of pre-commit checklist requirements."""
    return PRE_COMMIT_CHECKLIST


def verify_pre_commit_status(checks_completed: Dict[str, bool]) -> Dict[str, Any]:
    """Verify if staged changes satisfy all required pre-commit checks."""
    missing_required = []
    for item in PRE_COMMIT_CHECKLIST:
        item_id = item["id"]
        if item.get("required") and not checks_completed.get(item_id, False):
            missing_required.append(item["label"])

    is_ready = len(missing_required) == 0
    return {
        "is_ready_to_commit": is_ready,
        "total_checks": len(PRE_COMMIT_CHECKLIST),
        "passed_checks": sum(1 for item in PRE_COMMIT_CHECKLIST if checks_completed.get(item["id"], False)),
        "missing_required": missing_required,
        "summary": "All required pre-commit checks passed" if is_ready else f"Missing {len(missing_required)} required pre-commit checks",
    }
