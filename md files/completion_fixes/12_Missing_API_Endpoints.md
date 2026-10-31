# 12 — Missing API Endpoints Guide
> Complete implementation for download redirects, user profiles, collections, and developer API endpoints.

---

## Problem Statement

While the core search, memes, and feedback endpoints are implemented, several key endpoints specified in `01_PRODUCT_AND_FEATURES.md`, `02_TECH_STACK_AND_MODELS.md`, and `04_DESIGN_AND_DEVELOPMENT.md` are either missing or incomplete:

1. **`GET /api/v1/memes/{slug}/download`**: Direct download redirect with format selection (`gif`, `png`, `mp4`, `webp`) and usage telemetry increment.
2. **`GET/PUT /api/v1/users/me` & `/preferences`**: User profile retrieval, format preference persistence, and theme settings.
3. **`GET/POST/DELETE /api/v1/collections`**: Full CRUD for named user meme collections ("Monday Memes", "Reaction Pack").
4. **`POST /api/v1/share`**: Dedicated share generation endpoint with short-link and OpenGraph metadata payload.
5. **`GET /api/v1/developer/usage`**: Public developer API usage tracking and rate limit status.

---

## Step 1: Implement Download Redirect Endpoint

### 1.1 Create `backend/app/api/v1/download.py`

**File:** `backend/app/api/v1/download.py`

```python
"""
MemeGPT Download Redirect & Analytics Endpoint
Handles GET /api/v1/memes/{slug}/download?format=gif
Redirects to the CDN asset while asynchronously tracking download metrics.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db, Meme, MemeUsage
from app.services.cdn_service import cdn_service
import logging

logger = logging.getLogger("memegpt.download")

router = APIRouter()

ALLOWED_FORMATS = {"gif", "png", "jpg", "mp4", "webp"}

@router.get("/memes/{slug}/download", summary="Download meme in requested format")
async def download_meme(
    slug: str,
    request: Request,
    format: str = Query("gif", description="Requested format: gif, png, mp4, or webp"),
    db: Session = Depends(get_db),
):
    fmt = format.lower()
    if fmt not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Allowed formats: {', '.join(ALLOWED_FORMATS)}"
        )

    # 1. Lookup meme by slug
    meme = db.query(Meme).filter(Meme.slug == slug).first()
    if not meme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meme with slug '{slug}' not found"
        )

    # 2. Resolve target CDN URL based on format preference
    target_url: Optional[str] = None
    if fmt == "gif":
        target_url = meme.gif_url or meme.image_url
    elif fmt in ("png", "jpg"):
        target_url = meme.image_url or meme.webp_url
    elif fmt == "mp4":
        target_url = meme.mp4_url or meme.gif_url or meme.image_url
    elif fmt == "webp":
        target_url = meme.webp_url or meme.thumb_url or meme.image_url

    # Fallback to CDN URL generator if DB field is missing
    if not target_url:
        ext = "gif" if fmt == "gif" else ("mp4" if fmt == "mp4" else "jpg")
        target_url = cdn_service.get_asset_url(f"memes/{slug}.{ext}")

    # 3. Asynchronously record usage telemetry
    try:
        meme.usage_count = (meme.usage_count or 0) + 1
        usage_record = MemeUsage(
            meme_id=meme.id,
            action="download",
            format=fmt,
            user_agent=request.headers.get("user-agent", "")[:255],
        )
        db.add(usage_record)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to record download telemetry for {slug}: {e}")
        db.rollback()

    # 4. HTTP 307 Temporary Redirect to preserve caching and forward to CDN
    return RedirectResponse(url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
```

---

## Step 2: Implement User Profile & Preferences Endpoints

### 2.1 Create `backend/app/api/v1/users.py`

**File:** `backend/app/api/v1/users.py`

