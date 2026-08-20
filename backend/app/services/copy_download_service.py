"""Copy & Download Feature Service for MemeGPT.
Specification: 08_Features/Copy_Download.md
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.copy_download")

PLATFORM_SUPPORT_MATRIX = {
    "Chrome 76+": {"image_copy": True, "url_fallback": True},
    "Edge 79+": {"image_copy": True, "url_fallback": True},
    "Safari 14.1+": {"image_copy": True, "url_fallback": True},
    "Firefox": {"image_copy": False, "url_fallback": True},
    "Mobile Safari (iOS 16+)": {"image_copy": True, "url_fallback": True},
    "Mobile Chrome": {"image_copy": True, "url_fallback": True},
}

ANALYTICS_WEIGHTS = {
    "copy_image": {"action": "copy", "weight": 1.0, "description": "Raw image data copied to clipboard"},
    "copy_url": {"action": "copy", "weight": 0.5, "description": "Share URL copied as fallback"},
    "download": {"action": "download", "weight": 2.0, "description": "File downloaded in specific format"},
    "format_change": {"action": "format_change", "weight": 0.1, "description": "User switched format preview"},
}


def get_platform_support_matrix() -> Dict[str, Dict[str, bool]]:
    """Return browser/platform clipboard copy capability matrix."""
    return PLATFORM_SUPPORT_MATRIX.copy()


def get_copy_download_analytics_weights() -> Dict[str, Dict[str, Any]]:
    """Return interaction signal weights matching Copy_Download.md specification."""
    return ANALYTICS_WEIGHTS.copy()


def generate_download_asset_descriptor(
    meme: Any,
    format_type: str = "image"
) -> Dict[str, Any]:
    """Resolve filename and CDN target URL for asset download."""
    if hasattr(meme, "to_dict"):
        m_dict = meme.to_dict()
    elif isinstance(meme, dict):
        m_dict = meme
    else:
        m_dict = {}

    slug = m_dict.get("slug") or m_dict.get("id") or "meme"
    format_lower = format_type.lower()
    if format_lower == "image":
        ext = "png"
    elif format_lower == "video":
        ext = "mp4"
    else:
        ext = format_lower

    filename = f"{slug}.{ext}"

    # Extract target url
    formats = m_dict.get("formats", {})
    if isinstance(formats, dict) and formats.get(format_lower):
        target_url = formats[format_lower]
    else:
        if format_lower == "gif":
            target_url = m_dict.get("gif_ref") or m_dict.get("gifRef") or f"https://cdn.memegpt.com/memes/{slug}.gif"
        elif format_lower == "video":
            target_url = m_dict.get("video_ref") or m_dict.get("videoRef") or f"https://cdn.memegpt.com/videos/{slug}.mp4"
        elif format_lower == "webp":
            target_url = f"https://cdn.memegpt.com/webp/{slug}.webp"
        else:
            target_url = m_dict.get("image_ref") or m_dict.get("imageRef") or f"https://cdn.memegpt.com/images/{slug}.png"

    return {
        "slug": slug,
        "format": format_lower,
        "extension": ext,
        "filename": filename,
        "url": target_url,
        "content_type": f"image/{ext}" if ext in ["png", "gif", "webp", "jpg"] else f"video/{ext}",
    }
