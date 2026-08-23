"""Common Issues & System Diagnostic Troubleshooting Service for MemeGPT.
Specification: 14_Troubleshooting/Common_Issues.md

Covers:
- Quick Diagnostic Flowchart Decision Tree (/health check -> Search check -> Qdrant connectivity -> Frontend)
- 8 Common Issues & Error Runbooks (ModuleNotFoundError, CORS, Qdrant, Redis, Zero Results, Slow Search, Frontend Build, Railway Deploy)
- 5 Debugging Best Practices
- Automated Symptom Diagnosis Engine
"""

from typing import Any, Dict, List, Optional


# ── 1. Quick Diagnostic Flowchart ──────────────────────────────────────────────

DIAGNOSTIC_FLOWCHART = {
    "title": "Quick Diagnostic Flowchart",
    "description": "Step-by-step diagnostic decision tree from initial symptom to root cause isolation.",
    "root_step": {
        "step_id": 1,
        "question": "curl /health returns 200 OK?",
        "if_no": {
            "root_cause": "Backend is down or container failed to start",
            "action": "Check Railway logs (`railway logs --service api`) or Docker container status (`docker logs`)",
        },
        "if_yes": {
            "step_id": 2,
            "question": "Search endpoint (/search) returns meme results?",
            "if_yes": {
                "root_cause": "Backend search pipeline is fully operational",
                "action": "Backend is fine; check frontend networking, state, or React render errors",
            },
            "if_no": {
                "step_id": 3,
                "question": "Qdrant vector database is connected?",
                "if_no": {
                    "root_cause": "Vector database unreachable",
                    "action": "Check QDRANT_URL and QDRANT_API_KEY environment variables and cluster status",
                },
                "if_yes": {
                    "root_cause": "Search parameters too restrictive or empty collection",
                    "action": "Check score_threshold (lower from 0.45 to 0.35) and verify Qdrant collection item count",
                },
            },
        },
    },
}


def get_diagnostic_flowchart() -> Dict[str, Any]:
    """Return the quick diagnostic flowchart decision tree."""
    return DIAGNOSTIC_FLOWCHART


# ── 2. 8 Common Issues Catalog ─────────────────────────────────────────────────

