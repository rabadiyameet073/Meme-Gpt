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
            detail=f"Unsupported format '{format}'. Allowed formats: {', '.join(sorted(ALLOWED_FORMATS))}"
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
        meme.download_count = (meme.download_count or 0) + 1
        meme.usage_count = (meme.usage_count or 0) + 1
        usage_record = MemeUsage(
            meme_id=meme.id,
            query=f"download:{fmt}",
            session_id=request.headers.get("user-agent", "api")[:64],
            confidence=1.0,
        )
        db.add(usage_record)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to record download telemetry for {slug}: {e}")
        db.rollback()

    # 4. HTTP 307 Temporary Redirect to preserve caching and forward to CDN
    return RedirectResponse(url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
