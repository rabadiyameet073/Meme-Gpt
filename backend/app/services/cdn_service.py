"""MemeGPT — CDN URL Resolver Service.

Resolves meme IDs to format-specific CDN URLs.
In development: serves from local /static directory.
In production: resolves to Cloudflare R2 CDN URLs.

Specification: 04_DESIGN_AND_DEVELOPMENT.md
"""

import logging
from app.config import CDN_BASE_URL, APP_BASE_URL

logger = logging.getLogger("memegpt.cdn")


def resolve_formats(meme: dict) -> dict:
    """Resolve all available format URLs for a meme.

    Returns a dict with keys: image, gif, mp4, webp, thumb
    """
    meme_id = meme.get("id", "")
    name_slug = meme.get("slug") or meme.get("name", "meme").lower().replace(" ", "-")

    # Use existing refs if available
    image_url = (
        meme.get("imageRef")
        or meme.get("image_ref")
        or f"{CDN_BASE_URL}/images/{meme_id}.png"
    )
    gif_url = (
        meme.get("gifRef")
        or meme.get("gif_ref")
        or ""
    )
    mp4_url = (
        meme.get("videoRef")
        or meme.get("video_ref")
        or ""
    )

    return {
        "image": image_url,
        "gif": gif_url or None,
        "mp4": mp4_url or None,
        "webp": image_url.replace(".png", ".webp") if image_url.endswith(".png") else image_url,
        "thumb": image_url,
    }


def build_meme_urls(meme_id: str, slug: str) -> dict:
    """Build CDN URLs for all available formats matching Services.md spec."""
    return {
        "image": f"{CDN_BASE_URL}/images/{slug}.jpg",
        "gif": f"{CDN_BASE_URL}/gifs/{slug}.gif",
        "video": f"{CDN_BASE_URL}/videos/{slug}.mp4",
        "webp": f"{CDN_BASE_URL}/webp/{slug}.webp",
        "thumb": f"{CDN_BASE_URL}/thumbs/{slug}.webp",
    }


def get_share_url(slug: str, query_id: str = "") -> str:
    """Generate a shareable URL for a meme."""
    base = f"{APP_BASE_URL}/meme/{slug}"
    if query_id:
        return f"{base}?ref={query_id}"
    return base

