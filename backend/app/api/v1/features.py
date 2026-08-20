"""Features Section API Router for MemeGPT.
Specification: 08_Features/README.md
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.feature_manifest_service import (
    get_features_section_manifest,
    get_feature_by_id,
    verify_feature_system_health,
)

logger = logging.getLogger("memegpt.api.features")
router = APIRouter(prefix="/features", tags=["Features Section Manifest"])


@router.get("", summary="List all features in section 08")
def get_features():
    """Retrieve full catalog of features in Section 08."""
    manifest = get_features_section_manifest()
    return {
        "success": True,
        **manifest,
    }


@router.get("/health", summary="Verify features readiness")
def get_features_health():
    """Verify operational health across all feature capabilities."""
    health = verify_feature_system_health()
    return {
        "success": True,
        **health,
    }


@router.get("/{feature_id}", summary="Get individual feature specification")
def get_feature(feature_id: str):
    """Retrieve specification, document link, and endpoints for a feature."""
    feat = get_feature_by_id(feature_id)
    if not feat:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found in Section 08 manifest")
    return {
        "success": True,
        "feature": feat,
    }
