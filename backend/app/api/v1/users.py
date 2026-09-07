"""
MemeGPT User Profile & Preferences API
Handles GET/PUT /api/v1/users/me and preferences
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db, User
from app.core.auth import get_current_user

router = APIRouter()


class UserPreferencesUpdate(BaseModel):
    preferred_format: Optional[str] = Field("gif", description="gif, image, mp4, or webp")
    theme: Optional[str] = Field("dark", description="dark or light")
    nsfw_enabled: Optional[bool] = Field(False, description="Whether to include NSFW results")
    favourite_categories: Optional[List[str]] = Field(default_factory=list)


class UserProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    plan: Optional[str] = "free"
    preferred_format: str
    theme: str
    nsfw_enabled: bool
    favourite_categories: List[str]
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/users/me", response_model=UserProfileResponse, summary="Get current user profile")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username or current_user.name,
        avatar_url=current_user.avatar_url,
        plan=current_user.plan or "free",
        preferred_format=current_user.preferred_format or "gif",
        theme=current_user.theme or "dark",
        nsfw_enabled=bool(current_user.nsfw_enabled),
        favourite_categories=current_user.favourite_categories or [],
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
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

    # Sync into preferences JSON dictionary as well
    prefs_dict = current_user.preferences or {}
    prefs_dict["preferred_format"] = current_user.preferred_format
    prefs_dict["theme"] = current_user.theme
    prefs_dict["nsfw_enabled"] = current_user.nsfw_enabled
    prefs_dict["favourite_categories"] = current_user.favourite_categories
    current_user.preferences = prefs_dict

    db.commit()
    db.refresh(current_user)

    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username or current_user.name,
        avatar_url=current_user.avatar_url,
        plan=current_user.plan or "free",
        preferred_format=current_user.preferred_format or "gif",
        theme=current_user.theme or "dark",
        nsfw_enabled=bool(current_user.nsfw_enabled),
        favourite_categories=current_user.favourite_categories or [],
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
    )
