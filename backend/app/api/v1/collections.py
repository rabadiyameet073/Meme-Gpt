"""Collections and Favorites API Router for MemeGPT.
Specification: 08_Features/Favorites_Collections.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.auth import AuthContext, optional_auth
from app.services.favorites_service import (
    list_collections,
    create_collection,
    delete_collection,
    save_meme_to_collection,
    remove_meme_from_collection,
    list_saved_memes,
    add_recently_viewed,
    add_recently_copied,
    get_recently_viewed,
    get_recently_copied,
    get_favorites_storage_limits,
)

logger = logging.getLogger("memegpt.api.collections")
router = APIRouter(prefix="/collections", tags=["Favorites & Collections"])


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Collection name")
    icon: str = Field(default="folder", description="Icon identifier (e.g. star, folder, clock)")


class SaveMemeRequest(BaseModel):
    meme_id: str = Field(..., description="Unique meme ID")
    name: str = Field(default="", description="Meme name")
    thumbnail_url: str = Field(default="", description="Thumbnail URL")
    collection: str = Field(default="Favorites", description="Target collection name")


class RecentMemeRequest(BaseModel):
    meme_id: str = Field(..., description="Unique meme ID")
    name: str = Field(default="", description="Meme name")
    thumbnail_url: str = Field(default="", description="Thumbnail URL")


def _get_caller_id(auth: AuthContext, session_id: Optional[str] = None) -> str:
    if auth and auth.user_id:
        return auth.user_id
    if auth and auth.key_id:
        return auth.key_id
    if session_id:
        return session_id
    return "anonymous_device"


@router.get("", summary="List all collections")
def get_user_collections(
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """List all custom and default collections for user/session."""
    user_id = _get_caller_id(auth, session_id)
    cols = list_collections(user_id=user_id)
    return {
        "success": True,
        "collections": cols,
        "total": len(cols),
    }


@router.post("", summary="Create custom collection")
def create_user_collection(
    body: CreateCollectionRequest,
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """Create a new named collection."""
    user_id = _get_caller_id(auth, session_id)
    try:
        col = create_collection(user_id=user_id, name=body.name, icon=body.icon)
        return {
            "success": True,
            "collection": col,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{name}", summary="Delete custom collection")
def delete_user_collection(
    name: str,
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """Delete a custom collection. Contained memes are automatically moved to 'Favorites'."""
    user_id = _get_caller_id(auth, session_id)
    try:
        res = delete_collection(user_id=user_id, name=name)
        return {
            "success": True,
            **res,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/memes", summary="List saved memes")
def get_saved_memes(
    collection: Optional[str] = Query(None, description="Filter by collection name"),
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """List memes saved in a collection or all favorites."""
    user_id = _get_caller_id(auth, session_id)
    memes = list_saved_memes(user_id=user_id, collection=collection)
    return {
        "success": True,
        "collection": collection or "All",
        "saved_memes": memes,
        "total": len(memes),
    }


@router.post("/memes", summary="Save meme to collection")
def save_meme(
    body: SaveMemeRequest,
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """Save a meme to a collection with duplicate timestamp updating."""
    user_id = _get_caller_id(auth, session_id)
    res = save_meme_to_collection(
        user_id=user_id,
        meme_id=body.meme_id,
        name=body.name,
        thumbnail_url=body.thumbnail_url,
        collection=body.collection,
    )
    return {
        "success": True,
        **res,
    }


@router.delete("/memes/{meme_id}", summary="Remove meme from collection")
def remove_saved_meme(
    meme_id: str,
    collection: Optional[str] = Query(None, description="Specific collection name to remove from"),
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """Remove a saved meme from favorites or a collection."""
    user_id = _get_caller_id(auth, session_id)
    removed = remove_meme_from_collection(user_id=user_id, meme_id=meme_id, collection=collection)
    return {
        "success": True,
        "removed": removed,
        "meme_id": meme_id,
    }


@router.get("/recent-viewed", summary="List recently viewed memes")
def list_recent_viewed(
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """List up to 20 recently viewed memes."""
    user_id = _get_caller_id(auth, session_id)
    recent = get_recently_viewed(user_id=user_id)
    return {
        "success": True,
        "recent_viewed": recent,
        "total": len(recent),
    }


@router.post("/recent-viewed", summary="Record viewed meme")
def record_recent_viewed(
    body: RecentMemeRequest,
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """Record meme viewing event into recent viewed list."""
    user_id = _get_caller_id(auth, session_id)
    recent = add_recently_viewed(
        user_id=user_id,
        meme_id=body.meme_id,
        name=body.name,
        thumbnail_url=body.thumbnail_url,
    )
    return {
        "success": True,
        "recent_viewed": recent,
        "total": len(recent),
    }


@router.get("/recent-copied", summary="List recently copied memes")
def list_recent_copied(
    session_id: Optional[str] = Query(None, description="Client session ID"),
    auth: AuthContext = Depends(optional_auth),
):
    """List up to 10 recently copied memes."""
    user_id = _get_caller_id(auth, session_id)
    recent = get_recently_copied(user_id=user_id)
    return {
        "success": True,
        "recent_copied": recent,
        "total": len(recent),
    }


@router.get("/storage-limits", summary="Get storage capacity and limits")
def get_limits():
    """Retrieve storage capacity and policy limits."""
    return {
        "success": True,
        "limits": get_favorites_storage_limits(),
    }
