"""Rate Limiting Security API Router for MemeGPT.
Specification: 11_Security/Rate_Limiting_Security.md
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.rate_limiting_security_service import (
    get_rate_limiting_architecture,
    get_rate_limit_policies,
    get_ddos_mitigation_layers,
    get_rate_limiting_best_practices,
    check_rate_limit_policy,
    evaluate_rate_limiting_security_health,
)

logger = logging.getLogger("memegpt.api.rate_limiting")
router = APIRouter(prefix="/rate-limiting", tags=["Rate Limiting & DDoS Defense"])


class RateLimitCheckRequest(BaseModel):
    endpoint_path: str = Field(..., description="Target endpoint path (e.g. /api/v1/search)")
    client_ip: str = Field(default="127.0.0.1", description="Client IP address")
    custom_limit: Optional[int] = Field(default=None, description="Optional custom quota limit")


@router.get("/architecture", summary="Get rate limiting architecture and workflow")
def get_architecture():
    """Retrieve rate limiting token bucket architecture and workflow details."""
    return {
        "success": True,
        **get_rate_limiting_architecture(),
    }


@router.get("/policies", summary="Get 5 per-endpoint rate limit policies")
def get_policies():
    """Retrieve rate limit policies across search, trending, memes, feedback, and health check endpoints."""
    return {
        "success": True,
        **get_rate_limit_policies(),
    }


@router.get("/ddos-layers", summary="Get 4-layer DDoS mitigation defenses")
def get_ddos_layers():
    """Retrieve the 4 DDoS defense layers (Cloudflare CDN, Application Redis, Infra Autoscaling, IP Blocklist)."""
    return {
        "success": True,
        **get_ddos_mitigation_layers(),
    }


@router.get("/practices", summary="Get 6 rate limiting engineering best practices")
def get_practices():
    """Retrieve rate limiting best practices."""
    return {
        "success": True,
        **get_rate_limiting_best_practices(),
    }


@router.post("/check", summary="Evaluate rate limit quota for endpoint")
def check_rate_limit_endpoint(body: RateLimitCheckRequest):
    """Check if request passes rate limit quota for endpoint path and IP."""
    return {
        "success": True,
        **check_rate_limit_policy(
            endpoint_path=body.endpoint_path,
            client_ip=body.client_ip,
            custom_limit=body.custom_limit,
        ),
    }


@router.get("/health", summary="Rate limiting security health check")
def get_rate_limit_health():
    """Check rate limiting subsystem health, policy enforcement, and health check exemption."""
    return {
        "success": True,
        **evaluate_rate_limiting_security_health(),
    }
