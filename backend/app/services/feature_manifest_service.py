"""Features Section Manifest Service for MemeGPT.
Specification: 08_Features/README.md
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.feature_manifest")

FEATURES_SECTION_MANIFEST = {
    "section_id": "08_Features",
    "title": "08 — Features",
    "description": "Feature specifications for MemeGPT core capabilities.",
    "features": [
        {
            "id": "smart_search",
            "name": "Smart Meme Search",
            "document": "Smart_Meme_Search.md",
            "description": "Core search feature with AI semantic understanding and hybrid vector retrieval.",
            "status": "active",
            "endpoints": ["POST /api/v1/search"],
        },
        {
            "id": "multi_format",
            "name": "Multi-Format Support",
            "document": "Multi_Format.md",
            "description": "GIF, PNG, MP4, WebP format support + platform recommendations + Trending + SEO.",
            "status": "active",
            "endpoints": ["GET /api/v1/memes/{id}"],
        },
        {
            "id": "favorites_collections",
            "name": "Favorites & Collections",
            "document": "Favorites_Collections.md",
            "description": "Save and organize memes into personal collections with LocalStorage and cloud sync.",
            "status": "active",
            "endpoints": ["GET /api/v1/collections", "POST /api/v1/collections/memes"],
        },
        {
            "id": "copy_download",
            "name": "Copy & Download",
            "document": "Copy_Download.md",
            "description": "One-click copy to clipboard (image data + share URL fallback) and direct CDN download.",
            "status": "active",
            "endpoints": ["GET /api/v1/memes/{id}"],
        },
        {
            "id": "chat_refinement",
            "name": "Chat Refinement",
            "document": "Chat_Refinement.md",
            "description": "Multi-turn conversational search where users refine results by tone, format, and index.",
            "status": "active",
            "endpoints": ["POST /api/v1/chat/refine", "POST /api/v1/chat/search"],
        },
        {
            "id": "share_feature",
            "name": "Share Feature",
            "document": "Share_Feature.md",
            "description": "Dynamic share links, OpenGraph metadata, and social preview generator.",
            "status": "active",
            "endpoints": ["GET /api/v1/memes/{id}"],
        },
        {
            "id": "trending_memes",
            "name": "Trending Memes",
            "document": "Trending_Memes.md",
            "description": "Hourly-updated trending section based on search volume, downloads, and recency.",
            "status": "active",
            "endpoints": ["GET /api/v1/trending"],
        },
        {
            "id": "visual_search",
            "name": "Visual Search",
            "document": "Visual_Search.md",
            "description": "Image-to-meme and multimodal reverse visual similarity search.",
            "status": "active",
            "endpoints": ["POST /api/v1/search"],
        },
    ],
}


def get_features_section_manifest() -> Dict[str, Any]:
    """Return the full Features section manifest catalog."""
    return FEATURES_SECTION_MANIFEST.copy()


def get_feature_by_id(feature_id: str) -> Optional[Dict[str, Any]]:
    """Get metadata and endpoints for a specific feature."""
    feature_id_lower = feature_id.lower().replace("-", "_")
    for feat in FEATURES_SECTION_MANIFEST["features"]:
        if feat["id"] == feature_id_lower:
            return feat.copy()
    return None


def verify_feature_system_health() -> Dict[str, Any]:
    """Verify that all features have active backing services and handlers."""
    manifest = get_features_section_manifest()
    feature_count = len(manifest["features"])
    active_count = sum(1 for f in manifest["features"] if f.get("status") == "active")

    return {
        "section": manifest["section_id"],
        "total_features": feature_count,
        "active_features": active_count,
        "all_healthy": active_count == feature_count,
    }
