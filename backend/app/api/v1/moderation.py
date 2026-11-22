"""Content moderation — flagging, review queue, admin actions."""
import hashlib
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_admin
from app.core.rate_limit import require_route_rate_limit
from app.database import Meme, MemeFlag, DMCANotice, get_db, utc_now

router = APIRouter(prefix="/moderation", tags=["Content Moderation"])


class FlagRequest(BaseModel):
    meme_id: str
    reason: str  # 'nsfw' | 'offensive' | 'copyright' | 'spam' | 'other'
    details: Optional[str] = ""


class DMCANoticeRequest(BaseModel):
    claimant_name: str = Field(..., min_length=2, max_length=200)
    claimant_email: str = Field(..., min_length=5, max_length=255)
    copyrighted_work: str = Field(..., min_length=5)
    infringing_url: str = Field(..., min_length=5)
    meme_id: Optional[str] = None


@router.post(
    "/flag",
    summary="Flag a meme as inappropriate",
    dependencies=[Depends(require_route_rate_limit("moderation_flag"))],
)
async def flag_meme(body: FlagRequest, request: Request, db: Session = Depends(get_db)):
    """Community flagging with abuse resistance and hashed IP reporter privacy (MOD-05, MOD-06)."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    if body.reason not in ("nsfw", "offensive", "copyright", "spam", "other"):
        raise HTTPException(status_code=400, detail="Invalid reason. Allowed: nsfw, offensive, copyright, spam, other")

    client_ip = request.client.host if request.client else "unknown"
    # MOD-06: Hash reporter IP for GDPR/privacy retention
    reporter_hash = hashlib.sha256(f"reporter:{client_ip}".encode("utf-8")).hexdigest()[:32]

    # MOD-05: Deduplicate flag per (meme_id, reporter_hash)
    existing_flag = db.query(MemeFlag).filter(
        MemeFlag.meme_id == body.meme_id,
        MemeFlag.reporter_ip == reporter_hash,
    ).first()
    if existing_flag:
        return {
            "flagged": True,
            "total_flags": meme.flag_count or 0,
            "moderation_status": meme.moderation_status or "approved",
            "message": "Flag already recorded for this device.",
        }

    flag = MemeFlag(
        meme_id=body.meme_id,
        reporter_ip=reporter_hash,
        reason=body.reason,
        details=body.details or "",
    )
    db.add(flag)

    # Increment flag count
    meme.flag_count = (meme.flag_count or 0) + 1

    # Auto-queue for review after 5 flags (hidden pending review)
    if meme.flag_count >= 5 and meme.moderation_status == "approved":
        meme.moderation_status = "pending_review"
        from app.core.cache import cache_flush_pattern
        cache_flush_pattern("search:*")
        from app.services.trending_service import invalidate_trending_cache
        invalidate_trending_cache()

    db.commit()

    return {"flagged": True, "total_flags": meme.flag_count, "moderation_status": meme.moderation_status}


@router.post("/dmca", summary="Submit a DMCA copyright takedown notice (MOD-07)")
async def submit_dmca_notice(body: DMCANoticeRequest, db: Session = Depends(get_db)):
    """Receives DMCA notices, logs audit entry, immediately soft-deletes meme and flushes cache."""
    target_meme = None
    if body.meme_id:
        target_meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not target_meme and body.infringing_url:
        slug = body.infringing_url.rstrip("/").split("/")[-1]
        target_meme = db.query(Meme).filter((Meme.slug == slug) | (Meme.id == slug)).first()

    notice = DMCANotice(
        meme_id=target_meme.id if target_meme else body.meme_id,
        claimant_name=body.claimant_name,
        claimant_email=body.claimant_email,
        copyrighted_work=body.copyrighted_work,
        infringing_url=body.infringing_url,
        action_taken="takedown" if target_meme else "pending_review",
        status="processed" if target_meme else "pending",
    )
    db.add(notice)

    if target_meme:
        target_meme.moderation_status = "removed"
        from app.core.cache import cache_flush_pattern
        cache_flush_pattern("search:*")
        from app.services.trending_service import invalidate_trending_cache
        invalidate_trending_cache()

    db.commit()
    db.refresh(notice)
    return {"success": True, "notice_id": notice.id, "action_taken": notice.action_taken}


@router.get("/dmca/notices", summary="List DMCA takedown notices (admin)")
async def list_dmca_notices(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Retrieve logged DMCA notices for administrative review (MOD-07)."""
    notices = db.query(DMCANotice).order_by(DMCANotice.created_at.desc()).limit(100).all()
    return {"notices": [n.to_dict() for n in notices]}


@router.get("/queue", summary="Get moderation review queue (admin)")
async def get_review_queue(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Returns memes pending review, sorted by flag count. Admin only."""
    memes = (
        db.query(Meme)
        .filter(Meme.moderation_status == "pending_review")
        .order_by(Meme.flag_count.desc())
        .limit(50)
        .all()
    )
    return {
        "queue": [
            {
                **m.to_dict(),
                "flag_count": m.flag_count,
                "flags": [
                    {"reason": f.reason, "details": f.details, "created_at": f.created_at.isoformat() if f.created_at else None}
                    for f in m.flags
                ],
            }
            for m in memes
        ]
    }


class ReviewAction(BaseModel):
    meme_id: str
    action: str  # 'approve' | 'remove'


@router.post("/review", summary="Admin review action")
async def review_meme(
    body: ReviewAction,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Admin approves or removes a flagged meme. Admin only."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    if body.action == "approve":
        meme.moderation_status = "approved"
        meme.flag_count = 0
        db.query(MemeFlag).filter(
            MemeFlag.meme_id == body.meme_id, MemeFlag.status == "pending"
        ).update({"status": "dismissed", "reviewed_at": utc_now()})
    elif body.action == "remove":
        meme.moderation_status = "removed"
        db.query(MemeFlag).filter(
            MemeFlag.meme_id == body.meme_id, MemeFlag.status == "pending"
        ).update({"status": "reviewed", "reviewed_at": utc_now()})
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'remove'")

    db.commit()

    # Trending filters on moderation_status, but the ranking is cached for an
    # hour in both tiers — a removed meme would keep being served until then.
    from app.services.trending_service import invalidate_trending_cache
    invalidate_trending_cache()

    from app.core.cache import cache_flush_pattern
    cache_flush_pattern("search:*")

    return {"meme_id": meme.id, "status": meme.moderation_status}


class ClassifyRequest(BaseModel):
    image_url: Optional[str] = None
    image_path: Optional[str] = None


@router.post("/classify", summary="Classify image for NSFW content using CLIP")
async def classify_content(
    body: ClassifyRequest,
    auth: AuthContext = Depends(require_admin),
):
    """Zero-shot CLIP classification for safe vs. NSFW / violent content.

    Admin only: the endpoint can read arbitrary server paths and fetch arbitrary
    URLs, so exposing it anonymously would allow local file disclosure.
    """
    from app.services.nsfw_service import classify_image, classify_image_from_url
    if body.image_url:
        is_nsfw, confidence, category = classify_image_from_url(body.image_url)
    elif body.image_path:
        is_nsfw, confidence, category = classify_image(body.image_path)
    else:
        raise HTTPException(status_code=400, detail="Provide either image_url or image_path")
    return {
        "is_nsfw": is_nsfw,
        "confidence": round(confidence, 4),
        "category": category,
    }

