"""
MemeGPT — CDN Service (Cloudflare R2) — FIXED.

Handles URL building, file upload, and thumbnail generation.
All meme media stored in Cloudflare R2 with structure:
  memegpt-memes/
  ├── images/   {slug}.jpg
  ├── gifs/     {slug}.gif
  ├── videos/   {slug}.mp4
  ├── webp/     {slug}.webp
  └── thumbs/   {slug}.webp  (200×200)
"""

import logging
import os
from io import BytesIO
from typing import Optional, Any, Dict, List

from app.config import settings

logger = logging.getLogger("memegpt.cdn")

CDN_BASE = getattr(settings, "CDN_BASE_URL", "https://cdn.memegpt.com")
R2_BUCKET = getattr(settings, "R2_BUCKET", "memegpt-memes")


def build_meme_urls(slug_or_meme: Any = None, meme_id: Optional[str] = None, slug: Optional[str] = None) -> dict:
    """Build all CDN URLs for a meme by its slug, meme_id, or dict."""
    base = CDN_BASE.rstrip("/")
    if isinstance(slug_or_meme, dict):
        s = slug_or_meme.get("slug") or slug_or_meme.get("id") or slug or meme_id or "meme"
        orig = slug_or_meme.get("image_url") or slug_or_meme.get("imageRef") or f"{base}/images/{s}.jpg"
        webp = slug_or_meme.get("webp_url") or f"{base}/webp/{s}.webp"
        gif = slug_or_meme.get("gif_url") or slug_or_meme.get("gifRef") or f"{base}/gifs/{s}.gif"
        mp4 = slug_or_meme.get("mp4_url") or slug_or_meme.get("videoRef") or f"{base}/videos/{s}.mp4"
        thumb = slug_or_meme.get("thumb_url") or slug_or_meme.get("thumbUrl") or f"{base}/thumbs/{s}.webp"
    else:
        s = str(slug or slug_or_meme or meme_id or "meme")
        orig = f"{base}/images/{s}.jpg"
        webp = f"{base}/webp/{s}.webp"
        gif = f"{base}/gifs/{s}.gif"
        mp4 = f"{base}/videos/{s}.mp4"
        thumb = f"{base}/thumbs/{s}.webp"

    return {
        "image": orig,
        "image_url": orig,
        "original": orig,
        "webp": webp,
        "webp_url": webp,
        "gif": gif,
        "gif_url": gif,
        "video": mp4,
        "mp4": mp4,
        "mp4_url": mp4,
        "thumb": thumb,
        "thumb_url": thumb,
    }


def get_share_url(slug: str, query_id: Optional[str] = None) -> str:
    """Return shareable web URL for a meme with optional query referral."""
    app_base = getattr(settings, "APP_BASE_URL", "https://app.memegpt.com")
    url = f"{app_base.rstrip('/')}/meme/{slug}"
    if query_id:
        url += f"?ref={query_id}"
    return url



def get_r2_client():
    """Returns boto3 S3 client configured for Cloudflare R2."""
    endpoint = getattr(settings, "R2_ENDPOINT", "")
    access_key = getattr(settings, "R2_ACCESS_KEY", "")
    secret_key = getattr(settings, "R2_SECRET_KEY", "")

    if not all([endpoint, access_key, secret_key]):
        logger.debug("R2 credentials not configured — media upload disabled")
        return None

    try:
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
        )
        return client
    except ImportError:
        logger.error("boto3 not installed. Run: pip install boto3")
        return None
    except Exception as e:
        logger.error(f"Failed to create R2 client: {e}")
        return None


def upload_file(
    file_data: bytes,
    key: str,
    content_type: str = "image/jpeg",
    public: bool = True,
) -> Optional[str]:
    """
    Upload file bytes to R2.
    Returns CDN URL on success, None on failure.
    """
    client = get_r2_client()
    if not client:
        return None

    extra_args = {"ContentType": content_type}

    try:
        client.put_object(
            Bucket=R2_BUCKET,
            Key=key,
            Body=file_data,
            **extra_args,
        )
        cdn_url = f"{CDN_BASE.rstrip('/')}/{key}"
        logger.debug(f"Uploaded {key} → {cdn_url}")
        return cdn_url

    except Exception as e:
        logger.error(f"R2 upload failed for {key}: {e}")
        return None


def upload_meme_image(slug: str, image_data: bytes, fmt: str = "jpg") -> Optional[str]:
    """Upload meme original image. Returns CDN URL."""
    content_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "mp4": "video/mp4",
        "webp": "image/webp",
    }
    folder_map = {
        "jpg": "images",
        "jpeg": "images",
        "png": "images",
        "gif": "gifs",
        "mp4": "videos",
        "webp": "webp",
    }
    folder = folder_map.get(fmt.lower(), "images")
    key = f"{folder}/{slug}.{fmt.lower()}"
    ct = content_types.get(fmt.lower(), "image/jpeg")
    return upload_file(image_data, key, ct)


def generate_thumbnail(image_data: bytes, size: tuple = (200, 200)) -> Optional[bytes]:
    """
    Generate a 200×200 WebP thumbnail from image bytes.
    Returns thumbnail bytes or None on failure.
    """
    try:
        from PIL import Image

        img = Image.open(BytesIO(image_data)).convert("RGB")
        img.thumbnail(size, Image.LANCZOS)

        # Center-crop to exact size
        if img.size != size:
            left = max((img.width - size[0]) // 2, 0)
            top = max((img.height - size[1]) // 2, 0)
            img = img.crop((left, top, left + size[0], top + size[1]))

        output = BytesIO()
        img.save(output, format="WEBP", quality=85)
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Thumbnail generation failed: {e}")
        return None


def upload_thumbnail(slug: str, image_data: bytes) -> Optional[str]:
    """Generate 200×200 thumbnail and upload to R2/thumbs/. Returns CDN URL."""
    thumb_data = generate_thumbnail(image_data)
    if not thumb_data:
        return None
    key = f"thumbs/{slug}.webp"
    return upload_file(thumb_data, key, "image/webp")


def resolve_formats(meme: dict) -> dict:
    """
    Build format URLs for a meme dict.
    Tries CDN URLs, falls back to imageRef/gifRef/videoRef.
    """
    slug = meme.get("slug", "")
    cdn_urls = build_meme_urls(slug) if slug else {}

    image = meme.get("image_url") or meme.get("imageRef") or meme.get("image_ref") or cdn_urls.get("image_url")
    gif = meme.get("gif_url") or meme.get("gifRef") or meme.get("gif_ref") or cdn_urls.get("gif_url")
    mp4 = meme.get("mp4_url") or meme.get("videoRef") or meme.get("video_ref") or cdn_urls.get("mp4_url")
    thumb = meme.get("thumb_url") or meme.get("thumbUrl") or cdn_urls.get("thumb_url") or image
    webp = meme.get("webp_url") or cdn_urls.get("webp_url") or image

    return {
        "image": image,
        "gif": gif,
        "mp4": mp4,
        "webp": webp,
        "thumb": thumb,
    }
