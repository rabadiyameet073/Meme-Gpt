"""Development Manifest Service for MemeGPT.
Specification: 09_Development/README.md
"""

import logging
from typing import Any, Dict, List

from app.services.code_review_service import get_code_review_checklist
from app.services.coding_standards_service import get_coding_standards_spec
from app.services.contributing_service import get_contributing_guide
from app.services.debugging_service import get_debugging_matrix
from app.services.development_workflow_service import get_daily_workflow_overview
from app.services.git_workflow_service import get_git_branch_strategy

logger = logging.getLogger("memegpt.services.dev_manifest")

SECTION_09_DOCUMENTS = [
    {
        "filename": "Code_Review.md",
        "title": "Code Review Checklist",
        "description": "Standard 6-pillar checklist for code quality, security, and performance",
        "path": "09_Development/Code_Review.md",
    },
    {
        "filename": "Coding_Standards.md",
        "title": "Coding Standards",
        "description": "Code style, ruff & ESLint configurations, naming conventions, and forbidden patterns",
        "path": "09_Development/Coding_Standards.md",
    },
    {
        "filename": "Contributing.md",
        "title": "Contributing Guide",
        "description": "Contribution guidelines, 9-step PR workflow, and code of conduct for external developers",
        "path": "09_Development/Contributing.md",
    },
    {
        "filename": "Debugging_Guide.md",
        "title": "Debugging Guide",
        "description": "Troubleshooting matrix across backend, frontend, AI pipeline, and database with auto-diagnosis",
        "path": "09_Development/Debugging_Guide.md",
    },
    {
        "filename": "Development_Workflow.md",
        "title": "Development Workflow",
        "description": "Daily development lifecycle, local multi-terminal setup, and pre-commit checks",
        "path": "09_Development/Development_Workflow.md",
    },
    {
        "filename": "Git_Workflow.md",
        "title": "Git Workflow",
        "description": "Branch topology, Conventional Commits parser, and PR template specification",
        "path": "09_Development/Git_Workflow.md",
    },
    {
        "filename": "README.md",
        "title": "Development Section Manifest",
        "description": "Overview and master index of all development guidelines and standards",
        "path": "09_Development/README.md",
    },
]


def get_development_section_manifest() -> Dict[str, Any]:
    """Return Section 09 Development master manifest."""
    return {
        "section_id": "09_Development",
        "title": "09 — Development",
        "description": "Development practices and standards for MemeGPT.",
        "total_documents": len(SECTION_09_DOCUMENTS),
        "documents": SECTION_09_DOCUMENTS,
        "previous_section": "08_Features",
        "next_section": "10_Testing",
    }


def verify_development_system_health() -> Dict[str, Any]:
    """Perform health checks across all Section 09 development services."""
    checks = {}

    try:
        review = get_code_review_checklist()
        checks["code_review"] = {"status": "healthy", "items": review.get("total_items", 0)}
    except Exception as e:
        checks["code_review"] = {"status": "unhealthy", "error": str(e)}

    try:
        standards = get_coding_standards_spec()
        checks["coding_standards"] = {"status": "healthy", "rules": len(standards.get("forbidden_patterns", []))}
    except Exception as e:
        checks["coding_standards"] = {"status": "unhealthy", "error": str(e)}

    try:
        contrib = get_contributing_guide()
        checks["contributing"] = {"status": "healthy", "steps": len(contrib.get("first_contribution_checklist", []))}
    except Exception as e:
        checks["contributing"] = {"status": "unhealthy", "error": str(e)}

    try:
        debug = get_debugging_matrix()
        checks["debugging"] = {"status": "healthy", "categories": len(debug.get("categories", []))}
    except Exception as e:
        checks["debugging"] = {"status": "unhealthy", "error": str(e)}

    try:
        wf = get_daily_workflow_overview()
        checks["workflow"] = {"status": "healthy", "steps": len(wf.get("workflow_steps", []))}
    except Exception as e:
        checks["workflow"] = {"status": "unhealthy", "error": str(e)}

    try:
        git_wf = get_git_branch_strategy()
        checks["git_workflow"] = {"status": "healthy", "branches": len(git_wf.get("branches", []))}
    except Exception as e:
        checks["git_workflow"] = {"status": "unhealthy", "error": str(e)}

    all_healthy = all(v.get("status") == "healthy" for v in checks.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "total_modules": len(checks),
    }
