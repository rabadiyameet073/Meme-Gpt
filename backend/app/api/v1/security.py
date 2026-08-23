"""Security API Router for MemeGPT.
Specification: 11_Security/API_Security.md
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.api_security_service import (
    get_security_layers,
    get_security_headers_spec,
    get_secret_management_matrix,
    get_cors_policy_spec,
    get_security_prelaunch_checklist,
    evaluate_security_compliance,
    mask_api_key,
)
from app.services.security_manifest_service import (
    get_security_section_manifest,
    get_security_posture_summary,
    get_security_subsystem_health,
)

logger = logging.getLogger("memegpt.api.security")
router = APIRouter(prefix="/security", tags=["Security & Compliance"])


class KeyMaskRequest(BaseModel):
    api_key: str = Field(..., description="Raw API key to mask for display")


@router.get("/manifest", summary="Get Section 11 Security documentation manifest")
def get_manifest():
    """Retrieve Section 11 documentation inventory, completion status, and navigation links."""
    return {
        "success": True,
        **get_security_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated security posture summary")
def get_posture():
    """Retrieve security posture overview across Transport, Browser, Application, Privacy, and Rate Limiting."""
    return {
        "success": True,
        **get_security_posture_summary(),
    }


@router.get("/health", summary="Get live security subsystem diagnostic health")
def get_health():
    """Run real-time diagnostics across API Security, Data Privacy, Input Validation, and Rate Limiting."""
    return {
        "success": True,
        **get_security_subsystem_health(),
    }


@router.get("/layers", summary="Get 6-layer security architecture pipeline")
def get_layers():
    """Retrieve the 6-layer security pipeline (HTTPS, CORS, Rate Limit, Input Validation, Auth, Route Handler)."""
    return {
        "success": True,
        **get_security_layers(),
    }


@router.get("/headers", summary="Get security headers specification")
def get_headers():
    """Retrieve security headers spec (HSTS, X-Frame-Options, X-Content-Type-Options, etc.)."""
    return {
        "success": True,
        **get_security_headers_spec(),
    }


@router.get("/secrets", summary="Get secret management matrix and rules")
def get_secrets():
    """Retrieve secret storage matrix and 4 fundamental security rules."""
    return {
        "success": True,
        **get_secret_management_matrix(),
    }


@router.get("/cors", summary="Get CORS policy specification")
def get_cors(production: Optional[bool] = Query(default=None, description="Check for production CORS origins")):
    """Retrieve CORS allowed origins and policy configuration."""
    return {
        "success": True,
        "policy": get_cors_policy_spec(is_production=production),
    }


@router.get("/checklist", summary="Get 12-point pre-launch security checklist")
def get_checklist():
    """Retrieve 12-point pre-launch security checklist."""
    return {
        "success": True,
        **get_security_prelaunch_checklist(),
    }


@router.get("/compliance", summary="Evaluate runtime security compliance")
def get_compliance(production: Optional[bool] = Query(default=None, description="Evaluate in production mode")):
    """Run live programmatic audit against the 12-point pre-launch security checklist."""
    return {
        "success": True,
        **evaluate_security_compliance(is_production=production),
    }


@router.post("/mask-key", summary="Mask API key for safe display")
def mask_key_endpoint(body: KeyMaskRequest):
    """Mask an API key for safe display according to Secret Rule 3."""
    return {
        "success": True,
        "masked_key": mask_api_key(body.api_key),
    }


# ── Security Overview & Threat Model Endpoints (11_Security/Security_Overview.md) ──

from app.services.security_overview_service import (
    get_defense_in_depth_layers,
    get_owasp_top_10_matrix,
    get_threat_model_matrix,
    get_master_security_checklist,
    evaluate_owasp_compliance_status,
)


@router.get("/overview/layers", summary="Get 5-layer defense-in-depth model")
def get_defense_layers():
    """Retrieve 5 defense-in-depth security layers (Network, Application, Input, Data, Infrastructure)."""
    return {
        "success": True,
        **get_defense_in_depth_layers(),
    }


@router.get("/overview/owasp", summary="Get OWASP Top 10 security mapping")
def get_owasp():
    """Retrieve OWASP Top 10 risk mitigations and implementation status."""
    return {
        "success": True,
        **get_owasp_top_10_matrix(),
    }


@router.get("/overview/threat-model", summary="Get threat model matrix")
def get_threat_model():
    """Retrieve threat model with likelihood, impact, and engineering mitigations."""
    return {
        "success": True,
        **get_threat_model_matrix(),
    }


@router.get("/overview/audit-checklist", summary="Get master security audit checklist")
def get_audit_checklist():
    """Retrieve master pre-launch security checklist with verification status."""
    return {
        "success": True,
        **get_master_security_checklist(),
    }


@router.get("/overview/owasp-status", summary="Get OWASP compliance score")
def get_owasp_status():
    """Calculate OWASP Top 10 mitigation score and coverage."""
    return {
        "success": True,
        **evaluate_owasp_compliance_status(),
    }
