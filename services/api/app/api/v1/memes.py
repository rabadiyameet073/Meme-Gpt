"""
GET /api/v1/memes          — List all memes (paginated, for sitemap)
GET /api/v1/memes/{slug}   — Meme detail
GET /api/v1/memes/{slug}/download — CDN redirect (301)
"""
import re
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import RedirectResponse
from app.models.meme import MemeDetail, MemeFormats
from app.services.cdn_service import cdn_service

router = APIRouter()

# In-memory meme store for local dev (populated by data pipeline or seed)
# In production this hits Supabase via a repository layer
_MEME_STORE: dict[str, dict] = {}


def _slug(name: str) -> str:
    return re.sub(r"[^\w-]", "", name.lower().replace(" ", "-"))


def _get_meme_by_slug(slug: str) -> dict | None:
    if slug in _MEME_STORE:
        return _MEME_STORE[slug]
    # Try loading from local search service index
    from app.services.search_service import search_service
    for meme in search_service._local_index:
        meme_slug = meme.get("slug") or _slug(meme.get("name", ""))
        if meme_slug == slug:
            return meme
    return None


@router.get("/memes")
async def list_memes(
    limit: int = Query(default=1000, ge=1, le=50000),
    offset: int = Query(default=0, ge=0),
):
    """List all memes — used by sitemap and browsing. Paginated."""
    from app.services.search_service import search_service
    all_memes = search_service._local_index or []
    total = len(all_memes)
    page = all_memes[offset: offset + limit]

    items = []
    for meme in page:
        slug = meme.get("slug") or _slug(meme.get("name", "meme"))
        items.append({
            "id": meme.get("id", slug),
            "name": meme.get("name", slug),
            "slug": slug,
            "category": meme.get("category", "general"),
            "popularity_score": meme.get("popularity_score", 0.0),
            "created_at": meme.get("created_at", None),
        })

    return {"items": items, "total": total, "offset": offset, "limit": limit}


# In-memory meme store for local dev (populated by data pipeline or seed)
# In production this hits Supabase via a repository layer
_MEME_STORE: dict[str, dict] = {}


def _slug(name: str) -> str:
    return re.sub(r"[^\w-]", "", name.lower().replace(" ", "-"))


def _get_meme_by_slug(slug: str) -> dict | None:
    if slug in _MEME_STORE:
        return _MEME_STORE[slug]
    # Try loading from local search service index
    from app.services.search_service import search_service
    for meme in search_service._local_index:
        meme_slug = meme.get("slug") or _slug(meme.get("name", ""))
        if meme_slug == slug:
            return meme
    return None


@router.get("/memes/{slug}", response_model=MemeDetail)
async def get_meme(slug: str):
    """Get full meme details by slug."""
    meme = _get_meme_by_slug(slug)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    formats_dict = cdn_service.resolve_formats(meme)
    return MemeDetail(
        id=meme.get("id", slug),
        name=meme.get("name", slug),
        slug=slug,
        description=meme.get("caption") or meme.get("explanation") or "",
        origin="",
        categories=meme.get("categories", [meme.get("category", "general")]),
        emotions=meme.get("emotions", []),
        keywords=meme.get("keywords", []),
        formats=MemeFormats(**formats_dict),
        related_memes=[],
        usage_count=meme.get("usage_count", meme.get("usageCount", 0)),
        download_count=meme.get("download_count", 0),
        popularity_score=meme.get("popularity_score", 0.0),
        nsfw=meme.get("nsfw", False),
        source=meme.get("source", "manual"),
    )


@router.get("/memes/{slug}/download")
async def download_meme(
    slug: str,
    format: str = Query(default="gif", pattern="^(gif|image|png|mp4|video|webp)$"),
    background_tasks: BackgroundTasks = None,
):
    """Redirect to CDN file. Logs download signal as background task."""
    fmt = format.lower()
    meme = _get_meme_by_slug(slug)

    if fmt in ("gif",):
        url = (meme.get("gif_url") if meme else None) or cdn_service.get_gif_url(slug)
    elif fmt in ("mp4", "video"):
        url = (meme.get("mp4_url") if meme else None) or cdn_service.get_mp4_url(slug)
    elif fmt in ("webp", "thumb"):
        url = (meme.get("thumb_url") if meme else None) or cdn_service.get_thumb_url(slug)
    else:
        url = (meme.get("image_url") if meme else None) or cdn_service.get_image_url(slug)

    # Log download signal asynchronously
    if background_tasks and meme:
        from app.services.cdn_service import cdn_service as _cdn
        meme_id = meme.get("id", slug)
        background_tasks.add_task(_log_download, meme_id)

    return RedirectResponse(url=url, status_code=301)


def _log_download(meme_id: str) -> None:
    """Background task to record download signal."""
    try:
        from app.core.cache import cache_service
        key = f"downloads:{meme_id}"
        count = cache_service.get(key) or 0
        cache_service.set(key, count + 1, ttl=86400)
    except Exception:
        pass
