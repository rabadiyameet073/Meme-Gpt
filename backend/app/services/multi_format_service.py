"""Multi-Format Support Service for MemeGPT.
Specification: 08_Features/Multi_Format.md
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.multi_format")

FORMAT_SUPPORT_CATALOG = {
    "gif": {
        "format": "GIF",
        "extension": ".gif",
        "mime_type": "image/gif",
        "use_case": "WhatsApp, Discord, Slack",
        "avg_size": "1–5MB",
        "platform_recommendation": "Best for WhatsApp, Discord, Slack",
    },
    "image": {
        "format": "PNG/JPG",
        "extension": ".png",
        "mime_type": "image/png",
        "use_case": "Instagram, email, blog",
        "avg_size": "50–500KB",
        "platform_recommendation": "Best for Instagram, email, blog",
    },
    "video": {
        "format": "MP4",
        "extension": ".mp4",
        "mime_type": "video/mp4",
        "use_case": "TikTok, Reels, YouTube Shorts",
        "avg_size": "2–10MB",
        "platform_recommendation": "Best for TikTok, Reels, YouTube Shorts",
    },
    "webp": {
        "format": "WebP",
        "extension": ".webp",
        "mime_type": "image/webp",
        "use_case": "Telegram stickers, web",
        "avg_size": "30–200KB",
        "platform_recommendation": "Best for Telegram stickers, web",
    },
    "thumb": {
        "format": "Thumbnail",
        "extension": ".webp",
        "mime_type": "image/webp",
        "use_case": "Search results preview",
        "avg_size": "10–50KB",
        "platform_recommendation": "Search results preview",
    },
}


def get_format_catalog() -> Dict[str, Dict[str, Any]]:
    """Return full multi-format support matrix."""
    return FORMAT_SUPPORT_CATALOG.copy()


def get_format_platform_recommendation(format_type: str) -> str:
    """Return platform recommendation tip for format (e.g. 'Best for WhatsApp, Discord, Slack')."""
    fmt_key = format_type.lower().strip()
    if fmt_key in ["png", "jpg", "jpeg"]:
        fmt_key = "image"
    elif fmt_key in ["mp4"]:
        fmt_key = "video"
    
    info = FORMAT_SUPPORT_CATALOG.get(fmt_key)
    if info:
        return info["platform_recommendation"]
    return "Standard media format"


def resolve_all_meme_format_assets(meme: Any) -> Dict[str, Any]:
    """Resolve URLs, extensions, and recommendations for all supported formats of a meme."""
    if hasattr(meme, "to_dict"):
        m_dict = meme.to_dict()
    elif isinstance(meme, dict):
        m_dict = meme
    else:
        m_dict = {}

    slug = m_dict.get("slug") or m_dict.get("id") or "meme"
    formats_in = m_dict.get("formats", {})

    image_url = formats_in.get("image") or m_dict.get("image_ref") or m_dict.get("imageRef") or f"https://cdn.memegpt.com/images/{slug}.png"
    gif_url = formats_in.get("gif") or m_dict.get("gif_ref") or m_dict.get("gifRef") or f"https://cdn.memegpt.com/memes/{slug}.gif"
    video_url = formats_in.get("video") or m_dict.get("video_ref") or m_dict.get("videoRef") or f"https://cdn.memegpt.com/videos/{slug}.mp4"
    webp_url = formats_in.get("webp") or f"https://cdn.memegpt.com/webp/{slug}.webp"
    thumb_url = formats_in.get("thumb") or f"https://cdn.memegpt.com/thumbs/{slug}.webp"

    return {
        "slug": slug,
        "formats": {
            "image": {
                "url": image_url,
                "extension": ".png",
                "recommendation": FORMAT_SUPPORT_CATALOG["image"]["platform_recommendation"],
                "avg_size": FORMAT_SUPPORT_CATALOG["image"]["avg_size"],
            },
            "gif": {
                "url": gif_url,
                "extension": ".gif",
                "recommendation": FORMAT_SUPPORT_CATALOG["gif"]["platform_recommendation"],
                "avg_size": FORMAT_SUPPORT_CATALOG["gif"]["avg_size"],
            },
            "video": {
                "url": video_url,
                "extension": ".mp4",
                "recommendation": FORMAT_SUPPORT_CATALOG["video"]["platform_recommendation"],
                "avg_size": FORMAT_SUPPORT_CATALOG["video"]["avg_size"],
            },
            "webp": {
                "url": webp_url,
                "extension": ".webp",
                "recommendation": FORMAT_SUPPORT_CATALOG["webp"]["platform_recommendation"],
                "avg_size": FORMAT_SUPPORT_CATALOG["webp"]["avg_size"],
            },
            "thumb": {
                "url": thumb_url,
                "extension": ".webp",
                "recommendation": FORMAT_SUPPORT_CATALOG["thumb"]["platform_recommendation"],
                "avg_size": FORMAT_SUPPORT_CATALOG["thumb"]["avg_size"],
            },
        }
    }
