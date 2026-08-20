import json
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import (
    Meme,
    MemeVote,
    Feedback,
    FavouriteMeme as FavoriteMeme,
    SessionLocal,
    get_db,
)
from app.models.feedback import FeedbackRequest, VoteRequest, FavoriteRequest
from app.models.meme import ExportRequest
from app.meme_matcher import export_markdown, export_txt

logger = logging.getLogger("memegpt.api.feedback")
router = APIRouter(tags=["Feedback & Interactions"])

VALID_FEEDBACK_ACTIONS = {
    "view": 0.1,
    "click": 0.5,
    "copy": 1.0,
    "download": 2.0,
    "share": 3.0,
    "thumbs_up": 2.0,
    "thumbs_down": -1.0,
    "skip": -0.3,
}


def _record_feedback_background(
    meme_id: str,
    action: str,
    session_id: str = "anonymous",
    query_id: str = None,
    fmt: str = "image"
):
    """Background task for persisting feedback entry and updating meme viral score and usage counters."""
    db = SessionLocal()
    try:
        # 1. Insert feedback record
        feedback_entry = Feedback(
            session_id=session_id,
            meme_id=meme_id,
            query_id=query_id,
            action=action,
        )
        db.add(feedback_entry)

        # 2. Update meme metrics
        meme = db.query(Meme).filter(Meme.id == meme_id).first()
        if meme:
            weight = VALID_FEEDBACK_ACTIONS.get(action, 0.0)
            
            if action in ("copy", "download", "share"):
                meme.usage_count = (meme.usage_count or 0) + 1
            elif action == "thumbs_up":
                meme.upvotes = (meme.upvotes or 0) + 1
            elif action == "thumbs_down":
                meme.downvotes = (meme.downvotes or 0) + 1

            # Update viral score
            new_score = (meme.viral_score or 0.0) + weight
            meme.viral_score = max(0.0, round(new_score, 2))

        db.commit()
    except Exception as e:
        logger.error(f"Error in background feedback task: {e}")
        db.rollback()
    finally:
        db.close()


@router.post("/feedback", summary="Record user interaction feedback signal")
def record_feedback(
    body: FeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Records user interactions (view, click, copy, download, share, thumbs_up, thumbs_down, skip) asynchronously."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    action = body.get_action()
    if action not in VALID_FEEDBACK_ACTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{action}'. Valid actions: {list(VALID_FEEDBACK_ACTIONS.keys())}"
        )

    background_tasks.add_task(
        _record_feedback_background,
        meme_id=body.meme_id,
        action=action,
        session_id=body.session_id or "anonymous",
        query_id=body.query_id,
        fmt=body.format or "image",
    )

    return {
        "success": True,
        "message": "Feedback recorded",
        "meme_id": body.meme_id,
        "action": action,
    }


@router.post("/vote", summary="Vote on a meme result")
def vote_on_meme(body: VoteRequest, db: Session = Depends(get_db)):
    """Record thumbs up (+1) or thumbs down (-1) on a meme."""
    if body.vote not in (1, -1):
        raise HTTPException(status_code=400, detail="Vote must be 1 or -1")

    meme = db.query(Meme).filter(Meme.id == body.memeId).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    existing = (
        db.query(MemeVote)
        .filter(MemeVote.meme_id == body.memeId, MemeVote.session_id == body.sessionId)
        .first()
    )

    if existing:
        if existing.vote != body.vote:
            if existing.vote == 1:
                meme.upvotes -= 1
                meme.downvotes += 1
            else:
                meme.downvotes -= 1
                meme.upvotes += 1
            existing.vote = body.vote
    else:
        db.add(MemeVote(meme_id=body.memeId, vote=body.vote, session_id=body.sessionId))
        if body.vote == 1:
            meme.upvotes += 1
        else:
            meme.downvotes += 1

    db.commit()
    return {"success": True, "upvotes": meme.upvotes, "downvotes": meme.downvotes}


@router.get("/favorites", summary="List user favorite memes")
def list_favorites(sessionId: str, db: Session = Depends(get_db)):
    """Retrieve saved favorites for the given session ID."""
    favs = db.query(FavoriteMeme).filter(FavoriteMeme.session_id == sessionId).all()
    meme_ids = [f.meme_id for f in favs]
    memes = db.query(Meme).filter(Meme.id.in_(meme_ids)).all() if meme_ids else []
    return [m.to_dict() for m in memes]


@router.post("/favorites/toggle", summary="Toggle favorite status for a meme")
def toggle_favorite(body: FavoriteRequest, db: Session = Depends(get_db)):
    """Star or un-star a meme for a given session ID."""
    existing = (
        db.query(FavoriteMeme)
        .filter(FavoriteMeme.meme_id == body.memeId, FavoriteMeme.session_id == body.sessionId)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"isFavorite": False}
    else:
        db.add(FavoriteMeme(meme_id=body.memeId, session_id=body.sessionId))
        db.commit()
        return {"isFavorite": True}


@router.post("/export", summary="Export search results to file formats")
def export_results(body: ExportRequest):
    """Exports structured recommendation results to Markdown, Text, or JSON formats."""
    fmt = body.format.lower()
    if fmt == "txt":
        content = export_txt(body.result, body.query)
        filename = "memegpt-result.txt"
        content_type = "text/plain"
    elif fmt == "markdown":
        content = export_markdown(body.result, body.query)
        filename = "memegpt-result.md"
        content_type = "text/markdown"
    elif fmt == "json":
        content = json.dumps({"query": body.query, **body.result}, indent=2)
        filename = "memegpt-result.json"
        content_type = "application/json"
    else:
        raise HTTPException(status_code=400, detail="Format must be txt, json, or markdown")

    return {"content": content, "contentType": content_type, "filename": filename}
