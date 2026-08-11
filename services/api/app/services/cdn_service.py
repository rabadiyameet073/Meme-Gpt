"""
CDN Service — resolves meme file URLs.
Production: Cloudflare R2 (cdn.memegpt.com)
Development: local /public folder (localhost:8000/static)
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger("services.cdn")

LOCAL_MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "public" / "memes"


class CDNService:
    def __init__(self):
        from app.core.config import settings
        self.base_url = settings.CDN_BASE_URL.rstrip("/")

    def get_image_url(self, slug: str) -> str:
        return f"{self.base_url}/images/{slug}.jpg"

    def get_gif_url(self, slug: str) -> str:
        return f"{self.base_url}/gifs/{slug}.gif"

    def get_mp4_url(self, slug: str) -> str:
        return f"{self.base_url}/videos/{slug}.mp4"

    def get_thumb_url(self, slug: str) -> str:
        return f"{self.base_url}/thumbs/{slug}.webp"

    def get_share_url(self, slug: str, query_id: str = "") -> str:
        base = "https://memegpt.com" if "cdn.memegpt.com" in self.base_url else "http://localhost:3000"
        ref = f"?ref={query_id}" if query_id else ""
        return f"{base}/meme/{slug}{ref}"

    def resolve_formats(self, meme: dict) -> dict:
        """Build formats dict from meme payload (CDN or raw URLs)."""
        slug = meme.get("slug", meme.get("id", "unknown"))
        return {
            "gif": meme.get("gif_url") or (self.get_gif_url(slug) if meme.get("has_gif") else None),
            "image": meme.get("image_url") or self.get_image_url(slug),
            "video": meme.get("mp4_url") or (self.get_mp4_url(slug) if meme.get("has_video") else None),
            "webp": meme.get("thumb_url") or self.get_thumb_url(slug),
        }


cdn_service = CDNService()
