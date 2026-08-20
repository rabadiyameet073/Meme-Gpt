"""Debugging Service for MemeGPT.
Specification: 09_Development/Debugging_Guide.md
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.debugging")

DEBUGGING_MATRIX = {
    "backend": [
        {
            "problem": "ModuleNotFoundError",
            "diagnosis": "Missing dependency",
            "fix": "pip install -r requirements.txt",
            "keywords": ["modulenotfounderror", "no module named"],
        },
        {
            "problem": "Model loading fails",
            "diagnosis": "Wrong Python version or incompatible wheel",
            "fix": "Ensure Python 3.11+ is active",
            "keywords": ["model loading fails", "python version", "torch"],
        },
        {
            "problem": "ConnectionRefusedError on Redis",
            "diagnosis": "Redis service is not running",
            "fix": "docker-compose up redis (or start local redis-server)",
            "keywords": ["connectionrefusederror", "redis", "6379"],
        },
        {
            "problem": "Groq API 429",
            "diagnosis": "Rate limit exceeded on LLM tier",
            "fix": "Wait 1 minute, or enable local Ollama fallback",
            "keywords": ["429", "groq", "rate limit exceeded", "too many requests"],
        },
        {
            "problem": "Qdrant connection timeout",
            "diagnosis": "Wrong QDRANT_URL or API key in environment",
            "fix": "Check QDRANT_URL and QDRANT_API_KEY in .env",
            "keywords": ["qdrant connection timeout", "qdrant timeout", "qdrant 6333"],
        },
        {
            "problem": "CORS error from frontend",
            "diagnosis": "Frontend origin not present in CORS allow list",
            "fix": "Add http://localhost:5173 / http://localhost:3000 to CORS origins",
            "keywords": ["cors", "access-control-allow-origin", "cross-origin"],
        },
    ],
    "frontend": [
        {
            "problem": "fetch returns CORS error",
            "diagnosis": "Backend CORS misconfigured",
            "fix": "Add frontend URL to CORS origins in FastAPI backend",
            "keywords": ["cors error", "fetch", "blocked by cors"],
        },
        {
            "problem": "Images not loading",
            "diagnosis": "CDN URL or bucket endpoint incorrect",
            "fix": "Check R2_ENDPOINT / CDN_URL in .env.local",
            "keywords": ["images not loading", "broken image", "cdn", "r2"],
        },
        {
            "problem": "Hydration mismatch",
            "diagnosis": "Server-rendered HTML and client state differ",
            "fix": "Use 'use client' directive for interactive components",
            "keywords": ["hydration", "hydration mismatch", "did not match"],
        },
        {
            "problem": "Build fails with type error",
            "diagnosis": "TypeScript strict mode compilation error",
            "fix": "Fix type annotations and avoid 'any'",
            "keywords": ["type error", "typescript", "tsc", "strict mode"],
        },
        {
            "problem": "Slow page load",
            "diagnosis": "Large JavaScript client bundle",
            "fix": "Check 'npm run build' output for bundle sizes and lazy-load components",
            "keywords": ["slow page load", "bundle size", "lcp"],
        },
    ],
    "ai_pipeline": [
        {
            "problem": "Low search quality",
            "diagnosis": "Embeddings are not normalized before cosine search",
            "fix": "Add normalize_embeddings=True to sentence-transformers encoder",
            "keywords": ["low search quality", "bad search results", "embeddings not normalized"],
        },
        {
            "problem": "Emotion detection wrong",
            "diagnosis": "Input text is too short (<10 characters)",
            "fix": "Ensure query length > 10 characters for accurate emotion extraction",
            "keywords": ["emotion detection wrong", "short text", "emotion"],
        },
        {
            "problem": "Groq returns gibberish",
            "diagnosis": "Sampling temperature is set too high",
            "fix": "Lower temperature to 0.1 for structured JSON output",
            "keywords": ["gibberish", "groq returns gibberish", "temperature"],
        },
        {
            "problem": "Qdrant returns 0 results",
            "diagnosis": "Similarity score threshold is too strict",
            "fix": "Lower score threshold from 0.45 to 0.35 fallback",
            "keywords": ["0 results", "qdrant returns 0", "score threshold"],
        },
        {
            "problem": "CLIP model OOM",
            "diagnosis": "Insufficient RAM holding both CLIP and LLM at runtime",
            "fix": "Only load CLIP during offline indexing, not during request runtime",
            "keywords": ["clip", "oom", "out of memory", "cuda oom"],
        },
    ],
    "database": [
        {
            "problem": "SQLite locked",
            "diagnosis": "Concurrent write requests locking SQLite database",
            "fix": "Use single writer pattern or switch to PostgreSQL",
            "keywords": ["sqlite locked", "database is locked", "operationalerror: database is locked"],
        },
        {
            "problem": "Migration fails",
            "diagnosis": "Schema conflict between local state and migration files",
            "fix": "Run 'npx prisma migrate reset' (dev only!) or check alembic heads",
            "keywords": ["migration fails", "schema conflict", "prisma migrate reset", "alembic"],
        },
        {
            "problem": "Slow queries",
            "diagnosis": "Missing database index on queried columns",
            "fix": "Add index on searched columns (e.g. meme_id, created_at, category)",
            "keywords": ["slow queries", "missing index", "query time"],
        },
    ],
}

QUICK_DEBUG_COMMANDS = [
    {
        "target": "Backend Health",
        "command": "curl http://localhost:8000/health",
        "description": "Check if FastAPI server is responsive and healthy",
    },
    {
        "target": "Test Search Endpoint",
        "command": "curl -X POST http://localhost:8000/api/v1/search -H \"Content-Type: application/json\" -d '{\"query\": \"test\"}'",
        "description": "Test core AI vector search pipeline",
    },
    {
        "target": "Check Qdrant Vector DB",
        "command": "curl http://localhost:6333/collections/memes",
        "description": "Verify Qdrant collection status and vector counts",
    },
    {
        "target": "Check Redis Cache",
        "command": "redis-cli ping",
        "description": "Verify Redis is online and responding with PONG",
    },
    {
        "target": "Inspect Environment Variables",
        "command": "python -c \"from app.core.config import get_settings; print(get_settings().dict())\"",
        "description": "Check currently loaded configuration parameters",
    },
]

DEBUGGING_BEST_PRACTICES = [
    "Check health endpoint first — if /health fails, fix infrastructure first",
    "Read error messages carefully — FastAPI gives detailed Pydantic validation errors",
    "Test in isolation — test one service at a time (backend, then frontend)",
    "Use --reload flag — auto-restart server on code changes during development",
    "Check .env first — 90% of 'it doesn't work' issues are missing env vars",
]


def get_debugging_matrix(category: Optional[str] = None) -> Dict[str, Any]:
    """Return categorized debugging matrix."""
    if category and category.lower() in DEBUGGING_MATRIX:
        return {
            "category": category.lower(),
            "items": DEBUGGING_MATRIX[category.lower()],
        }
    return {
        "categories": list(DEBUGGING_MATRIX.keys()),
        "matrix": DEBUGGING_MATRIX,
    }


def get_quick_debug_commands() -> List[Dict[str, str]]:
    """Return list of quick debugging curl and cli commands."""
    return QUICK_DEBUG_COMMANDS


def get_debugging_best_practices() -> List[str]:
    """Return 5 core debugging best practices."""
    return DEBUGGING_BEST_PRACTICES


def diagnose_issue(symptom_text: str) -> Dict[str, Any]:
    """Diagnose issue based on error string or symptom and suggest immediate remedies."""
    symptom_lower = symptom_text.lower()
    matches = []

    for category, items in DEBUGGING_MATRIX.items():
        for item in items:
            for kw in item.get("keywords", []):
                if kw in symptom_lower:
                    matches.append({
                        "category": category,
                        "problem": item["problem"],
                        "diagnosis": item["diagnosis"],
                        "fix": item["fix"],
                        "matched_keyword": kw,
                    })
                    break

    if matches:
        matches.sort(key=lambda x: len(x["matched_keyword"]), reverse=True)
        return {
            "has_match": True,
            "total_matches": len(matches),
            "top_match": matches[0],
            "all_matches": matches,
        }
    else:
        return {
            "has_match": False,
            "total_matches": 0,
            "top_match": None,
            "fallback_advice": "Check .env configuration and test health endpoint via 'curl http://localhost:8000/health'",
            "all_matches": [],
        }
