"""Appendix External Quick References Service for MemeGPT.
Specification: 17_Appendix/References.md

Covers:
- 14 Curated Quick Reference Links across 3 Groups:
  1. Core Documentation (FastAPI, React, Qdrant, Supabase, Prisma)
  2. AI/ML Models (MiniLM-L6-v2, CLIP ViT-B/32, BLIP Captioning, Emotion Model, Groq API)
  3. Infrastructure (Vercel, Render, Cloudflare R2, Upstash Redis)
- Search, category filtering, and link metadata validation.
"""

from typing import Any, Dict, List, Optional


# ── Quick References Database (14 Resources) ──────────────────────────────────

QUICK_REFERENCES: List[Dict[str, Any]] = [
    # Core Documentation
    {
        "id": "fastapi",
        "title": "FastAPI Docs",
        "category": "core_documentation",
        "url": "https://fastapi.tiangolo.com",
        "description": "API framework",
        "role_in_memegpt": "Backend web server and REST API routing with automatic OpenAPI docs.",
    },
    {
        "id": "react",
        "title": "React Docs",
        "category": "core_documentation",
        "url": "https://react.dev",
        "description": "Frontend library",
        "role_in_memegpt": "Frontend UI library bundled with Vite for fast client rendering.",
    },
    {
        "id": "qdrant",
        "title": "Qdrant Docs",
        "category": "core_documentation",
        "url": "https://qdrant.tech/documentation",
        "description": "Vector database",
        "role_in_memegpt": "Stores 384-dim and 512-dim meme vectors for sub-50ms HNSW similarity search.",
    },
    {
        "id": "supabase",
        "title": "Supabase Docs",
        "category": "core_documentation",
        "url": "https://supabase.com/docs",
        "description": "PostgreSQL + Auth",
        "role_in_memegpt": "Managed PostgreSQL relational database with connection pooling and JWT auth.",
    },
    {
        "id": "prisma",
        "title": "Prisma Docs",
        "category": "core_documentation",
        "url": "https://www.prisma.io/docs",
        "description": "ORM",
        "role_in_memegpt": "Type-safe database ORM managing schema definitions and migrations.",
    },

    # AI/ML Models
    {
        "id": "minilm",
        "title": "MiniLM-L6-v2",
        "category": "ai_ml_models",
        "url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
        "description": "Text embeddings",
        "role_in_memegpt": "Generates 384-dimensional dense semantic text vectors in ~50ms.",
    },
    {
        "id": "clip",
        "title": "CLIP ViT-B/32",
        "category": "ai_ml_models",
        "url": "https://huggingface.co/openai/clip-vit-base-patch32",
        "description": "Image embeddings",
        "role_in_memegpt": "Generates 512-dimensional joint vision-language embeddings for visual meme search.",
    },
    {
        "id": "blip",
        "title": "BLIP Captioning",
        "category": "ai_ml_models",
        "url": "https://huggingface.co/Salesforce/blip-image-captioning-base",
        "description": "Image descriptions",
        "role_in_memegpt": "Generates synthetic descriptive captions for uncaptioned meme templates.",
    },
    {
        "id": "emotion_model",
        "title": "Emotion Model",
        "category": "ai_ml_models",
        "url": "https://huggingface.co/j-hartmann/emotion-english-distilroberta-base",
        "description": "Emotion detection",
        "role_in_memegpt": "Classifies queries into 7 emotional states (joy, sadness, anger, fear, surprise, disgust, neutral).",
    },
    {
        "id": "groq_api",
        "title": "Groq API",
        "category": "ai_ml_models",
        "url": "https://console.groq.com/docs",
        "description": "LLM inference",
        "role_in_memegpt": "Powers Llama 3.1 8B query intent parsing on custom LPU hardware with sub-200ms TTFT.",
    },

    # Infrastructure
    {
        "id": "vercel",
        "title": "Vercel Docs",
        "category": "infrastructure",
        "url": "https://vercel.com/docs",
        "description": "Frontend hosting",
        "role_in_memegpt": "Hosts React/Next.js frontend with global edge caching and automatic preview deploys.",
    },
    {
        "id": "render",
        "title": "Render Docs",
        "category": "infrastructure",
        "url": "https://render.com/docs",
        "description": "Backend hosting",
        "role_in_memegpt": "Hosts containerized FastAPI backend web service with zero-downtime deploys.",
    },
    {
        "id": "cloudflare_r2",
        "title": "Cloudflare R2",
        "category": "infrastructure",
        "url": "https://developers.cloudflare.com/r2",
        "description": "Object storage",
        "role_in_memegpt": "Stores meme GIFs, PNGs, and MP4 files with zero egress bandwidth charges.",
    },
    {
        "id": "upstash_redis",
        "title": "Upstash Redis",
        "category": "infrastructure",
        "url": "https://upstash.com/docs",
        "description": "Serverless Redis",
        "role_in_memegpt": "Provides serverless caching for search queries and rate-limiting sliding windows.",
    },
]


# ── Service Functions ──────────────────────────────────────────────────────────

def get_all_quick_references(category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all 14 quick reference resources or filter by category ('core_documentation', 'ai_ml_models', 'infrastructure')."""
    items = QUICK_REFERENCES

    if category:
        cat_clean = category.strip().lower()
        items = [r for r in items if r["category"] == cat_clean]

    return {
        "total_references": len(items),
        "category_filter": category,
        "references": items,
    }


def get_quick_reference_by_title(title_or_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve quick reference resource by exact ID or title."""
    clean = title_or_id.strip().lower()
    for r in QUICK_REFERENCES:
        if r["id"] == clean or r["title"].lower() == clean:
            return r
    return None


def search_quick_references(query: str) -> Dict[str, Any]:
    """Full-text search across titles, URLs, descriptions, and MemeGPT roles."""
    q_lower = query.strip().lower()
    matches = []

    for r in QUICK_REFERENCES:
        if (
            q_lower in r["title"].lower()
            or q_lower in r["url"].lower()
            or q_lower in r["description"].lower()
            or q_lower in r["role_in_memegpt"].lower()
            or q_lower in r["category"].lower()
        ):
            matches.append(r)

    return {
        "query": query,
        "total_matches": len(matches),
        "matches": matches,
    }


def get_quick_references_summary() -> Dict[str, Any]:
    """Retrieve summary statistics across all 14 reference links and category distributions."""
    category_counts = {}
    for r in QUICK_REFERENCES:
        cat = r["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "total_references": len(QUICK_REFERENCES),
        "categories_count": len(category_counts),
        "category_breakdown": {
            "core_documentation": category_counts.get("core_documentation", 0),
            "ai_ml_models": category_counts.get("ai_ml_models", 0),
            "infrastructure": category_counts.get("infrastructure", 0),
        },
        "all_categories": list(category_counts.keys()),
    }


def validate_reference_links() -> Dict[str, Any]:
    """Validate that all 14 reference links have valid HTTPS schemas and proper documentation domains."""
    valid_links = []
    for r in QUICK_REFERENCES:
        is_https = r["url"].startswith("https://")
        has_domain = "." in r["url"].replace("https://", "")
        valid_links.append({
            "id": r["id"],
            "title": r["title"],
            "url": r["url"],
            "is_valid_https": is_https,
            "status": "VALID" if (is_https and has_domain) else "INVALID",
        })

    return {
        "total_links_validated": len(valid_links),
        "valid_count": sum(1 for l in valid_links if l["status"] == "VALID"),
        "invalid_count": sum(1 for l in valid_links if l["status"] == "INVALID"),
        "results": valid_links,
    }
