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
- POST /api/v1/mobile/push-tokens
- DELETE /api/v1/mobile/push-tokens/{token}
- GET  /api/v1/mobile/readiness
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import DeviceToken, get_db, utc_now
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


# ── Push notification registration ────────────────────────────────────────────

class PushTokenRequest(BaseModel):
    token: str = Field(min_length=8, max_length=255, description="Expo push token from expo-notifications")
    platform: str = Field(default="android", pattern="^(ios|android|web)$")
    user_id: Optional[str] = Field(default=None, max_length=64)
    app_version: Optional[str] = Field(default=None, max_length=32)


@router.post("/push-tokens", status_code=201, summary="Register a device push token")
def register_push_token(body: PushTokenRequest, db: Session = Depends(get_db)):
    """Store or refresh the push token a device obtained from APNs/FCM.

    Registration is idempotent: re-registering the same token reactivates it and
    refreshes ``last_seen_at`` instead of creating a duplicate row.
    """
    token = body.token.strip()
    if not token:
        raise HTTPException(status_code=422, detail="token must not be blank")

    record = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if record is None:
        record = DeviceToken(
            token=token,
            platform=body.platform,
            user_id=body.user_id,
            app_version=body.app_version,
            active=True,
        )
        db.add(record)
        created = True
    else:
        record.platform = body.platform
        record.active = True
        record.last_seen_at = utc_now()
        if body.user_id:
            record.user_id = body.user_id
        if body.app_version:
            record.app_version = body.app_version
        created = False

    db.commit()
    db.refresh(record)
    return {"success": True, "created": created, "device": record.to_dict()}


@router.delete("/push-tokens/{token}", summary="Unregister a device push token")
def unregister_push_token(token: str, db: Session = Depends(get_db)):
    """Deactivate a token — called when the user disables notifications or signs out."""
    record = db.query(DeviceToken).filter(DeviceToken.token == token.strip()).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Push token not registered")
    record.active = False
    record.last_seen_at = utc_now()
    db.commit()
    db.refresh(record)
    return {"success": True, "device": record.to_dict()}


@router.get("/push-tokens", summary="List registered device push tokens")
def list_push_tokens(platform: Optional[str] = None, db: Session = Depends(get_db)):
    """Return active device registrations (tokens are masked)."""
    query = db.query(DeviceToken).filter(DeviceToken.active.is_(True))
    if platform:
        query = query.filter(DeviceToken.platform == platform)
    devices = query.order_by(DeviceToken.last_seen_at.desc()).all()
    return {"success": True, "count": len(devices), "devices": [d.to_dict() for d in devices]}


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
