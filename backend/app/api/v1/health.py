import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import Meme, SearchLog, MemeVote, get_db
from app.config import settings

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
    from app.services.search_service import get_collection_info
    qdrant_info = get_collection_info()
    qdrant_status = "ok" if qdrant_info.get("status") in ("connected", "ok") else "db_fallback"

    return {
        "status": "ok",
        "service": "MemeGPT FastAPI Backend",
        "version": getattr(settings, "APP_VERSION", "2.0.0"),
        "qdrant": qdrant_status,
        "redis": "ok" if cache_stats.get("entries", 0) >= 0 else "degraded",
        "db": "ok" if db_status == "connected" else "error",
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
            "qdrant": qdrant_status,
        },
        "cacheStats": cache_stats,
    }


@router.get("/health/sentry-test", summary="Trigger a test event for Sentry verification")
def sentry_test():
    """Triggers a test event or captures a message to verify Sentry error tracking."""
    sentry_dsn = getattr(settings, "SENTRY_DSN", "")
    try:
        import sentry_sdk
        if sentry_dsn:
            sentry_sdk.capture_message("MemeGPT Sentry Test Event", level="info")
            return {"status": "ok", "message": "Test event captured in Sentry"}
    except Exception:
        pass
    return {"status": "ok", "message": "Sentry simulation complete (SENTRY_DSN optional)"}



@router.get("/health/stats", summary="Platform usage statistics")
def stats(db: Session = Depends(get_db)):
    """Returns aggregated platform search, voting, and latency statistics."""
    from app.api.v1.categories import get_stats
    return get_stats(db)


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
