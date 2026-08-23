"""Comprehensive Debug Guide and Diagnostic Service for MemeGPT.
Specification: 14_Troubleshooting/Debug_Guide.md

Covers:
- Backend Debugging (Debug logs, curl test commands, scoring breakdown, embedding vector inspection)
- Frontend Debugging (Chrome DevTools 5 tabs, JS console snippets, localStorage inspection)
- Database Debugging (Prisma Studio, SQL inspection queries, seed count verification)
- ML Model Debugging (Emotion detection DistilRoBERTa, Groq Llama-3 intent parsing)
- Network Debugging (DNS nslookup, netstat port audit, openssl certificate verify, curl latency timing)
- Search Quality Decision Tree & Interactive Diagnostic Evaluator
"""

from typing import Any, Dict, List, Optional


# ── 1. Backend Debugging Guide ─────────────────────────────────────────────────

BACKEND_DEBUG_PROCEDURES = {
    "run_with_debug_logging": {
        "command": "LOG_LEVEL=DEBUG python -m uvicorn app.main:app --reload --port 8000",
        "description": "Starts FastAPI with live code reload and verbose debug log output.",
    },
    "curl_endpoint_tests": [
        {
            "name": "Health check",
            "command": "curl -s http://localhost:8000/health | python -m json.tool",
            "expected_status": 200,
        },
        {
            "name": "Search endpoint",
            "command": 'curl -s -X POST http://localhost:8000/search -H "Content-Type: application/json" -d \'{"query": "Monday morning", "limit": 3}\' | python -m json.tool',
            "expected_status": 200,
        },
        {
            "name": "Single meme retrieval",
            "command": "curl -s http://localhost:8000/memes/THIS_IS_FINE_ID | python -m json.tool",
            "expected_status": 200,
        },
    ],
    "search_quality_debug_script": (
        "from app.meme_matcher import match_memes\n\n"
        "results = match_memes('Monday morning', limit=5)\n"
        "for r in results:\n"
        "    print(f\"{r['name']}: keyword={r.get('keyword_score',0):.2f} \""
        "f\"semantic={r.get('semantic_score',0):.2f} \""
        "f\"emotion={r.get('emotion_score',0):.2f} \""
        "f\"composite={r.get('composite_score',0):.2f}\")"
    ),
    "embedding_generation_debug_script": (
        "from app.semantic_search import embed_text\n"
        "import numpy as np\n\n"
        "vec = embed_text('test query')\n"
        "print(f'Shape: {len(vec)}')\n"
        "print(f'Norm: {np.linalg.norm(vec):.4f}')  # Should be ~1.0\n"
        "print(f'Min: {min(vec):.4f}, Max: {max(vec):.4f}')"
    ),
}


def get_backend_debug_procedures() -> Dict[str, Any]:
    """Return backend debugging commands, curl recipes, and Python diagnostic scripts."""
    return BACKEND_DEBUG_PROCEDURES


# ── 2. Frontend Debugging Guide ────────────────────────────────────────────────

FRONTEND_DEBUG_GUIDE = {
    "chrome_devtools_tabs": [
        {"tab": "Console", "hotkey": "F12 -> Console", "purpose": "Check for JavaScript errors, unhandled rejections, and runtime warnings."},
        {"tab": "Network", "hotkey": "F12 -> Network", "purpose": "Verify API request headers, response payload JSON, status codes, and timing."},
        {"tab": "Performance", "hotkey": "F12 -> Performance", "purpose": "Record and analyze slow React component renders and FPS drops."},
        {"tab": "React DevTools", "hotkey": "React Extension", "purpose": "Inspect component hierarchy, state hooks, and prop drilling."},
        {"tab": "Application", "hotkey": "F12 -> Application -> Local Storage", "purpose": "Inspect saved favorites, theme preferences, and search history."},
    ],
    "common_console_commands": [
        {"name": "Check API connectivity", "code": "fetch('http://localhost:8000/health').then(r => r.json()).then(console.log);"},
        {"name": "Check localStorage favorites", "code": "JSON.parse(localStorage.getItem('favorites'));"},
        {"name": "Clear cached data", "code": "localStorage.clear();"},
    ],
}


def get_frontend_debug_guide() -> Dict[str, Any]:
    """Return Chrome DevTools workflows and browser console debugging snippets."""
    return FRONTEND_DEBUG_GUIDE


# ── 3. Database Debugging Guide ────────────────────────────────────────────────

DATABASE_DEBUG_COMMANDS = {
    "visual_browser": {
        "tool": "Prisma Studio",
        "command": "npx prisma studio",
        "description": "Visual web GUI for exploring, modifying, and filtering database records.",
    },
    "sql_inspection_queries": [
        {"name": "Check total meme count", "command": 'sqlite3 prisma/dev.db "SELECT COUNT(*) FROM Meme;"'},
        {"name": "Check top viral memes", "command": 'sqlite3 prisma/dev.db "SELECT name, viralScore FROM Meme ORDER BY viralScore DESC LIMIT 10;"'},
        {"name": "Verify seeder completion", "command": 'sqlite3 prisma/dev.db "SELECT COUNT(*) as total FROM Meme;"  # Should be 1000+'},
    ],
}


def get_database_debug_commands() -> Dict[str, Any]:
    """Return database exploration commands and sanity SQL queries."""
    return DATABASE_DEBUG_COMMANDS


