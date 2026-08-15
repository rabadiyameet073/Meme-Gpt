import json
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import (
    Meme,
    MemeVote,
    FavouriteMeme as FavoriteMeme,
    SessionLocal,
    get_db,
)
from app.models.feedback import FeedbackRequest, VoteRequest, FavoriteRequest
from app.models.meme import ExportRequest
from app.meme_matcher import export_markdown, export_txt

logger = logging.getLogger("memegpt.api.feedback")
router = APIRouter(tags=["Feedback & Interactions"])


def _record_feedback_background(meme_id: str, signal: str, fmt: str = "image"):
    """Background task for updating meme viral score and usage counters."""
    db = SessionLocal()
    try:
        meme = db.query(Meme).filter(Meme.id == meme_id).first()
        if meme:
            if signal == "upvote":
                meme.upvotes += 1
            elif signal == "downvote":
                meme.downvotes += 1
            elif signal == "copy":
                meme.viral_score += 0.5
                meme.usage_count += 1
            elif signal == "download":
                meme.viral_score += 1.0
                meme.usage_count += 1
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
    """Logs user actions (copy, download, upvote, downvote, share) to train recommendation ranking."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    signal = body.get_signal()
    background_tasks.add_task(
        _record_feedback_background,
        body.meme_id,
        signal,
        body.format or "image"
    )
    return {
        "status": "recorded",
        "meme_id": body.meme_id,
        "signal": signal,
        "success": True
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
