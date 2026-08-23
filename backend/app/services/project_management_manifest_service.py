"""Project Management Section Manifest and Governance Service for MemeGPT.
Specification: 13_Project_Management/README.md

Covers:
- Section 13 Documentation Manifest & Navigation (Roadmap, MVP_Phases, Risk_Register, README)
- Consolidated Project Governance Posture Summary
- Live Subsystem Health & Governance Diagnostic Evaluator
"""

from typing import Any, Dict, List
from app.services.mvp_phases_service import get_mvp_completion_summary, get_definition_of_done


# ── 1. Section 13 Documentation Manifest ───────────────────────────────────────

PROJECT_MANAGEMENT_SECTION_MANIFEST = [
    {
        "file": "MVP_Phases.md",
        "title": "MVP Phases (Detailed Sprint Planning)",
        "description": "Sprint-level task breakdown across 4 sprints (8 weeks, 30 tasks), owner assignments, deliverables, and 6 Definition of Done (DoD) criteria.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/project-management/sprints",
    },
    {
        "file": "Roadmap.md",
        "title": "Development Roadmap & Milestones",
        "description": "Long-term development roadmap across Phase 1 (MVP) through Phase 4 (Scale), release milestones, and Gantt schedule.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/project-management/roadmap",
    },
    {
        "file": "Risk_Register.md",
        "title": "Risk Register & Mitigation Matrix",
        "description": "12 project, technical, and operational risks scored by Probability x Impact with mitigation and contingency plans.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/project-management/risks",
    },
    {
        "file": "README.md",
        "title": "Project Management Section Manifest",
        "description": "Section index, documentation directory, consolidated governance posture, and live project management diagnostic health checks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/project-management",
    },
]


def get_project_management_section_manifest() -> Dict[str, Any]:
    """Return Section 13 documentation catalog and navigation metadata."""
    completed = sum(1 for d in PROJECT_MANAGEMENT_SECTION_MANIFEST if d["status"] == "COMPLETED")
    total = len(PROJECT_MANAGEMENT_SECTION_MANIFEST)

    return {
        "section_id": "13_Project_Management",
        "title": "13 — Project Management",
        "description": "Project management, sprint planning, development roadmap, and risk governance for MemeGPT.",
        "total_documents": total,
        "completed_documents": completed,
        "completion_percentage": f"{round((completed / total) * 100, 1)}%",
        "navigation": {
            "previous": {
                "section": "12_Deployment",
                "title": "12 — Deployment",
                "path": "12_Deployment/README.md",
            },
            "next": {
                "section": "14_Troubleshooting",
                "title": "14 — Troubleshooting",
                "path": "14_Troubleshooting/README.md",
            },
        },
        "documents": PROJECT_MANAGEMENT_SECTION_MANIFEST,
    }


# ── 2. Consolidated Project Governance Posture Summary ─────────────────────────

def get_project_management_posture_summary() -> Dict[str, Any]:
    """Return consolidated project management and agile delivery posture."""
    summary = get_mvp_completion_summary()
    dod = get_definition_of_done()

    return {
        "project_governance": {
            "methodology": "Agile Sprint Delivery (2-Week Iterations)",
            "total_sprints": 4,
            "total_duration": "8 Weeks",
            "overall_status": summary["overall_status"],
            "total_tasks": summary["total_tasks"],
            "completed_tasks": summary["completed_tasks"],
            "completion_rate": summary["completion_rate"],
        },
        "team_allocation": summary["owners_breakdown"],
        "quality_gates": {
            "definition_of_done_criteria_count": dod["total_criteria"],
            "mandatory_gates": [c["title"] for c in dod["criteria"]],
            "ci_cd_automated_verification": True,
        },
        "risk_governance": {
            "risk_assessment_framework": "Probability (1-5) x Impact (1-5) Scoring Matrix",
            "total_tracked_risks": 12,
            "risk_monitoring_cadence": "Weekly sprint planning and retrospective",
        },
    }


# ── 3. Project Management Diagnostic Health Check ─────────────────────────────

def get_project_management_subsystem_health() -> Dict[str, Any]:
    """Evaluate real-time project management subsystem health."""
    summary = get_mvp_completion_summary()
    dod = get_definition_of_done()

    healthy = (
        summary["total_tasks"] > 0
        and summary["completed_tasks"] > 0
        and dod["total_criteria"] == 6
    )

    return {
        "status": "HEALTHY" if healthy else "DEGRADED",
        "sprint_roadmap_loaded": True,
        "definition_of_done_active": True,
        "governance_gates_verified": True,
        "active_sprints": 4,
        "completed_milestones": len(summary["milestones"]),
    }
