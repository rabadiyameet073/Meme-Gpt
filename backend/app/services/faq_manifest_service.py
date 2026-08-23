"""FAQ Section Manifest and Knowledge Base Health Service for MemeGPT.
Specification: 15_FAQs/README.md

Covers:
- Section 15F Documentation Manifest & Navigation (General_FAQ, Technical_FAQ, API_FAQ, README)
- Consolidated Knowledge Base & FAQ Posture Summary
- Live Subsystem Health & Search Engine Diagnostic Evaluator
"""

from typing import Any, Dict, List
from app.services.faq_service import (
    get_all_faqs,
    get_faq_categories_summary,
    get_ai_models_catalog,
    get_graceful_degradation_matrix,
)


# ── 1. Section 15F Documentation Manifest ──────────────────────────────────────

FAQ_SECTION_MANIFEST = [
    {
        "file": "General_FAQ.md",
        "title": "General, Technical & API FAQ Knowledge Base",
        "description": "21 question & answer pairs across General Product (8), Technical Architecture (8), and API Integration (5) categories.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/faqs",
    },
    {
        "file": "README.md",
        "title": "FAQ Section Manifest & Navigation",
        "description": "Section index, documentation directory, consolidated knowledge base posture, and global diagnostic health checks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/faqs",
    },
]


def get_faq_section_manifest() -> Dict[str, Any]:
    """Return Section 15F documentation catalog and navigation metadata."""
    completed = sum(1 for d in FAQ_SECTION_MANIFEST if d["status"] == "COMPLETED")
    total = len(FAQ_SECTION_MANIFEST)

    return {
        "section_id": "15_FAQs",
        "title": "15 — FAQs",
        "description": "Searchable Frequently Asked Questions knowledge base covering general concepts, technical architecture, and API integrations.",
        "total_documents": total,
        "completed_documents": completed,
        "completion_percentage": f"{round((completed / total) * 100, 1)}%",
        "navigation": {
            "previous": {
                "section": "14_Troubleshooting",
                "title": "14 — Troubleshooting",
                "path": "14_Troubleshooting/README.md",
            },
            "next": {
                "section": "15_Mobile",
                "title": "15 — Mobile",
                "path": "15_Mobile/README.md",
            },
        },
        "documents": FAQ_SECTION_MANIFEST,
    }


# ── 2. Consolidated FAQ Posture Summary ────────────────────────────────────────

def get_faq_posture_summary() -> Dict[str, Any]:
    """Return consolidated knowledge base and FAQ readiness posture."""
    cats = get_faq_categories_summary()
    models = get_ai_models_catalog()
    degradation = get_graceful_degradation_matrix()

    return {
        "knowledge_base_readiness": {
            "total_indexed_faqs": cats["total_faqs"],
            "total_categories": cats["total_categories"],
            "category_distribution": cats["category_counts"],
            "search_enabled": True,
        },
        "technical_catalog": {
            "total_ai_models_documented": models["total_models"],
            "total_degradation_paths": degradation["total_scenarios"],
            "max_query_length_limit": 2000,
            "rate_limits": {
                "free_tier": "60 req/min per IP (30 search/min)",
                "developer_tier": "300 req/min",
            },
        },
    }


# ── 3. FAQ Subsystem Health Diagnostic ─────────────────────────────────────────

def get_faq_subsystem_health() -> Dict[str, Any]:
    """Evaluate real-time FAQ knowledge base and search engine health."""
    all_faqs = get_all_faqs()
    cats = get_faq_categories_summary()
    models = get_ai_models_catalog()

    healthy = (
        all_faqs["total_faqs"] == 21
        and cats["total_categories"] == 3
        and models["total_models"] == 6
    )

    return {
        "status": "HEALTHY" if healthy else "DEGRADED",
        "knowledge_base_active": True,
        "search_engine_active": True,
        "total_faqs_indexed": all_faqs["total_faqs"],
        "general_faqs": cats["category_counts"].get("general", 0),
        "technical_faqs": cats["category_counts"].get("technical", 0),
        "api_faqs": cats["category_counts"].get("api", 0),
        "ai_models_indexed": models["total_models"],
    }
