"""Data Privacy & GDPR API Router for MemeGPT.
Specification: 11_Security/Data_Privacy.md
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, User, SavedMeme, Feedback, SearchLog
from app.core.auth import get_current_user
from app.services.data_privacy_service import (
    get_privacy_by_design_principles,
    get_data_classification_matrix,
    get_gdpr_rights_catalog,
    get_cookie_policy_spec,
    get_dpa_status_matrix,
    export_session_data,
    delete_session_data,
    purge_expired_privacy_data,
    evaluate_privacy_compliance,
)

logger = logging.getLogger("memegpt.api.privacy")
router = APIRouter(prefix="/privacy", tags=["Data Privacy & GDPR"])


class PurgeRequest(BaseModel):
    retention_days: int = Field(default=90, ge=1, le=365, description="Days of data to retain before purging")


@router.get("/principles", summary="Get 7 Privacy-by-Design principles")
def get_principles():
    """Retrieve the 7 fundamental Privacy-by-Design principles implemented across MemeGPT."""
    return {
        "success": True,
        **get_privacy_by_design_principles(),
    }


@router.get("/classification", summary="Get 6-category data classification matrix")
def get_classification():
    """Retrieve data classification, storage durations, and retention policies."""
    return {
        "success": True,
        **get_data_classification_matrix(),
    }


@router.get("/gdpr-rights", summary="Get GDPR data subject rights mapping")
def get_gdpr_rights():
    """Retrieve supported GDPR data subject rights and corresponding endpoints."""
    return {
        "success": True,
        **get_gdpr_rights_catalog(),
    }


@router.get("/cookies", summary="Get cookie policy and privacy guarantees")
def get_cookies():
    """Retrieve cookie inventory with strict zero third-party/advertising guarantees."""
    return {
        "success": True,
        **get_cookie_policy_spec(),
    }


@router.get("/dpa", summary="Get Data Processing Agreements (DPA) status matrix")
def get_dpa():
    """Retrieve status of third-party DPAs (Supabase, Groq, Qdrant, Cloudflare, Vercel)."""
    return {
        "success": True,
        **get_dpa_status_matrix(),
    }


@router.get("/export", summary="GDPR Right to Access & Portability")
def export_data(
    session_id: str = Query(..., description="Client session ID to export data for"),
    db: Session = Depends(get_db),
):
    """Export all stored feedback, votes, and favorites associated with session ID in JSON format."""
    if not session_id or session_id.strip() == "":
        raise HTTPException(status_code=400, detail="session_id is required")
    res = export_session_data(session_id=session_id, db=db)
    return {
        "success": True,
        **res,
    }


@router.delete("/delete", summary="GDPR Right to Erasure / Deletion")
def delete_data(
    session_id: str = Query(..., description="Client session ID to delete data for"),
    db: Session = Depends(get_db),
):
    """Permanently delete all stored feedback, votes, and favorites associated with session ID."""
    if not session_id or session_id.strip() == "":
        raise HTTPException(status_code=400, detail="session_id is required")
    res = delete_session_data(session_id=session_id, db=db)
    return res


@router.post("/purge-expired", summary="Purge data older than retention limit")
def purge_expired(
    body: PurgeRequest = PurgeRequest(),
    db: Session = Depends(get_db),
):
    """Auto-purge feedback and interaction records older than retention threshold (default 90 days)."""
    res = purge_expired_privacy_data(db=db, retention_days=body.retention_days)
    return res


@router.get("/compliance", summary="Evaluate GDPR and privacy-by-design compliance")
def get_compliance():
    """Evaluate system implementation against GDPR and Privacy-by-Design standards."""
    return {
        "success": True,
        **evaluate_privacy_compliance(),
    }


@router.delete("/me", status_code=status.HTTP_200_OK, summary="GDPR Right to Be Forgotten")
async def delete_user_account_and_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    logger.info(f"Initiating full GDPR data purge for user_id={user_id}")

    try:
        # 1. Delete all saved memes and collections
        deleted_saved = db.query(SavedMeme).filter(SavedMeme.user_id == user_id).delete()

        # 2. Anonymize feedback logs (remove user association, preserve training signals)
        db.query(Feedback).filter(Feedback.user_id == str(user_id)).update({
            "user_id": "anonymized",
            "session_id": "anonymized"
        })

        # 3. Anonymize search logs
        db.query(SearchLog).filter(SearchLog.session_id == str(user_id)).update({
            "session_id": "anonymized"
        })

        # 4. Delete user account record
        db.delete(current_user)
        db.commit()

        return {
            "status": "success",
            "message": "All personal data has been permanently purged.",
            "records_deleted": {
                "saved_memes": deleted_saved,
                "user_account": 1
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"GDPR purge failed for user_id={user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete data deletion request."
        )
