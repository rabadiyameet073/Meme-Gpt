"""References Section Manifest and Resource Health Service for MemeGPT.
Specification: 16_References/README.md

Covers:
- Section 16R Documentation Manifest & Navigation (Technology_Stack, External_Resources, README)
- Consolidated External Resources & Citations Posture Summary
- Live Subsystem Health & Citation Index Diagnostic Evaluator
"""

from typing import Any, Dict, List
from app.services.external_resources_service import get_external_resources_summary


# ── 1. Section 16R Documentation Manifest ──────────────────────────────────────

REFERENCES_SECTION_MANIFEST = [
    {
        "file": "Technology_Stack.md",
        "title": "Comprehensive Technology Stack Catalog",
        "description": "Complete breakdown of 20+ technologies, frameworks, and tools across Frontend, Backend, AI/ML, Storage, and DevOps with selection rationales.",
        "status": "IN_PROGRESS",
        "route_prefix": "/api/v1/references/tech-stack",
    },
    {
        "file": "External_Resources.md",
        "title": "External Resources, Citations & Research Papers",
        "description": "25 official documentation links, 6 foundational AI research papers, 4 meme data source APIs, and 5 developer community channels.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/references/resources",
    },
    {
        "file": "README.md",
        "title": "References Section Manifest & Navigation",
        "description": "Section index, documentation directory, consolidated references posture, and global diagnostic health checks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/references",
    },
]


def get_references_section_manifest() -> Dict[str, Any]:
    """Return Section 16R documentation catalog and navigation metadata."""
    completed = sum(1 for d in REFERENCES_SECTION_MANIFEST if d["status"] == "COMPLETED")
    total = len(REFERENCES_SECTION_MANIFEST)

    return {
        "section_id": "16_References",
        "title": "16 — References",
        "description": "External references, technology stack selections, research papers, and developer resources for MemeGPT.",
        "total_documents": total,
        "completed_documents": completed,
        "completion_percentage": f"{round((completed / total) * 100, 1)}%",
        "navigation": {
            "previous": {
                "section": "15_FAQs",
                "title": "15 — FAQs",
                "path": "15_FAQs/README.md",
            },
            "next": {
                "section": "17_Appendix",
                "title": "17 — Appendix",
                "path": "17_Appendix/README.md",
            },
        },
        "documents": REFERENCES_SECTION_MANIFEST,
    }


# ── 2. Consolidated References Posture Summary ─────────────────────────────────

def get_references_posture_summary() -> Dict[str, Any]:
    """Return consolidated external resources, papers, and citations posture."""
    summary = get_external_resources_summary()

    return {
        "resources_readiness": {
            "grand_total_external_resources": summary["grand_total_external_resources"],
            "official_documentation_links": summary["total_official_documentation"],
            "documentation_categories": summary["documentation_categories"],
            "foundational_research_papers": summary["total_research_papers"],
            "meme_data_providers": summary["total_meme_sources"],
            "community_forums_and_chats": summary["total_community_channels"],
        },
        "citation_coverage": {
            "embedding_models_cited": ["Sentence-BERT (2019)", "MTEB (2023)", "Word2Vec (2013)"],
            "multimodal_vision_cited": ["CLIP (2021)", "BLIP (2022)"],
            "architecture_cited": ["Attention Is All You Need (2017)"],
        },
    }


# ── 3. References Subsystem Health Diagnostic ──────────────────────────────────

def get_references_subsystem_health() -> Dict[str, Any]:
    """Evaluate real-time references database and citation index health."""
    summary = get_external_resources_summary()

    healthy = summary["grand_total_external_resources"] == 40

    return {
        "status": "HEALTHY" if healthy else "DEGRADED",
        "external_resources_loaded": True,
        "research_papers_indexed": summary["total_research_papers"],
        "official_docs_indexed": summary["total_official_documentation"],
        "meme_sources_indexed": summary["total_meme_sources"],
        "community_channels_indexed": summary["total_community_channels"],
        "grand_total_assets": summary["grand_total_external_resources"],
    }
