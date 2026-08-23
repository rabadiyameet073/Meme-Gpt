"""FAQ API Router for MemeGPT.
Specification: 15_FAQs/General_FAQ.md

Endpoints:
- GET /api/v1/faqs
- GET /api/v1/faqs/search
- GET /api/v1/faqs/categories
- GET /api/v1/faqs/models
- GET /api/v1/faqs/degradation
- GET /api/v1/faqs/{faq_id}
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from app.services.faq_service import (
    get_all_faqs,
    get_faq_by_id,
    search_faqs,
    get_faq_categories_summary,
    get_ai_models_catalog,
    get_graceful_degradation_matrix,
)

router = APIRouter(prefix="/faqs", tags=["Frequently Asked Questions"])


@router.get("", summary="Get all FAQs or filter by category")
def list_faqs(category: Optional[str] = Query(None, description="Filter category: 'general', 'technical', or 'api'")):
    """Retrieve full catalog of 21 FAQs with optional category filtering."""
    return {
        "success": True,
        **get_all_faqs(category=category),
    }


@router.get("/search", summary="Search FAQs by keyword or natural language query")
def search_faq_list(q: str = Query(..., min_length=1, description="Search query string")):
    """Full-text search across questions, answers, and tags in the FAQ knowledge base."""
    return {
        "success": True,
        **search_faqs(query=q),
    }


@router.get("/categories", summary="Get FAQ categories breakdown and statistics")
def get_categories():
    """Retrieve category counts and distribution (general, technical, api)."""
    return {
        "success": True,
        **get_faq_categories_summary(),
    }


@router.get("/models", summary="Get AI models inventory table")
def get_models():
    """Retrieve specifications for all 6 AI models used in MemeGPT."""
    return {
        "success": True,
        **get_ai_models_catalog(),
    }


@router.get("/degradation", summary="Get graceful degradation failure matrix")
def get_degradation():
    """Retrieve external service failure scenarios and system fallback paths."""
    return {
        "success": True,
        **get_graceful_degradation_matrix(),
    }


# ── Manifest & Health Endpoints (15_FAQs/README.md) ──────────────────────────

from app.services.faq_manifest_service import (
    get_faq_section_manifest,
    get_faq_posture_summary,
    get_faq_subsystem_health,
)


@router.get("/manifest", summary="Get Section 15F documentation manifest")
def get_manifest():
    """Retrieve complete catalog and navigation metadata for Section 15F (FAQs)."""
    return {
        "success": True,
        **get_faq_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated FAQ knowledge base posture")
def get_posture():
    """Retrieve knowledge base readiness, indexed entries count, and technical parameters."""
    return {
        "success": True,
        **get_faq_posture_summary(),
    }


@router.get("/health", summary="Get FAQ subsystem diagnostic health")
def get_health():
    """Evaluate health and readiness of FAQ knowledge base and search engine."""
    return {
        "success": True,
        **get_faq_subsystem_health(),
    }


@router.get("/{faq_id}", summary="Get a single FAQ by ID")
def get_single_faq(faq_id: str = Path(..., description="FAQ identifier (e.g. FAQ_GEN_1, FAQ_TECH_3, FAQ_API_1)")):
    """Retrieve a single FAQ question, answer, and metadata."""
    item = get_faq_by_id(faq_id=faq_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"FAQ with ID '{faq_id}' not found.")
    return {
        "success": True,
        "faq": item,
    }