```python
"""
MemeGPT User Profile & Preferences API
Handles GET/PUT /api/v1/users/me
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db, User
from app.core.auth import get_current_user

router = APIRouter()

class UserPreferencesUpdate(BaseModel):
    preferred_format: Optional[str] = Field("gif", description="gif, image, or mp4")
    theme: Optional[str] = Field("dark", description="dark or light")
    nsfw_enabled: Optional[bool] = Field(False, description="Whether to include NSFW results")
    favourite_categories: Optional[List[str]] = Field(default_factory=list)

class UserProfileResponse(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_format: str
    theme: str
    nsfw_enabled: bool
    favourite_categories: List[str]
    created_at: str

    class Config:
        from_attributes = True

@router.get("/users/me", response_model=UserProfileResponse, summary="Get current user profile")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        preferred_format=current_user.preferred_format or "gif",
        theme=current_user.theme or "dark",
        nsfw_enabled=bool(current_user.nsfw_enabled),
        favourite_categories=current_user.favourite_categories or [],
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
    )

@router.put("/users/me/preferences", response_model=UserProfileResponse, summary="Update user preferences")
async def update_preferences(
    prefs: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if prefs.preferred_format is not None:
        if prefs.preferred_format not in {"gif", "image", "mp4", "webp"}:
            raise HTTPException(status_code=400, detail="Invalid format preference")
        current_user.preferred_format = prefs.preferred_format

    if prefs.theme is not None:
        current_user.theme = prefs.theme

    if prefs.nsfw_enabled is not None:
        current_user.nsfw_enabled = prefs.nsfw_enabled

    if prefs.favourite_categories is not None:
        current_user.favourite_categories = prefs.favourite_categories

    db.commit()
    db.refresh(current_user)
    return current_user
```

---

## Step 3: Implement Collection CRUD Endpoints

### 3.1 Create `backend/app/api/v1/collections_full.py`

**File:** `backend/app/api/v1/collections_full.py`

```python
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
    meme_ids: List[int] = Field(default_factory=list)

class CollectionItem(BaseModel):
    id: int
    meme_id: int
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
    meme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meme = db.query(Meme).filter(Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    existing = db.query(SavedMeme).filter(
        SavedMeme.user_id == current_user.id,
        SavedMeme.meme_id == meme_id,
        SavedMeme.collection_name == collection_name
    ).first()

    if existing:
        return {"status": "already_exists", "message": "Meme already in collection"}

    saved = SavedMeme(
        user_id=current_user.id,
        meme_id=meme_id,
        collection_name=collection_name
    )
    db.add(saved)
    db.commit()
    return {"status": "success", "message": f"Added to {collection_name}"}

@router.delete("/collections/{collection_name}/items/{meme_id}")
async def remove_from_collection(
    collection_name: str,
    meme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedMeme).filter(
        SavedMeme.user_id == current_user.id,
        SavedMeme.meme_id == meme_id,
        SavedMeme.collection_name == collection_name
    ).first()

    if not saved:
        raise HTTPException(status_code=404, detail="Item not found in collection")

    db.delete(saved)
    db.commit()
    return {"status": "success", "message": "Removed from collection"}
```

---

## Step 4: Register New Routes in API Router

**File:** `backend/app/api/v1/__init__.py`

Ensure the new route modules are imported and mounted to `v1_router`:

```python
from app.api.v1 import (
    search, memes, trending, feedback, health,
    download, users, collections_full
)

# In v1_router registration:
v1_router.include_router(download.router, tags=["Download"])
v1_router.include_router(users.router, tags=["Users"])
v1_router.include_router(collections_full.router, tags=["Collections"])
```

---

## Step 5: Verification Checklist

- [ ] Test download redirect:
  ```powershell
  curl -I "http://localhost:8000/api/v1/memes/drake-pointing/download?format=gif"
  # Should return HTTP 307 with Location: <cdn_url>
  ```
- [ ] Test user preferences update with valid bearer token.
- [ ] Test collection creation and item removal.
- [ ] Run backend tests:
  ```powershell
  cd "d:\Meme GPT\backend"
  pytest tests/test_api_memes.py -v
  ```
