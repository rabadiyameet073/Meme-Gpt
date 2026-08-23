"""Troubleshooting Section Manifest and Diagnostic Health Service for MemeGPT.
Specification: 14_Troubleshooting/README.md

Covers:
- Section 14 Documentation Manifest & Navigation (Common_Issues, Debug_Guide, README)
- Consolidated Troubleshooting & Diagnostics Posture Summary
- Live Subsystem Health & Troubleshooting Diagnostic Evaluator
"""

from typing import Any, Dict, List
from app.services.troubleshooting_service import get_common_issues_catalog, get_debugging_best_practices


# ── 1. Section 14 Documentation Manifest ───────────────────────────────────────

TROUBLESHOOTING_SECTION_MANIFEST = [
    {
        "file": "Common_Issues.md",
        "title": "Common Issues & Quick Diagnostics",
        "description": "Quick diagnostic flowchart, 8 common error runbooks with root causes and CLI fixes, and 5 debugging best practices.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/troubleshooting/issues",
    },
    {
        "file": "Debug_Guide.md",
        "title": "Comprehensive Component Debug Guide",
        "description": "Layer-by-layer debugging recipes for Backend, Frontend, Database, ML pipelines, Network diagnostics, and the search quality decision tree.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/troubleshooting/debug",
    },
    {
        "file": "README.md",
        "title": "Troubleshooting Section Manifest",
        "description": "Section index, documentation directory, consolidated troubleshooting posture, and global diagnostic health checks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/troubleshooting",
    },
]


def get_troubleshooting_section_manifest() -> Dict[str, Any]:
    """Return Section 14 documentation catalog and navigation metadata."""
    completed = sum(1 for d in TROUBLESHOOTING_SECTION_MANIFEST if d["status"] == "COMPLETED")
    total = len(TROUBLESHOOTING_SECTION_MANIFEST)

    return {
        "section_id": "14_Troubleshooting",
        "title": "14 — Troubleshooting",
        "description": "Searchable troubleshooting guide, quick diagnostic flowcharts, and component debugging procedures for MemeGPT.",
        "total_documents": total,
        "completed_documents": completed,
        "completion_percentage": f"{round((completed / total) * 100, 1)}%",
        "navigation": {
            "previous": {
                "section": "13_Project_Management",
                "title": "13 — Project Management",
                "path": "13_Project_Management/README.md",
            },
            "next": {
                "section": "15_FAQs",
                "title": "15 — FAQs",
                "path": "15_FAQs/README.md",
            },
        },
        "documents": TROUBLESHOOTING_SECTION_MANIFEST,
    }


# ── 2. Consolidated Troubleshooting Posture Summary ───────────────────────────

def get_troubleshooting_posture_summary() -> Dict[str, Any]:
    """Return consolidated troubleshooting and diagnostic readiness posture."""
    issues = get_common_issues_catalog()
    practices = get_debugging_best_practices()

    return {
        "diagnostic_readiness": {
            "flowcharts_configured": [
                "Quick Diagnostic Flowchart (/health -> /search -> Qdrant)",
                "Search Quality Decision Tree (DB -> Embeddings -> Groq -> Qdrant -> Threshold)",
            ],
            "total_documented_issues": issues["total_issues"],
            "supported_categories": [
                "Environment & Dependencies",
                "Networking & Security",
                "Database & Vector Store",
                "Cache & Rate Limiting",
                "Search & Relevance",
                "Performance & Latency",
                "Frontend & Build Tools",
                "Deployment & Cloud Infrastructure",
            ],
            "debugging_best_practices_count": practices["total_practices"],
        },
        "component_debuggers": {
            "backend": "Uvicorn debug mode, endpoint curl testing, scoring and embedding diagnostics",
            "frontend": "Chrome DevTools (Console, Network, Performance, React, LocalStorage)",
            "database": "Prisma Studio, SQLite/PostgreSQL count and viralScore inspection queries",
            "ml_models": "DistilRoBERTa emotion and Groq Llama-3 intent parsing standalone test scripts",
            "network": "nslookup, netstat port audit, openssl cert verify, curl timing format",
        },
    }


# ── 3. Troubleshooting Diagnostic Health Check ────────────────────────────────

def get_troubleshooting_subsystem_health() -> Dict[str, Any]:
    """Evaluate real-time troubleshooting subsystem health."""
    issues = get_common_issues_catalog()
    practices = get_debugging_best_practices()

    healthy = (
        issues["total_issues"] == 8
        and practices["total_practices"] == 5
    )

    return {
        "status": "HEALTHY" if healthy else "DEGRADED",
        "diagnostic_engine_active": True,
        "issue_catalog_loaded": True,
        "debugging_recipes_active": True,
        "total_issues_indexed": issues["total_issues"],
        "total_best_practices": practices["total_practices"],
    }
