import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import Meme, SearchLog, MemeVote, get_db

router = APIRouter(tags=["Health & Diagnostics"])
START_TIME = time.time()


@router.get("/health", summary="Health check endpoint")
def health_check(request: Request = None, db: Session = Depends(get_db)):
    """Returns system status, uptime, model availability, and service diagnostics."""
    from app.core.cache import query_cache
    from app.services.embedding_service import is_loaded

    uptime_sec = int(time.time() - START_TIME)
    models_loaded = is_loaded()

    # Test database connectivity
    db_status = "connected"
    meme_count = 0
    try:
        meme_count = db.query(Meme).count()
    except Exception:
        db_status = "error"

    cache_stats = query_cache.stats()

    return {
        "status": "ok",
        "service": "MemeGPT FastAPI Backend",
        "version": "2.0.0",
        "uptime_seconds": uptime_sec,
        "uptimeSeconds": uptime_sec,
        "memeCount": meme_count,
        "modelsLoaded": models_loaded,
        "models": {
            "text_model": "loaded" if models_loaded else "deferred",
            "emotion": "loaded" if models_loaded else "deferred",
        },
        "services": {
            "database": db_status,
            "cache": "connected" if cache_stats.get("entries", 0) >= 0 else "degraded",
        },
        "cacheStats": cache_stats,
    }


@router.get("/stats", summary="Platform usage statistics")
def stats(db: Session = Depends(get_db)):
    """Returns aggregated platform search, voting, and latency statistics."""
    total_memes = db.query(Meme).count()
    total_searches = db.query(SearchLog).count()
    total_votes = db.query(MemeVote).count()
    total_usage = db.query(func.sum(Meme.usage_count)).scalar() or 0
    avg_latency = db.query(func.avg(SearchLog.latency_ms)).scalar() or 0

    return {
        "totalMemes": total_memes,
        "totalSearches": total_searches,
        "totalVotes": total_votes,
        "totalUsage": total_usage,
        "avgLatencyMs": round(float(avg_latency), 1),
    }


@router.get("/categories", summary="List of available meme categories")
def categories():
    """Returns all supported meme category tags."""
    return [
        "coding", "startup", "relationship", "college", "office", "funny",
        "motivation", "unrealistic_goals", "ai", "business", "exam", "failure",
        "success", "gaming", "bollywood", "youtube", "money", "sleep"
    ]


@router.get("/database/overview", summary="Polyglot persistence architecture overview")
def database_overview():
    """Returns architecture overview of the 4 specialized data stores from 06_Database/Database_Overview.md."""
    from app.services.database_service import get_polyglot_database_overview
    return get_polyglot_database_overview()


@router.get("/database/ownership", summary="Data ownership matrix")
def database_ownership():
    """Returns entity-to-store mapping from 06_Database/Database_Overview.md."""
    from app.services.database_service import get_data_ownership_matrix
    return get_data_ownership_matrix()


@router.get("/database/access-patterns", summary="Access patterns catalog")
def database_access_patterns():
    """Returns standard access patterns from 06_Database/Database_Overview.md."""
    from app.services.database_service import get_access_patterns
    return get_access_patterns()


@router.get("/database/limits", summary="Free tier headroom limits and alerts")
def database_limits():
    """Returns free-tier headroom limits and active threshold alerts."""
    from app.services.database_service import get_free_tier_limits, check_free_tier_alerts
    return {
        "limits": get_free_tier_limits(),
        "alerts": check_free_tier_alerts(threshold_pct=80.0),
    }