COMMON_ISSUES_CATALOG = [
    {
        "id": "ERR_MISSING_DEPENDENCY",
        "title": "ModuleNotFoundError: No module named 'sentence_transformers'",
        "category": "Environment & Dependencies",
        "cause": "Python virtual environment dependencies not installed.",
        "symptom": "Backend crash on startup or import error during ML initialization.",
        "fix_command": "cd services/api && pip install -r requirements.txt",
        "details": "Ensure you are operating inside the active virtualenv prior to running uvicorn.",
    },
    {
        "id": "ERR_CORS_BLOCKED",
        "title": "CORS error — blocked by CORS policy",
        "category": "Networking & Security",
        "cause": "Frontend URL not in backend's CORS allow list.",
        "symptom": "Browser console shows 'Access-Control-Allow-Origin' header missing on API fetch.",
        "fix_command": "ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'https://memegpt.com']",
        "details": "Update CORS whitelist configuration in backend/app/core/config.py.",
    },
    {
        "id": "ERR_QDRANT_CONNECTION",
        "title": "Qdrant connection refused",
        "category": "Database & Vector Store",
        "cause": "Qdrant daemon not running locally, or invalid cloud URL / API key.",
        "symptom": "ConnectionRefusedError or 503 Vector Database Unavailable during search.",
        "fix_command": "docker run -p 6333:6333 qdrant/qdrant  # Or set QDRANT_URL and QDRANT_API_KEY",
        "details": "For local development use port 6333; for cloud use https://xxx.qdrant.io with API key.",
    },
    {
        "id": "ERR_REDIS_CONNECTION",
        "title": "Redis connection refused",
        "category": "Cache & Rate Limiting",
        "cause": "Redis server not running locally or missing Upstash credentials.",
        "symptom": "Redis ConnectionError or fallback to in-memory non-distributed cache.",
        "fix_command": "docker run -p 6379:6379 redis:7-alpine  # Or set UPSTASH_REDIS_URL",
        "details": "Upstash Redis requires rediss:// TLS protocol URI in production.",
    },
    {
        "id": "ISSUE_ZERO_SEARCH_RESULTS",
        "title": "Search returns 0 results",
        "category": "Search & Relevance",
        "cause": "Empty collection, strict threshold, NSFW filter, wrong collection, or unnormalized vectors.",
        "symptom": "Query completes with 200 OK but results list is empty [].",
        "fix_command": "python scripts/index_qdrant.py  # Run seeder and indexer",
        "troubleshooting_steps": [
            {"order": 1, "cause": "Qdrant collection is empty", "fix": "Run python scripts/index_qdrant.py"},
            {"order": 2, "cause": "score_threshold too high", "fix": "Lower score_threshold from 0.45 to 0.35"},
            {"order": 3, "cause": "NSFW filter excluding everything", "fix": "Set nsfw=True temporarily to test query"},
            {"order": 4, "cause": "Wrong collection name", "fix": "Verify collection name 'memes' in Qdrant dashboard"},
            {"order": 5, "cause": "Embeddings not normalized", "fix": "Add normalize_embeddings=True in sentence_transformers"},
        ],
    },
    {
        "id": "ISSUE_SLOW_SEARCH",
        "title": "Search is slow (>3 seconds)",
        "category": "Performance & Latency",
        "cause": "Groq LLM latency, per-request model loading, inactive cache, or free tier cold start.",
        "symptom": "Search queries taking 3.0s to 6.0s P95 latency.",
        "fix_command": "Enable Redis caching and pre-load ML models in FastAPI lifespan startup hook.",
        "troubleshooting_steps": [
            {"order": 1, "cause": "Groq API slow", "fix": "Check Groq status page; fallback to raw query"},
            {"order": 2, "cause": "ML models loading per-request", "fix": "Use lifespan hook to load once at startup"},
            {"order": 3, "cause": "Redis cache not working", "fix": "Verify Redis connection; check cache TTL"},
            {"order": 4, "cause": "Cold start after idle", "fix": "Set minimum 1 instance on Railway / UptimeRobot ping"},
        ],
    },
    {
        "id": "ISSUE_FRONTEND_BUILD_FAILURE",
        "title": "Frontend build fails",
        "category": "Frontend & Build Tools",
        "cause": "Corrupted node_modules, missing TypeScript types, or stale Next.js cache.",
        "symptom": "`next build` or `vite build` throws compilation error or exit code 1.",
        "fix_command": "cd apps/web && rm -rf node_modules .next && npm install && npm run build",
        "details": "Clear build artifacts and perform fresh dependency installation.",
    },
    {
        "id": "ISSUE_RAILWAY_DEPLOY_FAILURE",
        "title": "Railway deploy fails",
        "category": "Deployment & Cloud Infrastructure",
        "cause": "Dockerfile syntax error, missing environment variable, or dependency installation timeout.",
        "symptom": "Railway build logs fail during container creation or health check timeout.",
        "fix_command": "railway logs --service api",
        "troubleshooting_steps": [
            {"order": 1, "cause": "Incorrect Python version", "fix": "Ensure Dockerfile uses python:3.11-slim or 3.12-slim"},
            {"order": 2, "cause": "Missing environment variables", "fix": "Verify all .env keys set in Railway dashboard"},
            {"order": 3, "cause": "Missing dependency", "fix": "Verify requirements.txt contains all imported libraries"},
        ],
    },
]


def get_common_issues_catalog() -> Dict[str, Any]:
    """Return all 8 common troubleshooting issues."""
    return {
        "total_issues": len(COMMON_ISSUES_CATALOG),
        "issues": COMMON_ISSUES_CATALOG,
    }


