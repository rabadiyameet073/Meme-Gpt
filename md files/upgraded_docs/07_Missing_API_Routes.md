# 07 — Missing API Routes
# /categories, /stats, /admin/memes, /favorites — Full Implementation

> **Gap Source:** Sections 10 & 18 of GAP_ANALYSIS_FULL.md  
> **Priority:** P0 (frontend calls these and gets 404 errors)  
> **Files to create:**  
> - `d:\Meme GPT\backend\app\api\v1\categories.py` (NEW)  
> - `d:\Meme GPT\backend\app\api\v1\admin.py` (NEW)  
> - Fix `d:\Meme GPT\backend\app\api\v1\collections.py` (complete stub)  
> - Fix `d:\Meme GPT\backend\app\api\v1\__init__.py` (register new routers)  
> - Fix `d:\Meme GPT\backend\app\main.py` (add `/api/stats` and `/api/categories`)

---

## 1. CREATE `categories.py`

**Create new file:** `d:\Meme GPT\backend\app\api\v1\categories.py`

```python
"""
MemeGPT — Categories & Stats Endpoints.

Frontend api.ts calls:
  GET /api/categories  → list of all meme categories
  GET /api/stats       → platform statistics

Gap Analysis: These routes were missing, causing 404 errors.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, Meme, SearchLog, Feedback

logger = logging.getLogger("memegpt.api.categories")

router = APIRouter(tags=["Categories & Stats"])


@router.get("/categories", summary="List all meme categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Returns all unique meme categories.
    Frontend uses this to populate category filter chips.
    """
    try:
        memes = db.query(Meme).all()

        categories = set()
        for meme in memes:
            # Handle both old (string) and new (JSON array) category format
            if isinstance(meme.categories, list):
                categories.update(meme.categories)
            elif hasattr(meme, "category") and meme.category:
                categories.add(meme.category)

        sorted_categories = sorted(categories)
        return sorted_categories

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        # Return sensible defaults if DB fails
        return [
            "coding", "work", "college", "gaming", "relationships",
            "money", "food", "general", "reaction", "wholesome"
        ]


@router.get("/stats", summary="Platform statistics")
def get_stats(db: Session = Depends(get_db)):
    """
    Returns platform-level statistics for admin dashboard / health check.
    Frontend calls GET /api/stats.
    """
    try:
        total_memes = db.query(func.count(Meme.id)).scalar() or 0
        total_searches = db.query(func.count(SearchLog.id)).scalar() or 0
        total_feedback = db.query(func.count(Feedback.id)).scalar() or 0

        # Count memes with actual media (not NULL image URL)
        memes_with_images = db.query(func.count(Meme.id)).filter(
            (Meme.image_url.isnot(None)) | (Meme.image_ref.isnot(None))
        ).scalar() or 0

        return {
            "total_memes": total_memes,
            "memes_with_images": memes_with_images,
            "total_searches": total_searches,
            "total_feedback": total_feedback,
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {"total_memes": 0, "total_searches": 0, "version": "1.0.0"}
```

---

## 2. CREATE `admin.py`

**Create new file:** `d:\Meme GPT\backend\app\api\v1\admin.py`

