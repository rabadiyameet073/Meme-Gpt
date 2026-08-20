"""Share Feature Service for MemeGPT.
Specification: 08_Features/Share_Feature.md
"""

import logging
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("memegpt.services.share")

BASE_SHARE_DOMAIN = "https://memegpt.com"

SHARE_ANALYTICS_WEIGHTS = {
    "share": 3.0,          # Native share completed
    "copy_link": 1.0,      # Link copied to clipboard
    "copy_image": 1.0,     # Image copied to clipboard
    "copy": 1.0,           # General copy signal
    "share_cancelled": 0.0 # User cancelled / AbortError
}


def generate_share_url(slug_or_id: str, query_id: Optional[str] = None) -> str:
    """Generate SEO-friendly attributed share URL: https://memegpt.com/meme/{slug}?ref={query_id}"""
    clean_slug = (slug_or_id or "meme").strip().lower().replace(" ", "-")
    url = f"{BASE_SHARE_DOMAIN}/meme/{clean_slug}"
    if query_id and query_id.strip():
        url += f"?ref={query_id.strip()}"
    return url


def parse_share_url(share_url: str) -> Dict[str, Optional[str]]:
    """Extract slug and ref (query_id) from share URL."""
    try:
        parsed = urlparse(share_url)
        path_parts = [p for p in parsed.path.split("/") if p]
        slug = path_parts[1] if len(path_parts) >= 2 and path_parts[0] == "meme" else (path_parts[0] if path_parts else None)
        query_params = parse_qs(parsed.query)
        ref = query_params.get("ref", [None])[0]
        return {
            "slug": slug,
            "ref_query_id": ref,
        }
    except Exception as e:
        logger.warning(f"Failed to parse share URL '{share_url}': {e}")
        return {"slug": None, "ref_query_id": None}


def get_share_analytics_weights() -> Dict[str, float]:
    """Return signal weights for share and copy actions."""
    return SHARE_ANALYTICS_WEIGHTS.copy()


def generate_opengraph_metadata(meme: Any, query_id: Optional[str] = None) -> Dict[str, str]:
    """Generate OpenGraph and Twitter card metadata for meme sharing."""
    if hasattr(meme, "to_dict"):
        m_dict = meme.to_dict()
    elif isinstance(meme, dict):
        m_dict = meme
    else:
        m_dict = {}

    slug = m_dict.get("slug") or m_dict.get("id") or "meme"
    name = m_dict.get("name") or "Meme"
    explanation = m_dict.get("explanation") or m_dict.get("dialogue") or f"Check out this meme: {name}"
    
    formats = m_dict.get("formats", {})
    image_url = formats.get("image") or m_dict.get("image_ref") or m_dict.get("preview_url") or f"https://cdn.memegpt.com/images/{slug}.png"
    share_url = generate_share_url(slug, query_id)

    return {
        "og:title": f"{name} — MemeGPT",
        "og:description": explanation,
        "og:image": image_url,
        "og:url": share_url,
        "og:type": "video.other" if formats.get("video") else "image",
        "og:site_name": "MemeGPT",
        "twitter:card": "summary_large_image",
        "twitter:title": f"{name} — MemeGPT",
        "twitter:description": explanation,
        "twitter:image": image_url,
    }