def get_issue_by_id(issue_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve detailed resolution runbook for a specific issue ID."""
    normalized = issue_id.strip().upper()
    return next((i for i in COMMON_ISSUES_CATALOG if i["id"] == normalized), None)


# ── 3. 5 Debugging Best Practices ──────────────────────────────────────────────

DEBUGGING_BEST_PRACTICES = [
    {
        "id": 1,
        "title": "Check /health first",
        "description": "If health check fails, fix infrastructure and database connections before debugging application logic.",
    },
    {
        "id": 2,
        "title": "Read the error message",
        "description": "FastAPI and Pydantic provide detailed validation error paths and type mismatch details.",
    },
    {
        "id": 3,
        "title": "Check .env file",
        "description": "Over 90% of local and cloud startup failures are caused by missing or misconfigured environment variables.",
    },
    {
        "id": 4,
        "title": "Test one service at a time",
        "description": "Isolate the backend API endpoints first using curl/Swagger, then test the frontend client UI.",
    },
    {
        "id": 5,
        "title": "Check logs",
        "description": "Inspect live execution logs via `railway logs --service api` or `docker logs -f` for unhandled tracebacks.",
    },
]


def get_debugging_best_practices() -> Dict[str, Any]:
    """Return 5 debugging best practices."""
    return {
        "total_practices": len(DEBUGGING_BEST_PRACTICES),
        "practices": DEBUGGING_BEST_PRACTICES,
    }


# ── 4. Automated Symptom Diagnosis Engine ──────────────────────────────────────

def diagnose_system_issue(
    health_status_200: bool = True,
    search_results_count: int = 10,
    qdrant_connected: bool = True,
    redis_connected: bool = True,
    latency_seconds: float = 1.2,
) -> Dict[str, Any]:
    """Analyze system telemetry & symptoms to output targeted remediation runbooks."""
    diagnosed_issues = []

    if not health_status_200:
        diagnosed_issues.append({
            "issue_id": "ERR_BACKEND_DOWN",
            "title": "Backend Service Down",
            "recommendation": "Inspect Railway logs (`railway logs --service api`) and restart container",
        })

    if not qdrant_connected:
        diagnosed_issues.append({
            "issue_id": "ERR_QDRANT_CONNECTION",
            "title": "Qdrant Vector Database Unreachable",
            "recommendation": "Verify QDRANT_URL and QDRANT_API_KEY in .env, or start local container (`docker run -p 6333:6333 qdrant/qdrant`)",
        })

    if not redis_connected:
        diagnosed_issues.append({
            "issue_id": "ERR_REDIS_CONNECTION",
            "title": "Redis Cache Unreachable",
            "recommendation": "Verify UPSTASH_REDIS_URL or start local Redis (`docker run -p 6379:6379 redis:7-alpine`)",
        })

    if health_status_200 and qdrant_connected and search_results_count == 0:
        diagnosed_issues.append({
            "issue_id": "ISSUE_ZERO_SEARCH_RESULTS",
            "title": "Zero Search Results Returned",
            "recommendation": "Lower score_threshold (0.45 -> 0.35) or populate collection via `python scripts/index_qdrant.py`",
        })

    if latency_seconds > 3.0:
        diagnosed_issues.append({
            "issue_id": "ISSUE_SLOW_SEARCH",
            "title": "High Search Latency (>3.0s)",
            "recommendation": "Verify Redis cache hit rate, check Groq API status, and ensure ML models are cached in lifespan startup hook",
        })

    healthy = len(diagnosed_issues) == 0

    return {
        "status": "ALL_SYSTEMS_OPERATIONAL" if healthy else "DIAGNOSTIC_ISSUES_DETECTED",
        "healthy": healthy,
        "detected_issues_count": len(diagnosed_issues),
        "diagnosed_issues": diagnosed_issues,
    }