```python
"""
MemeGPT — Admin Meme Management Endpoints.

Frontend api.ts calls:
  POST   /api/admin/memes       → create meme
  DELETE /api/admin/memes/{id}  → delete meme
  GET    /api/admin/memes        → list all memes (admin view)

Gap Analysis: These routes were missing entirely.
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, Meme
from app.core.auth import AuthContext, require_admin, get_api_tier

logger = logging.getLogger("memegpt.api.admin")

router = APIRouter(prefix="/admin", tags=["Admin — Meme Management"])


class CreateMemeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    category: str = "general"
    categories: list[str] = []
    emotions: list[str] = []
    dialogue: str = ""
    explanation: str = ""
    keywords: list[str] = []
    image_url: Optional[str] = None
    gif_url: Optional[str] = None
    mp4_url: Optional[str] = None
    thumb_url: Optional[str] = None
    source: str = "manual"
    nsfw: bool = False


class UpdateMemeRequest(BaseModel):
    name: Optional[str] = None
    categories: Optional[list[str]] = None
    emotions: Optional[list[str]] = None
    dialogue: Optional[str] = None
    explanation: Optional[str] = None
    keywords: Optional[list[str]] = None
    image_url: Optional[str] = None
    gif_url: Optional[str] = None
    mp4_url: Optional[str] = None
    nsfw: Optional[bool] = None
    popularity_score: Optional[float] = None


@router.get("/memes", summary="List all memes (admin)")
def list_all_memes(
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier),
):
    """Returns paginated list of all memes for admin panel."""
    offset = (page - 1) * limit
    total = db.query(Meme).count()
    memes = db.query(Meme).offset(offset).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "memes": [m.to_dict() for m in memes],
    }


@router.post("/memes", summary="Create a new meme")
def create_meme(
    body: CreateMemeRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier),
):
    """
    Create a new meme record.
    Frontend calls POST /api/admin/memes.
    """
    # Check slug uniqueness
    existing = db.query(Meme).filter(Meme.slug == body.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Slug '{body.slug}' already exists")

    meme_id = str(uuid.uuid4())[:8]
    categories = body.categories or ([body.category] if body.category else ["general"])

    new_meme = Meme(
        id=meme_id,
        name=body.name,
        slug=body.slug,
        categories=categories,
        emotions=body.emotions,
        dialogue=body.dialogue,
        explanation=body.explanation,
        keywords=body.keywords,
        image_url=body.image_url,
        image_ref=body.image_url,  # Keep refs in sync
        gif_url=body.gif_url,
        gif_ref=body.gif_url,
        mp4_url=body.mp4_url,
        video_ref=body.mp4_url,
        thumb_url=body.thumb_url,
        source=body.source,
        nsfw=body.nsfw,
    )

    db.add(new_meme)
    db.commit()
    db.refresh(new_meme)

    logger.info(f"Created meme: {meme_id} ({body.name})")
    return {"success": True, "meme": new_meme.to_dict()}


@router.patch("/memes/{meme_id}", summary="Update meme fields")
def update_meme(
    meme_id: str,
    body: UpdateMemeRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier),
):
    """Update specific fields of a meme."""
    meme = db.query(Meme).filter(Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    update_data = body.dict(exclude_none=True)
    for field, value in update_data.items():
        setattr(meme, field, value)

    db.commit()
    db.refresh(meme)
    return {"success": True, "meme": meme.to_dict()}


@router.delete("/memes/{meme_id}", summary="Delete a meme")
def delete_meme(
    meme_id: str,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier),
):
    """
    Delete a meme by ID.
    Frontend calls DELETE /api/admin/memes/{id}.
    Also removes from Qdrant if connected.
    """
    meme = db.query(Meme).filter(Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    meme_name = meme.name
    db.delete(meme)
    db.commit()

    # Also remove from Qdrant
    try:
        from app.services.search_service import get_qdrant_client, COLLECTION_NAME, _meme_id_to_int
        client = get_qdrant_client()
        if client:
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=[_meme_id_to_int(meme_id)],
            )
    except Exception as e:
        logger.warning(f"Failed to remove meme {meme_id} from Qdrant: {e}")

    logger.info(f"Deleted meme: {meme_id} ({meme_name})")
    return {"success": True, "deleted_id": meme_id}
```

---

## 3. FIX `collections.py` (Favorites)

**Replace stub** in `d:\Meme GPT\backend\app\api\v1\collections.py`:

```python
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
```

---

## 4. REGISTER NEW ROUTERS in `__init__.py`

In `d:\Meme GPT\backend\app\api\v1\__init__.py`, add the new imports and includes:

```python
# Add these imports at the top:
from app.api.v1.categories import router as categories_router
from app.api.v1.admin import router as admin_router

# Add these includes after the existing ones:
v1_router.include_router(categories_router)
v1_router.include_router(admin_router)
```

---

## 5. ADD ROUTES TO `main.py` LEGACY PATHS

The frontend calls `/api/categories` and `/api/stats` (NOT `/api/v1/...`).  
In `d:\Meme GPT\backend\app\main.py`, add these legacy route mounts:

```python
# After creating the app, mount legacy /api paths that frontend expects:
from app.api.v1.categories import get_categories, get_stats

@app.get("/api/categories")
def legacy_categories(db: Session = Depends(get_db)):
    return get_categories(db)

@app.get("/api/stats")
def legacy_stats(db: Session = Depends(get_db)):
    return get_stats(db)

@app.get("/api/favorites")
def legacy_favorites(sessionId: str = Query(default=""), db: Session = Depends(get_db)):
    from app.api.v1.collections import get_favorites
    return get_favorites(sessionId, db)

@app.post("/api/favorites/toggle")
def legacy_toggle(body: dict, db: Session = Depends(get_db)):
    from app.api.v1.collections import toggle_favorite, ToggleFavoriteRequest
    return toggle_favorite(ToggleFavoriteRequest(**body))
```

---

## VERIFICATION

Test all routes after implementation:

```bash
# Start server
cd "d:\Meme GPT\backend"
uvicorn app.main:app --reload --port 8000

# In another terminal:
curl http://localhost:8000/api/categories
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/favorites?sessionId=test123
curl -X POST http://localhost:8000/api/favorites/toggle \
  -H "Content-Type: application/json" \
  -d '{"memeId":"meme1","sessionId":"test123"}'
```

All should return JSON (not 404).
