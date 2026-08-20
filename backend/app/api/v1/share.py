"""Share Feature API Router for MemeGPT.
Specification: 08_Features/Share_Feature.md
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.share_service import (
    generate_share_url,
    parse_share_url,
    get_share_analytics_weights,
    generate_opengraph_metadata,
)
from app.services.meme_service import get_meme_by_id

logger = logging.getLogger("memegpt.api.share")
router = APIRouter(prefix="/share", tags=["Share Feature"])


@router.get("/url/{slug}", summary="Generate attributed share URL")
def get_meme_share_url(
    slug: str,
    ref: Optional[str] = Query(None, description="Search query ID that led to the share"),
):
    """Generate SEO-friendly attributed share URL with query_id tracking."""
    url = generate_share_url(slug_or_id=slug, query_id=ref)
    return {
        "success": True,
        "slug": slug,
        "ref": ref,
        "share_url": url,
    }


@router.get("/parse", summary="Parse share URL")
def parse_url(
    url: str = Query(..., description="Share URL to parse"),
):
    """Parse slug and ref tracking ID from share URL."""
    res = parse_share_url(url)
    return {
        "success": True,
        **res,
    }


@router.get("/og/{meme_id_or_slug}", summary="Get OpenGraph social card metadata")
def get_og_metadata(
    meme_id_or_slug: str,
    ref: Optional[str] = Query(None, description="Search query ID reference"),
):
    """Return OpenGraph and Twitter card metadata for rich link previews."""
    meme = get_meme_by_id(meme_id_or_slug)
    if not meme:
        # Fallback to generated card
        meme = {
            "id": meme_id_or_slug,
            "slug": meme_id_or_slug,
            "name": meme_id_or_slug.replace("-", " ").title(),
            "explanation": f"Check out the {meme_id_or_slug} meme on MemeGPT",
        }

    og_data = generate_opengraph_metadata(meme, query_id=ref)
    return {
        "success": True,
        "og_metadata": og_data,
    }


@router.get("/analytics-weights", summary="Get share analytics signal weights")
def get_analytics_weights():
    """Return signal weight scoring for share actions (+3.0 share, +1.0 copy, 0.0 cancelled)."""
    return {
        "success": True,
        "weights": get_share_analytics_weights(),
    }
