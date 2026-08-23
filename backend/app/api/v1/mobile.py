"""Mobile Application API Router for MemeGPT.
Specification: 15_Mobile/Mobile_Overview.md

Endpoints:
- GET  /api/v1/mobile/stack
- GET  /api/v1/mobile/architecture
- GET  /api/v1/mobile/platforms
- GET  /api/v1/mobile/build-release
- GET  /api/v1/mobile/size-budget
- GET  /api/v1/mobile/features
- POST /api/v1/mobile/offline-sync
- GET  /api/v1/mobile/readiness
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.mobile_service import (
    get_mobile_tech_stack,
    get_mobile_architecture,
    get_platform_differences,
    get_build_and_release_workflows,
    get_app_size_budget,
    get_mobile_features_catalog,
    simulate_mobile_offline_sync,
    evaluate_mobile_app_readiness,
)

router = APIRouter(prefix="/mobile", tags=["Mobile App"])


class OfflineSyncRequest(BaseModel):
    cached_memes: List[Dict[str, Any]] = Field(default_factory=list, description="List of locally cached meme objects")
    max_cache_size: int = Field(default=50, ge=1, le=200, description="Max cache capacity (defaults to 50 memes)")


@router.get("/stack", summary="Get mobile tech stack")
def get_stack():
    """Retrieve React Native 0.74, Expo SDK 51, Expo Router, EAS Build, and Hermes configurations."""
    return {
        "success": True,
        **get_mobile_tech_stack(),
    }


@router.get("/architecture", summary="Get mobile screen architecture and native APIs")
def get_arch():
    """Retrieve 4-screen navigation structure and native modules (expo-sharing, media-library, haptics, clipboard)."""
    return {
        "success": True,
        **get_mobile_architecture(),
    }


@router.get("/platforms", summary="Get iOS vs Android platform differences matrix")
def get_platforms():
    """Retrieve share sheet, permissions, haptics, push notification, and binary size matrix."""
    return {
        "success": True,
        **get_platform_differences(),
    }


@router.get("/build-release", summary="Get Expo and EAS build/release commands")
def get_workflows():
    """Retrieve development simulator commands and production EAS Build/Submit pipelines."""
    return {
        "success": True,
        **get_build_and_release_workflows(),
    }


@router.get("/size-budget", summary="Get app binary size budget breakdown")
def get_budget():
    """Retrieve component size breakdown (Hermes, JS bundle, Expo modules, assets) totaling ~29MB."""
    return {
        "success": True,
        **get_app_size_budget(),
    }


@router.get("/features", summary="Get mobile-specific features list & priorities")
def get_features():
    """Retrieve mobile feature backlog with priority ratings (P0, P1, P2)."""
    return {
        "success": True,
        **get_mobile_features_catalog(),
    }


@router.post("/offline-sync", summary="Simulate mobile offline cache sync (50 memes LRU)")
def offline_sync(body: OfflineSyncRequest):
    """Maintain local MMKV/AsyncStorage cache enforcing 50-meme LRU eviction."""
    return {
        "success": True,
        **simulate_mobile_offline_sync(
            cached_memes=body.cached_memes,
            max_cache_size=body.max_cache_size,
        ),
    }


@router.get("/readiness", summary="Evaluate mobile app delivery readiness")
def get_readiness():
    """Check readiness across tech stack, screen models, size budget, and prioritized features."""
    return {
        "success": True,
        **evaluate_mobile_app_readiness(),
    }


# ── Manifest & Health Endpoints (15_Mobile/README.md) ────────────────────────

from app.services.mobile_manifest_service import (
    get_mobile_section_manifest,
    get_mobile_posture_summary,
    get_mobile_subsystem_health,
)


@router.get("/manifest", summary="Get Section 15M documentation manifest")
def get_manifest():
    """Retrieve complete catalog and navigation metadata for Section 15M (Mobile)."""
    return {
        "success": True,
        **get_mobile_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated mobile client posture")
def get_posture():
    """Retrieve mobile frameworks, native modules, platform parity, and binary budget posture."""
    return {
        "success": True,
        **get_mobile_posture_summary(),
    }


@router.get("/health", summary="Get mobile client specifications diagnostic health")
def get_health():
    """Evaluate specifications integrity and readiness of mobile client architecture."""
    return {
        "success": True,
        **get_mobile_subsystem_health(),
    }
