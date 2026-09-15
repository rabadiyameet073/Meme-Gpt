"""
MemeGPT User Collections API
Supports creating custom folders (e.g. 'Monday Reactions', 'Work Memes')
and adding/removing memes from collections.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db, User, SavedMeme, Meme
from app.core.auth import get_current_user

router = APIRouter()


class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    meme_ids: List[str] = Field(default_factory=list)


class CollectionItem(BaseModel):
    id: str
    meme_id: str
    meme_name: str
    meme_slug: str
    meme_url: str
    added_at: str


class CollectionSummary(BaseModel):
    collection_name: str
    item_count: int
    cover_image_url: Optional[str] = None


@router.get("/collections", response_model=List[CollectionSummary], summary="List all user collections")
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(SavedMeme).filter(SavedMeme.user_id == current_user.id).all()
    grouped = {}
    for item in items:
        c_name = item.collection_name or "Favorites"
        if c_name not in grouped:
            grouped[c_name] = []
        grouped[c_name].append(item)

    summaries = []
    for name, list_items in grouped.items():
        cover = None
        if list_items:
            first_meme = db.query(Meme).filter(Meme.id == list_items[0].meme_id).first()
            if first_meme:
                cover = first_meme.thumb_url or first_meme.image_url
        summaries.append(CollectionSummary(
            collection_name=name,
            item_count=len(list_items),
            cover_image_url=cover
        ))
    return summaries


@router.post("/collections/{collection_name}/items/{meme_id}", status_code=status.HTTP_201_CREATED)
async def add_to_collection(
    collection_name: str,
    meme_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meme = db.query(Meme).filter((Meme.id == meme_id) | (Meme.slug == meme_id)).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    existing = db.query(SavedMeme).filter(
        SavedMeme.user_id == current_user.id,
        SavedMeme.meme_id == meme.id,
        SavedMeme.collection_name == collection_name
    ).first()

    if existing:
        return {"status": "already_exists", "message": "Meme already in collection"}

    saved = SavedMeme(
        user_id=current_user.id,
        meme_id=meme.id,
        collection_name=collection_name
    )
    db.add(saved)
    db.commit()
    return {"status": "success", "message": f"Added to {collection_name}"}


@router.delete("/collections/{collection_name}/items/{meme_id}")
async def remove_from_collection(
    collection_name: str,
    meme_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meme = db.query(Meme).filter((Meme.id == meme_id) | (Meme.slug == meme_id)).first()
    target_id = meme.id if meme else meme_id

    saved = db.query(SavedMeme).filter(
        SavedMeme.user_id == current_user.id,
        SavedMeme.meme_id == target_id,
        SavedMeme.collection_name == collection_name
    ).first()

    if not saved:
        raise HTTPException(status_code=404, detail="Item not found in collection")

    db.delete(saved)
    db.commit()
    return {"status": "success", "message": "Removed from collection"}


@router.post("/collections", status_code=status.HTTP_201_CREATED, summary="Create a new collection")
async def create_collection(
    body: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Collection name cannot be empty")

    for meme_id in body.meme_ids:
        meme = db.query(Meme).filter((Meme.id == meme_id) | (Meme.slug == meme_id)).first()
        if meme:
            existing = db.query(SavedMeme).filter(
                SavedMeme.user_id == current_user.id,
                SavedMeme.meme_id == meme.id,
                SavedMeme.collection_name == body.name.strip()
            ).first()
            if not existing:
                saved = SavedMeme(
                    user_id=current_user.id,
                    meme_id=meme.id,
                    collection_name=body.name.strip()
                )
                db.add(saved)
    db.commit()
    return {
        "status": "success",
        "message": f"Collection '{body.name.strip()}' created",
        "collection_name": body.name.strip(),
    }


@router.get("/collections/{collection_name}", summary="Get all memes in a collection")
async def get_collection(
    collection_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(SavedMeme).filter(
        SavedMeme.user_id == current_user.id,
        SavedMeme.collection_name == collection_name
    ).all()

    meme_ids = [item.meme_id for item in items]
    memes = db.query(Meme).filter(Meme.id.in_(meme_ids)).all() if meme_ids else []

    return {
        "collection_name": collection_name,
        "item_count": len(items),
        "items": [m.to_dict() for m in memes]
    }


@router.delete("/collections/{collection_name}", summary="Delete an entire collection")
async def delete_collection(
    collection_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(SavedMeme).filter(
        SavedMeme.user_id == current_user.id,
        SavedMeme.collection_name == collection_name
    ).all()

    for item in items:
        db.delete(item)
    db.commit()

    return {
        "status": "success",
        "message": f"Deleted collection '{collection_name}'",
        "deleted_count": len(items)
    }