# ── 4. ML Model Debugging Guide ────────────────────────────────────────────────

ML_DEBUG_RECIPES = {
    "emotion_detection_test": (
        "from transformers import pipeline\n\n"
        "classifier = pipeline('text-classification',\n"
        "    model='j-hartmann/emotion-english-distilroberta-base',\n"
        "    return_all_scores=True)\n"
        "results = classifier(\"I'm so frustrated with this bug!\")\n"
        "for r in sorted(results[0], key=lambda x: -x['score'])[:3]:\n"
        "    print(f\"{r['label']}: {r['score']:.2%}\")"
    ),
    "groq_intent_parsing_test": (
        "import groq\n\n"
        "client = groq.Groq(api_key='your_key')\n"
        "response = client.chat.completions.create(\n"
        "    model='llama-3.1-8b-instant',\n"
        "    messages=[{'role': 'user', 'content': 'Parse: Monday morning'}],\n"
        "    temperature=0.1, max_tokens=200\n"
        ")\n"
        "print(response.choices[0].message.content)"
    ),
}


def get_ml_debug_recipes() -> Dict[str, Any]:
    """Return ML model standalone debugging and validation scripts."""
    return ML_DEBUG_RECIPES


# ── 5. Network Debugging Tools ─────────────────────────────────────────────────

NETWORK_DEBUG_TOOLS = [
    {
        "issue": "DNS resolution",
        "tool": "nslookup",
        "command": "nslookup api.memegpt.com",
        "description": "Verifies DNS record resolution and IP propagation.",
    },
    {
        "issue": "Port availability",
        "tool": "netstat",
        "command": "netstat -ano | findstr :8000",
        "description": "Checks whether local port 8000 is open or in conflict with another process.",
    },
    {
        "issue": "SSL certificate",
        "tool": "openssl",
        "command": "openssl s_client -connect api.memegpt.com:443",
        "description": "Validates SSL certificate chain, cipher suite, and TLS expiration date.",
    },
    {
        "issue": "API response time",
        "tool": "curl",
        "command": 'curl -w "@curl-format.txt" -o /dev/null -s api.memegpt.com/health',
        "description": "Measures precise DNS lookup, TCP connect, TTFB, and total transfer timings.",
    },
]


def get_network_debug_tools() -> Dict[str, Any]:
    """Return network diagnostic CLI utilities table."""
    return {
        "total_tools": len(NETWORK_DEBUG_TOOLS),
        "tools": NETWORK_DEBUG_TOOLS,
    }


# ── 6. Search Quality Decision Tree ───────────────────────────────────────────

SEARCH_QUALITY_DECISION_TREE = {
    "title": "Decision Tree: Search Returns Bad Results",
    "root_step": {
        "step": 1,
        "question": "Database seeded?",
        "if_no": "Run: npm run seed or python seed_memes.py",
        "if_yes": {
            "step": 2,
            "question": "Embeddings generated in Qdrant?",
            "if_no": "Run: npm run embeddings or python scripts/index_qdrant.py",
            "if_yes": {
                "step": 3,
                "question": "Groq LLM API working?",
                "if_no": "Check GROQ_API_KEY environment variable and Groq service status",
                "if_yes": {
                    "step": 4,
                    "question": "Qdrant vector cluster connected?",
                    "if_no": "Check QDRANT_URL and QDRANT_API_KEY in .env",
                    "if_yes": {
                        "step": 5,
                        "question": "Check score_threshold parameter",
                        "action": "Score threshold may be too high (>0.45) or too low (<0.20); adjust to 0.35 baseline",
                    },
                },
            },
        },
    },
}


def get_search_quality_decision_tree() -> Dict[str, Any]:
    """Return the 5-step search quality debugging decision tree."""
    return SEARCH_QUALITY_DECISION_TREE


def simulate_search_quality_diagnosis(
    db_seeded: bool = True,
    embeddings_generated: bool = True,
    groq_working: bool = True,
    qdrant_connected: bool = True,
) -> Dict[str, Any]:
    """Evaluate pipeline state against search quality decision tree and output targeted action."""
    if not db_seeded:
        return {
            "step": 1,
            "root_cause": "Database is not seeded",
            "action": "Run: python seed_memes.py",
            "status": "ACTION_REQUIRED",
        }
    if not embeddings_generated:
        return {
            "step": 2,
            "root_cause": "Vector embeddings not indexed in Qdrant",
            "action": "Run: python scripts/index_qdrant.py",
            "status": "ACTION_REQUIRED",
        }
    if not groq_working:
        return {
            "step": 3,
            "root_cause": "Groq LLM intent parser unreachable or invalid key",
            "action": "Check GROQ_API_KEY in .env and check status.groq.com",
            "status": "ACTION_REQUIRED",
        }
    if not qdrant_connected:
        return {
            "step": 4,
            "root_cause": "Qdrant vector cluster unreachable",
            "action": "Check QDRANT_URL and QDRANT_API_KEY in .env",
            "status": "ACTION_REQUIRED",
        }

    return {
        "step": 5,
        "root_cause": "All pipeline subsystems operational",
        "action": "Tune score_threshold (recommended: 0.35) and verify query keyword match weights",
        "status": "ALL_SUBSYSTEMS_HEALTHY",
    }
