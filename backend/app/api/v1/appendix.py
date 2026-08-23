"""Appendix API Router for MemeGPT.
Specification: 17_Appendix/Changelog.md

Endpoints:
- GET  /api/v1/appendix/changelog
- GET  /api/v1/appendix/changelog/latest
- GET  /api/v1/appendix/changelog/summary
- GET  /api/v1/appendix/changelog/search
- GET  /api/v1/appendix/changelog/{version}
- POST /api/v1/appendix/changelog/upgrade-path
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.changelog_service import (
    get_all_releases,
    get_release_by_version,
    get_latest_release,
    search_changelog,
    get_changelog_summary,
    evaluate_version_upgrade,
)

router = APIRouter(prefix="/appendix", tags=["Appendix & Changelog"])


class UpgradePathRequest(BaseModel):
    current_version: str = Field(default="v1.0.0", description="Current deployed version (e.g. 'v1.0.0')")
    target_version: str = Field(default="v2.0.0", description="Target upgrade version (e.g. 'v2.0.0')")


@router.get("/changelog", summary="Get all releases in changelog")
def list_releases(status: Optional[str] = Query(None, description="Filter by 'RELEASED' or 'PLANNED'")):
    """Retrieve full version history across initial release (v1.0.0) and planned roadmap releases (v1.1.0, v1.2.0, v2.0.0)."""
    return {
        "success": True,
        **get_all_releases(status=status),
    }


@router.get("/changelog/latest", summary="Get latest released version")
def get_latest():
    """Retrieve most recent production release metadata."""
    return {
        "success": True,
        **get_latest_release(),
    }


@router.get("/changelog/summary", summary="Get changelog inventory summary")
def get_summary():
    """Retrieve summary counts across releases, initial features, and planned future milestones."""
    return {
        "success": True,
        **get_changelog_summary(),
    }


@router.get("/changelog/search", summary="Search changelog entries")
def search_entries(q: str = Query(..., min_length=1, description="Search keyword")):
    """Full-text search across all changelog features, architecture items, and planned enhancements."""
    return {
        "success": True,
        **search_changelog(query=q),
    }


@router.get("/changelog/{version}", summary="Get release details by version")
def get_release(version: str):
    """Retrieve detailed changelog sections for a specific version tag (e.g. 'v1.0.0')."""
    release = get_release_by_version(version=version)
    if not release:
        raise HTTPException(status_code=404, detail=f"Version '{version}' not found in changelog.")
    return {
        "success": True,
        "release": release,
    }


@router.post("/changelog/upgrade-path", summary="Evaluate SemVer upgrade path")
def check_upgrade(body: UpgradePathRequest):
    """Evaluate SemVer upgrade delta between two versions, highlighting breaking changes and intermediate milestones."""
    result = evaluate_version_upgrade(current_version=body.current_version, target_version=body.target_version)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "success": True,
        **result,
    }


# ── Glossary Endpoints (17_Appendix/Glossary.md) ───────────────────────────

from app.services.glossary_service import (
    get_all_glossary_terms,
    get_glossary_term_by_name,
    search_glossary,
    get_glossary_summary,
)


@router.get("/glossary", summary="Get all glossary technical terms")
def list_terms(
    category: Optional[str] = Query(None, description="Filter by domain category ('ai_ml', 'backend_storage', 'architecture', 'security', 'marketing')"),
    letter: Optional[str] = Query(None, description="Filter by initial letter (e.g. 'A', 'C', 'M')"),
):
    """Retrieve full alphabetical glossary of technical terms, abbreviations, and system concepts."""
    return {
        "success": True,
        **get_all_glossary_terms(category=category, letter=letter),
    }


@router.get("/glossary/summary", summary="Get glossary summary & category distribution")
def get_glossary_stats():
    """Retrieve total term counts, domain distribution, and letter groupings."""
    return {
        "success": True,
        **get_glossary_summary(),
    }


@router.get("/glossary/search", summary="Search glossary definitions")
def search_terms(q: str = Query(..., min_length=1, description="Search term, abbreviation, or concept")):
    """Full-text search across all 42 technical terms, definitions, and system usage contexts."""
    return {
        "success": True,
        **search_glossary(query=q),
    }


@router.get("/glossary/{term_name}", summary="Get term definition by name or acronym")
def get_term(term_name: str):
    """Retrieve term definition, acronym expansion, domain category, and MemeGPT architecture context."""
    term = get_glossary_term_by_name(term_name=term_name)
    if not term:
        raise HTTPException(status_code=404, detail=f"Term '{term_name}' not found in glossary.")
    return {
        "success": True,
        "term": term,
    }


# ── Manifest & Health Endpoints (17_Appendix/README.md) ────────────────────

from app.services.appendix_manifest_service import (
    get_appendix_section_manifest,
    get_appendix_posture_summary,
    get_appendix_subsystem_health,
)


@router.get("/manifest", summary="Get Section 17 Appendix manifest")
def get_manifest():
    """Retrieve complete catalog, navigation hierarchy, and document directory for Section 17."""
    return {
        "success": True,
        **get_appendix_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated appendix posture")
def get_posture():
    """Retrieve consolidated counts across changelog versions, glossary terms, and external references."""
    return {
        "success": True,
        **get_appendix_posture_summary(),
    }


@router.get("/health", summary="Get appendix subsystem diagnostic health")
def get_health():
    """Evaluate completeness and diagnostic integrity of Section 17 documentation components."""
    return {
        "success": True,
        **get_appendix_subsystem_health(),
    }


# ── External References Endpoints (17_Appendix/References.md) ─────────────

from app.services.appendix_references_service import (
    get_all_quick_references,
    get_quick_reference_by_title,
    search_quick_references,
    get_quick_references_summary,
    validate_reference_links,
)


@router.get("/references", summary="Get all external quick reference links")
def list_references(category: Optional[str] = Query(None, description="Filter by category ('core_documentation', 'ai_ml_models', 'infrastructure')")):
    """Retrieve curated quick reference links across Core Documentation, AI/ML Models, and Infrastructure."""
    return {
        "success": True,
        **get_all_quick_references(category=category),
    }


@router.get("/references/summary", summary="Get references inventory summary")
def get_references_stats():
    """Retrieve summary counts across categories and resource groups."""
    return {
        "success": True,
        **get_quick_references_summary(),
    }


@router.get("/references/search", summary="Search quick reference links")
def search_ref_links(q: str = Query(..., min_length=1, description="Search query")):
    """Full-text search across reference link titles, URLs, descriptions, and MemeGPT roles."""
    return {
        "success": True,
        **search_quick_references(query=q),
    }


@router.get("/references/validate", summary="Validate external reference links")
def validate_links():
    """Validate all reference URLs for HTTPS schema compliance and domain formatting."""
    return {
        "success": True,
        **validate_reference_links(),
    }


@router.get("/references/{title_or_id}", summary="Get quick reference link by title or ID")
def get_single_reference(title_or_id: str):
    """Retrieve single external reference resource by ID (e.g. 'fastapi', 'qdrant', 'clip') or title."""
    ref = get_quick_reference_by_title(title_or_id=title_or_id)
    if not ref:
        raise HTTPException(status_code=404, detail=f"Reference '{title_or_id}' not found.")
    return {
        "success": True,
        "reference": ref,
    }
