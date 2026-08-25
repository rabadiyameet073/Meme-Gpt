"""
MemeGPT — Favorites / Collections Endpoints (FIXED).

Frontend api.ts calls:
  GET  /api/favorites?sessionId={id}   → list saved memes
  POST /api/favorites/toggle            → save or unsave a meme

Gap Analysis: These were stubs, not functional.
"""

import logging
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, Meme

logger = logging.getLogger("memegpt.api.collections")
router = APIRouter(tags=["Favorites"])

# In-memory store for anonymous session favorites (no auth required)
# In production: replace with DB table (saved_memes)
_session_favorites: dict[str, set[str]] = {}


class ToggleFavoriteRequest(BaseModel):
    memeId: str
    sessionId: str


@router.get("/favorites", summary="Get saved memes for session")
def get_favorites(
    sessionId: str = Query(..., description="Anonymous session ID"),
    db: Session = Depends(get_db),
):
    """Returns list of memes saved by this session."""
    meme_ids = list(_session_favorites.get(sessionId, set()))

    if not meme_ids:
        return []

    memes = db.query(Meme).filter(Meme.id.in_(meme_ids)).all()
    return [m.to_dict() for m in memes]


@router.post("/favorites/toggle", summary="Save or unsave a meme")
def toggle_favorite(body: ToggleFavoriteRequest):
    """
    Toggle meme in session favorites.
    Returns {isFavorite: bool}.
    """
    session_id = body.sessionId
    meme_id = body.memeId

    if session_id not in _session_favorites:
        _session_favorites[session_id] = set()

    favorites = _session_favorites[session_id]

    if meme_id in favorites:
        favorites.remove(meme_id)
        is_favorite = False
    else:
        favorites.add(meme_id)
        is_favorite = True

    return {"isFavorite": is_favorite, "memeId": meme_id}
