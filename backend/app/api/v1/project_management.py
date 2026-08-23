"""Project Management API Router for MemeGPT.
Specification: 13_Project_Management/MVP_Phases.md

Endpoints:
- GET  /api/v1/project-management/sprints
- GET  /api/v1/project-management/sprints/{sprint_id}
- GET  /api/v1/project-management/dod
- POST /api/v1/project-management/dod/evaluate
- GET  /api/v1/project-management/mvp-summary
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from app.services.mvp_phases_service import (
    get_all_sprints,
    get_sprint_by_id,
    get_definition_of_done,
    evaluate_dod_readiness,
    get_mvp_completion_summary,
)

router = APIRouter(prefix="/project-management", tags=["Project Management"])


class DoDEvaluationRequest(BaseModel):
    merged_develop: bool = Field(default=False, description="Code merged to develop")
    tests_pass: bool = Field(default=False, description="All unit, lint, and build tests pass")
    no_critical_bugs: bool = Field(default=False, description="No P0/P1 blocking issues")
    code_reviewed: bool = Field(default=False, description="Peer code review completed")
    documentation_updated: bool = Field(default=False, description="Documentation updated")
    staging_verified: bool = Field(default=False, description="Staging environment smoke tests passed")


@router.get("/sprints", summary="Get all 4 MVP sprints and task breakdown")
def list_sprints():
    """Retrieve complete roadmap across all 4 MVP sprints (8 weeks, 30 tasks)."""
    return {
        "success": True,
        **get_all_sprints(),
    }


@router.get("/sprints/{sprint_id}", summary="Get sprint details by ID")
def get_sprint(sprint_id: int = Path(..., ge=1, le=4, description="Sprint ID (1 to 4)")):
    """Retrieve tasks, ownership, and completion rate for a specific sprint."""
    sprint = get_sprint_by_id(sprint_id=sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail=f"Sprint {sprint_id} not found. Must be 1 to 4.")
    return {
        "success": True,
        "sprint": sprint,
    }


@router.get("/dod", summary="Get Definition of Done (DoD) criteria")
def get_dod():
    """Retrieve 6 standard Definition of Done checklist requirements."""
    return {
        "success": True,
        **get_definition_of_done(),
    }


@router.post("/dod/evaluate", summary="Evaluate feature against Definition of Done")
def evaluate_dod(body: DoDEvaluationRequest):
    """Audit whether a task or feature branch satisfies the 6 DoD criteria."""
    checks = body.model_dump()
    return {
        "success": True,
        **evaluate_dod_readiness(checks=checks),
    }


@router.get("/mvp-summary", summary="Get MVP completion and milestone summary")
def get_summary():
    """Retrieve high-level milestone progress, team ownership, and completion velocity."""
    return {
        "success": True,
        **get_mvp_completion_summary(),
    }


# ── Manifest & Governance Endpoints (13_Project_Management/README.md) ───────

from app.services.project_management_manifest_service import (
    get_project_management_section_manifest,
    get_project_management_posture_summary,
    get_project_management_subsystem_health,
)


@router.get("/manifest", summary="Get Section 13 documentation manifest")
def get_pm_manifest():
    """Retrieve complete catalog and navigation metadata for Section 13."""
    return {
        "success": True,
        **get_project_management_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated project governance posture")
def get_pm_posture():
    """Retrieve agile delivery model, team allocation, quality gates, and risk posture."""
    return {
        "success": True,
        **get_project_management_posture_summary(),
    }


@router.get("/health", summary="Get project management subsystem health")
def get_pm_health():
    """Evaluate health and readiness of sprint planning and governance subsystems."""
    return {
        "success": True,
        **get_project_management_subsystem_health(),
    }


# ── Risk Register Endpoints (13_Project_Management/Risk_Register.md) ────────

from app.services.risk_register_service import (
    get_all_risks,
    get_risk_by_id,
    get_risk_matrix_quadrants,
    get_risk_summary_stats,
    audit_risk_mitigation_health,
)


@router.get("/risks", summary="Get all 12 tracked project & technical risks")
def list_risks(severity: Optional[str] = None):
    """Retrieve all 12 tracked risk items, with optional severity filtering (High, Medium, Low)."""
    return {
        "success": True,
        **get_all_risks(severity=severity),
    }


@router.get("/risks/matrix/quadrants", summary="Get risk quadrant assessment matrix")
def get_risk_quadrants():
    """Retrieve 4-quadrant risk distribution (Critical, Monitor, Mitigate, Accept)."""
    return {
        "success": True,
        **get_risk_matrix_quadrants(),
    }


@router.get("/risks/summary/stats", summary="Get risk register statistical summary")
def get_risk_stats():
    """Retrieve risk breakdown by severity levels and mitigation statuses."""
    return {
        "success": True,
        **get_risk_summary_stats(),
    }


@router.get("/risks/audit/health", summary="Audit risk mitigation health")
def get_risk_audit():
    """Evaluate whether all risk vectors have documented mitigations and contingency plans."""
    return {
        "success": True,
        **audit_risk_mitigation_health(),
    }


@router.get("/risks/{risk_id}", summary="Get specific risk details and mitigation plan")
def get_risk(risk_id: str = Path(..., description="Risk ID (e.g. R1, R2, ..., R12)")):
    """Retrieve single risk metadata, probability/impact score, and mitigation runbook."""
    risk = get_risk_by_id(risk_id=risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk '{risk_id}' not found. Valid IDs: R1 to R12.")
    return {
        "success": True,
        "risk": risk,
    }


# ── Roadmap & Milestones Endpoints (13_Project_Management/Roadmap.md) ───────

from app.services.roadmap_service import (
    get_roadmap_phases,
    get_roadmap_phase_by_id,
    get_roadmap_gantt_chart,
    get_success_metrics_by_phase,
    evaluate_phase_readiness,
)


@router.get("/roadmap/phases", summary="Get all 4 product roadmap phases")
def list_roadmap_phases():
    """Retrieve complete feature list and timeline across Phase 1 to Phase 4."""
    return {
        "success": True,
        **get_roadmap_phases(),
    }


@router.get("/roadmap/phases/{phase_id}", summary="Get specific roadmap phase details")
def get_phase(phase_id: int = Path(..., ge=1, le=4, description="Phase ID (1 to 4)")):
    """Retrieve feature priority list, delivery timeline, and metrics for a phase."""
    phase = get_roadmap_phase_by_id(phase_id=phase_id)
    if not phase:
        raise HTTPException(status_code=404, detail=f"Phase {phase_id} not found. Must be 1 to 4.")
    return {
        "success": True,
        "phase": phase,
    }


@router.get("/roadmap/gantt", summary="Get roadmap Gantt chart schedule")
def get_gantt():
    """Retrieve Mermaid Gantt chart schedule and milestone timelines."""
    return {
        "success": True,
        **get_roadmap_gantt_chart(),
    }


@router.get("/roadmap/metrics", summary="Get success metrics benchmarks by phase")
def get_metrics():
    """Retrieve target DAU, latency, feedback, and MRR metrics for all phases."""
    return {
        "success": True,
        **get_success_metrics_by_phase(),
    }


@router.get("/roadmap/readiness/{phase_id}", summary="Evaluate phase delivery readiness")
def get_phase_readiness(phase_id: int = Path(..., ge=1, le=4, description="Phase ID (1 to 4)")):
    """Evaluate completion rate and deployment readiness for a roadmap phase."""
    return {
        "success": True,
        **evaluate_phase_readiness(phase_id=phase_id),
    }
