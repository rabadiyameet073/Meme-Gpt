"""Troubleshooting API Router for MemeGPT.
Specification: 14_Troubleshooting/Common_Issues.md

Endpoints:
- GET  /api/v1/troubleshooting/flowchart
- GET  /api/v1/troubleshooting/issues
- GET  /api/v1/troubleshooting/issues/{issue_id}
- POST /api/v1/troubleshooting/diagnose
- GET  /api/v1/troubleshooting/practices
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from app.services.troubleshooting_service import (
    get_diagnostic_flowchart,
    get_common_issues_catalog,
    get_issue_by_id,
    get_debugging_best_practices,
    diagnose_system_issue,
)

router = APIRouter(prefix="/troubleshooting", tags=["Troubleshooting"])


class SystemDiagnosticRequest(BaseModel):
    health_status_200: bool = Field(default=True, description="Whether /health returned 200 OK")
    search_results_count: int = Field(default=10, description="Number of results returned by /search")
    qdrant_connected: bool = Field(default=True, description="Whether Qdrant vector database is reachable")
    redis_connected: bool = Field(default=True, description="Whether Redis cache is reachable")
    latency_seconds: float = Field(default=1.2, description="Observed endpoint response latency in seconds")


@router.get("/flowchart", summary="Get quick diagnostic flowchart")
def get_flowchart():
    """Retrieve structured decision tree for debugging application and infrastructure failures."""
    return {
        "success": True,
        **get_diagnostic_flowchart(),
    }


@router.get("/issues", summary="Get all 8 common troubleshooting issues")
def list_issues():
    """Retrieve complete catalog of 8 common issues, causes, and step-by-step resolution commands."""
    return {
        "success": True,
        **get_common_issues_catalog(),
    }


@router.get("/practices", summary="Get 5 debugging best practices")
def get_practices():
    """Retrieve 5 debugging best practices."""
    return {
        "success": True,
        **get_debugging_best_practices(),
    }


@router.post("/diagnose", summary="Diagnose system symptoms & return fixes")
def run_diagnosis(body: SystemDiagnosticRequest):
    """Analyze reported runtime symptoms and retrieve targeted remediation runbooks."""
    return {
        "success": True,
        **diagnose_system_issue(
            health_status_200=body.health_status_200,
            search_results_count=body.search_results_count,
            qdrant_connected=body.qdrant_connected,
            redis_connected=body.redis_connected,
            latency_seconds=body.latency_seconds,
        ),
    }


@router.get("/issues/{issue_id}", summary="Get resolution guide for a specific issue ID")
def get_issue(issue_id: str = Path(..., description="Issue identifier (e.g. ERR_MISSING_DEPENDENCY, ISSUE_ZERO_SEARCH_RESULTS)")):
    """Retrieve root cause, symptom details, and exact CLI remediation command."""
    issue = get_issue_by_id(issue_id=issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found in troubleshooting catalog.")
    return {
        "success": True,
        "issue": issue,
    }


# ── Debug Guide Endpoints (14_Troubleshooting/Debug_Guide.md) ────────────────

from app.services.debug_guide_service import (
    get_backend_debug_procedures,
    get_frontend_debug_guide,
    get_database_debug_commands,
    get_ml_debug_recipes,
    get_network_debug_tools,
    get_search_quality_decision_tree,
    simulate_search_quality_diagnosis,
)


class SearchQualityDiagnosisRequest(BaseModel):
    db_seeded: bool = Field(default=True, description="Whether the database has been seeded")
    embeddings_generated: bool = Field(default=True, description="Whether embeddings are present in Qdrant")
    groq_working: bool = Field(default=True, description="Whether Groq LLM API is responding")
    qdrant_connected: bool = Field(default=True, description="Whether Qdrant cluster is reachable")


@router.get("/debug/backend", summary="Get backend debugging guide and curl commands")
def get_dbg_backend():
    """Retrieve uvicorn debug flags, endpoint curl commands, and Python scoring test scripts."""
    return {
        "success": True,
        **get_backend_debug_procedures(),
    }


@router.get("/debug/frontend", summary="Get frontend DevTools and console debug guide")
def get_dbg_frontend():
    """Retrieve Chrome DevTools 5-tab debugging guide and browser console snippets."""
    return {
        "success": True,
        **get_frontend_debug_guide(),
    }


@router.get("/debug/database", summary="Get database exploration and debug queries")
def get_dbg_database():
    """Retrieve Prisma Studio instructions and SQLite/Postgres verification queries."""
    return {
        "success": True,
        **get_database_debug_commands(),
    }


@router.get("/debug/ml", summary="Get ML model standalone debug scripts")
def get_dbg_ml():
    """Retrieve standalone test snippets for DistilRoBERTa emotion and Groq intent parsing."""
    return {
        "success": True,
        **get_ml_debug_recipes(),
    }


@router.get("/debug/network", summary="Get network diagnostic tools")
def get_dbg_network():
    """Retrieve network diagnostic commands (nslookup, netstat, openssl, curl timing)."""
    return {
        "success": True,
        **get_network_debug_tools(),
    }


@router.get("/debug/decision-tree", summary="Get search quality debugging decision tree")
def get_dbg_decision_tree():
    """Retrieve structured 5-step decision tree for resolving bad search results."""
    return {
        "success": True,
        **get_search_quality_decision_tree(),
    }


@router.post("/debug/diagnose-quality", summary="Simulate search quality diagnosis")
def diagnose_quality(body: SearchQualityDiagnosisRequest):
    """Evaluate pipeline state against search quality decision tree and output targeted action."""
    return {
        "success": True,
        **simulate_search_quality_diagnosis(
            db_seeded=body.db_seeded,
            embeddings_generated=body.embeddings_generated,
            groq_working=body.groq_working,
            qdrant_connected=body.qdrant_connected,
        ),
    }


# ── Manifest & Health Endpoints (14_Troubleshooting/README.md) ───────────────

from app.services.troubleshooting_manifest_service import (
    get_troubleshooting_section_manifest,
    get_troubleshooting_posture_summary,
    get_troubleshooting_subsystem_health,
)


@router.get("/manifest", summary="Get Section 14 documentation manifest")
def get_tb_manifest():
    """Retrieve complete catalog and navigation metadata for Section 14."""
    return {
        "success": True,
        **get_troubleshooting_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated troubleshooting posture")
def get_tb_posture():
    """Retrieve diagnostic flowcharts, common issues count, and debugging tools posture."""
    return {
        "success": True,
        **get_troubleshooting_posture_summary(),
    }


@router.get("/health", summary="Get troubleshooting subsystem health")
def get_tb_health():
    """Evaluate health and readiness of diagnostic engines and troubleshooting catalogs."""
    return {
        "success": True,
        **get_troubleshooting_subsystem_health(),
    }
