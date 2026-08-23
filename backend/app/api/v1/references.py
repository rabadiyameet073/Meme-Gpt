"""References & External Resources API Router for MemeGPT.
Specification: 16_References/External_Resources.md

Endpoints:
- GET /api/v1/references/resources/documentation
- GET /api/v1/references/resources/papers
- GET /api/v1/references/resources/meme-sources
- GET /api/v1/references/resources/community
- GET /api/v1/references/resources/search
- GET /api/v1/references/resources/summary
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.external_resources_service import (
    get_official_documentation,
    get_research_papers,
    get_meme_data_sources,
    get_community_resources,
    search_external_resources,
    get_external_resources_summary,
)

router = APIRouter(prefix="/references", tags=["References & External Resources"])


@router.get("/resources/documentation", summary="Get official documentation links")
def list_documentation(category: Optional[str] = Query(None, description="Filter: 'frameworks_libraries', 'ai_ml', 'infrastructure', 'development_tools'")):
    """Retrieve official documentation URLs for frameworks, AI models, cloud infrastructure, and dev tools."""
    return {
        "success": True,
        **get_official_documentation(category=category),
    }


@router.get("/resources/papers", summary="Get foundational research papers")
def list_papers():
    """Retrieve 6 AI/ML research papers (Sentence-BERT, CLIP, BLIP, MTEB, Word2Vec, Attention)."""
    return {
        "success": True,
        **get_research_papers(),
    }


@router.get("/resources/meme-sources", summary="Get external meme data sources")
def list_meme_sources():
    """Retrieve meme template providers and trending feed APIs (Imgflip, Reddit, Tenor, Know Your Meme)."""
    return {
        "success": True,
        **get_meme_data_sources(),
    }


@router.get("/resources/community", summary="Get community & learning resources")
def list_community():
    """Retrieve developer communities across Discord, Reddit, and HuggingFace forums."""
    return {
        "success": True,
        **get_community_resources(),
    }


@router.get("/resources/search", summary="Search across all external resources & citations")
def search_resources(q: str = Query(..., min_length=1, description="Search query keyword or library name")):
    """Full-text search across documentation links, research papers, meme data sources, and community channels."""
    return {
        "success": True,
        **search_external_resources(query=q),
    }


@router.get("/resources/summary", summary="Get external resources inventory summary")
def get_summary():
    """Retrieve summary counts across official documentation, research papers, meme sources, and community channels."""
    return {
        "success": True,
        **get_external_resources_summary(),
    }


# ── Manifest & Health Endpoints (16_References/README.md) ────────────────────

from app.services.references_manifest_service import (
    get_references_section_manifest,
    get_references_posture_summary,
    get_references_subsystem_health,
)


@router.get("/manifest", summary="Get Section 16R documentation manifest")
def get_manifest():
    """Retrieve complete catalog and navigation metadata for Section 16R (References)."""
    return {
        "success": True,
        **get_references_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated references posture")
def get_posture():
    """Retrieve external resources readiness, citation coverage, and documentation counts."""
    return {
        "success": True,
        **get_references_posture_summary(),
    }


@router.get("/health", summary="Get references subsystem diagnostic health")
def get_health():
    """Evaluate health and completeness of external citations and research paper references."""
    return {
        "success": True,
        **get_references_subsystem_health(),
    }


# ── Technology Stack Endpoints (16_References/Technology_Stack.md) ──────────

from app.services.tech_stack_service import (
    get_all_tech_stack_components,
    get_tech_stack_by_id,
    search_tech_stack,
    get_tech_stack_tiers_summary,
    evaluate_tech_stack_compliance,
)


@router.get("/tech-stack", summary="Get all technology stack components")
def list_tech_stack(tier: Optional[str] = Query(None, description="Filter tier: 'backend', 'frontend', 'ai_ml', 'infrastructure', 'dev_tools'")):
    """Retrieve full catalog of 20+ technologies with rationale, benefits, and best practices."""
    return {
        "success": True,
        **get_all_tech_stack_components(tier=tier),
    }


@router.get("/tech-stack/tiers", summary="Get technology stack tier breakdown")
def get_tech_tiers():
    """Retrieve distribution of technologies across the 5 core architecture tiers."""
    return {
        "success": True,
        **get_tech_stack_tiers_summary(),
    }


@router.get("/tech-stack/search", summary="Search technology stack")
def search_technologies(q: str = Query(..., min_length=1, description="Search query string")):
    """Full-text search across technology names, purposes, rationales, and alternatives."""
    return {
        "success": True,
        **search_tech_stack(query=q),
    }


@router.get("/tech-stack/compliance", summary="Evaluate Phase 6 technology stack compliance")
def get_tech_compliance():
    """Verify that all technologies have complete 8-attribute specifications as required by Phase 6."""
    return {
        "success": True,
        **evaluate_tech_stack_compliance(),
    }


@router.get("/tech-stack/{tech_id}", summary="Get single technology component by ID")
def get_tech_item(tech_id: str):
    """Retrieve full 8-attribute specification for a single technology component."""
    item = get_tech_stack_by_id(tech_id=tech_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Technology with ID '{tech_id}' not found.")
    return {
        "success": True,
        "technology": item,
    }
