"""
MemeGPT — Favorites & Collections Endpoints (FIXED & FULL SPECIFICATION).

Provides full collection management, anonymous session favorites,
recently viewed/copied limits, and storage quotas.
Specifications:
  - 08_Features/Favorites_Collections.md
  - 07_Missing_API_Routes.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, Meme
from app.services.favorites_service import (
    create_collection as svc_create_collection,
    list_collections as svc_list_collections,
    delete_collection as svc_delete_collection,
    save_meme_to_collection as svc_save_meme,
    remove_meme_from_collection as svc_remove_meme,
    list_saved_memes as svc_list_saved_memes,
    add_recently_viewed as svc_add_recently_viewed,
    add_recently_copied as svc_add_recently_copied,
    get_favorites_storage_limits as svc_get_storage_limits,
    _USER_STORAGE,
)

logger = logging.getLogger("memegpt.api.collections")
router = APIRouter(tags=["Favorites & Collections"])

_session_favorites: dict[str, set[str]] = {}


class ToggleFavoriteRequest(BaseModel):
    memeId: str
    sessionId: str


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = "folder"


class SaveMemeToCollectionRequest(BaseModel):
    meme_id: str
    name: str = ""
    thumbnail_url: str = ""
    collection: str = "Favorites"


# ── Legacy & Simple Favorites Endpoints ───────────────────────────────────────

@router.get("/favorites", summary="Get saved memes for session")
def get_favorites(
    sessionId: str = Query("", description="Anonymous session ID"),
    session_id: str = Query("", description="Session ID alternative"),
    db: Session = Depends(get_db),
):
    """Returns list of memes saved by this session."""
    sid = sessionId or session_id or "anonymous"
    meme_ids = list(_session_favorites.get(sid, set()))

    # Also check user storage
    user_store = _USER_STORAGE.get(sid, {})
    saved_in_store = [m.get("memeId") for m in user_store.get("saved_memes", []) if m.get("memeId")]
    all_ids = list(dict.fromkeys(meme_ids + saved_in_store))

    if not all_ids:
        return []

    memes = db.query(Meme).filter(Meme.id.in_(all_ids)).all()
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
        try:
            svc_remove_meme(user_id=session_id, meme_id=meme_id)
        except Exception:
            pass
    else:
        favorites.add(meme_id)
        is_favorite = True
        try:
            svc_save_meme(user_id=session_id, meme_id=meme_id, name="Saved Meme")
        except Exception:
            pass

    return {"isFavorite": is_favorite, "memeId": meme_id}


# ── Extended Collections Endpoints ────────────────────────────────────────────

@router.get("/collections", summary="List collections")
def list_collections(
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
):
    sid = sessionId or session_id or "anonymous"
    return svc_list_collections(user_id=sid)


@router.post("/collections", summary="Create custom collection")
def create_collection(
    body: CreateCollectionRequest,
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
):
    sid = sessionId or session_id or "anonymous"
    try:
        return svc_create_collection(user_id=sid, name=body.name, icon=body.icon)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/collections/{name}", summary="Delete custom collection")
def delete_collection(
    name: str,
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
):
    sid = sessionId or session_id or "anonymous"
    try:
        return svc_delete_collection(user_id=sid, name=name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/collections/memes", summary="Save meme to collection")
def save_meme_to_collection(
    body: SaveMemeToCollectionRequest,
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
):
    sid = sessionId or session_id or "anonymous"
    return svc_save_meme(
        user_id=sid,
        meme_id=body.meme_id,
        name=body.name,
        thumbnail_url=body.thumbnail_url,
        collection=body.collection,
    )


@router.delete("/collections/memes/{meme_id}", summary="Remove meme from collection")
def remove_meme_from_collection(
    meme_id: str,
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
    collection: str = Query("Favorites", description="Collection name"),
):
    sid = sessionId or session_id or "anonymous"
    return svc_remove_meme(user_id=sid, meme_id=meme_id, collection=collection)


@router.get("/collections/recent-viewed", summary="List recently viewed memes")
def get_recently_viewed(
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
):
    sid = sessionId or session_id or "anonymous"
    store = _USER_STORAGE.get(sid, {})
    return {"recent_viewed": store.get("recent_viewed", [])}


@router.get("/collections/recent-copied", summary="List recently copied memes")
def get_recently_copied(
    session_id: str = Query("anonymous", description="Session / User ID"),
    sessionId: str = Query("", description="Alternative Session ID"),
):
    sid = sessionId or session_id or "anonymous"
    store = _USER_STORAGE.get(sid, {})
    return {"recent_copied": store.get("recent_copied", [])}


@router.get("/collections/storage-limits", summary="Get storage capacity and limits")
def get_storage_limits():
    return {"limits": svc_get_storage_limits()}
