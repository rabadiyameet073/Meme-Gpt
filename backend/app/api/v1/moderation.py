"""Content moderation — flagging, review queue, admin actions."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db, Meme, MemeFlag, utc_now

router = APIRouter(prefix="/moderation", tags=["Content Moderation"])


class FlagRequest(BaseModel):
    meme_id: str
    reason: str  # 'nsfw' | 'offensive' | 'copyright' | 'spam' | 'other'
    details: Optional[str] = ""


@router.post("/flag", summary="Flag a meme as inappropriate")
async def flag_meme(body: FlagRequest, request: Request, db: Session = Depends(get_db)):
    """Community flagging. Auto-queues meme for review after 5 flags."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    if body.reason not in ("nsfw", "offensive", "copyright", "spam", "other"):
        raise HTTPException(status_code=400, detail="Invalid reason. Allowed: nsfw, offensive, copyright, spam, other")

    client_ip = request.client.host if request.client else None
    flag = MemeFlag(
        meme_id=body.meme_id,
        reporter_ip=client_ip,
        reason=body.reason,
        details=body.details or "",
    )
    db.add(flag)

    # Increment flag count
    meme.flag_count = (meme.flag_count or 0) + 1

    # Auto-queue for review after 5 flags
    if meme.flag_count >= 5 and meme.moderation_status == "approved":
        meme.moderation_status = "pending_review"

    db.commit()

    return {"flagged": True, "total_flags": meme.flag_count, "moderation_status": meme.moderation_status}


@router.get("/queue", summary="Get moderation review queue (admin)")
async def get_review_queue(db: Session = Depends(get_db)):
    """Returns memes pending review, sorted by flag count."""
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
async def review_meme(body: ReviewAction, db: Session = Depends(get_db)):
    """Admin approves or removes a flagged meme."""
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
    return {"meme_id": meme.id, "status": meme.moderation_status}
