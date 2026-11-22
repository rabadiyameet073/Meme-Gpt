import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.database import Meme, SearchLog, MemeVote, get_db
from app.config import settings

router = APIRouter(tags=["Health & Diagnostics"])
START_TIME = time.time()


def _require_non_prod_or_admin(request: Request = None):
    """Enforce that debug endpoints are only available in non-production or to administrators."""
    app_env = str(getattr(settings, "APP_ENV", "development") or "development").lower()
    if app_env == "production":
        if request is None:
            raise HTTPException(status_code=403, detail="Debug endpoints are restricted in production")
        
        api_key = request.headers.get("x-api-key", "").strip()
        auth_header = request.headers.get("authorization", "").strip()
        if not api_key and auth_header.startswith("Bearer "):
            api_key = auth_header[7:].strip()

        from app.core.auth import get_cached_api_key_tier
        _, is_admin = get_cached_api_key_tier(api_key)

        if not is_admin:
            token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else request.cookies.get("access_token", "")
            if token:
                try:
                    from app.services.jwt_service import decode_token
                    payload = decode_token(token)
                    if payload and payload.get("role") in ("admin", "internal"):
                        is_admin = True
                except Exception:
                    pass

        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Debug endpoints are only available in non-production environments or to administrators."
            )


@router.get("/health", summary="Health check endpoint")
def health_check(request: Request = None, response: Response = None, db: Session = Depends(get_db)):
    """Returns system status, uptime, model availability, and service diagnostics."""
    from app.core.cache import query_cache, get_redis_client
    from app.services.embedding_service import is_loaded
    from app.services.search_service import get_collection_info

    uptime_sec = int(time.time() - START_TIME)
    models_loaded = is_loaded()

    # 1. Database connectivity check: real SELECT 1 and record count
    db_status = "connected"
    meme_count = 0
    try:
        db.execute(text("SELECT 1"))
        meme_count = db.query(Meme).count()
    except Exception:
        db_status = "error"

    # 2. Redis connectivity check: real ping or in-memory fallback
    client = get_redis_client()
    if client is not None:
        try:
            ping_ok = client.ping()
            redis_status = "connected" if ping_ok else "degraded"
        except Exception:
            redis_status = "degraded"
    else:
        # Check if Redis was explicitly required but failed to connect
        if (getattr(settings, "REDIS_URL", "") or getattr(settings, "UPSTASH_REDIS_URL", "") or getattr(settings, "UPSTASH_REDIS_REST_URL", "")):
            redis_status = "degraded"
        else:
            redis_status = "connected"

    # 3. Qdrant connectivity check: collection info
    qdrant_info = get_collection_info()
    qdrant_status = "connected" if (qdrant_info.get("status") in ("connected", "ok", "green", "yellow") and qdrant_info.get("is_connected", True)) else ("error" if getattr(settings, "QDRANT_URL", "") else "db_fallback")

    # 4. Overall status determination
    if db_status == "error":
        overall_status = "degraded"
        if response is not None:
            response.status_code = 503
    elif redis_status in ("degraded", "error") or qdrant_status == "error" or not models_loaded:
        overall_status = "degraded"
    else:
        overall_status = "ok"

    cache_stats = query_cache.stats()

    return {
        "status": overall_status,
        "service": "MemeGPT FastAPI Backend",
        "version": getattr(settings, "APP_VERSION", "2.0.0"),
        "qdrant": qdrant_status,
        "redis": redis_status,
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
            "redis": redis_status,
            "cache": redis_status,
            "qdrant": qdrant_status,
        },
        "cacheStats": cache_stats,
    }


@router.get("/health/sentry-test", summary="Trigger a test event for Sentry verification")
def sentry_test(request: Request = None):
    """Triggers a test event or captures a message to verify Sentry error tracking."""
    _require_non_prod_or_admin(request)
    sentry_dsn = getattr(settings, "SENTRY_DSN", "")
    try:
        import sentry_sdk
        if sentry_dsn:
            sentry_sdk.capture_message("MemeGPT Sentry Test Event", level="info")
            return {"status": "ok", "message": "Test event captured in Sentry"}
    except Exception:
        pass
    return {"status": "ok", "message": "Sentry simulation complete (SENTRY_DSN optional)"}


@router.get("/health/sentry-error", summary="Trigger an intentional error for Sentry verification")
def sentry_error(request: Request = None):
    """Triggers an intentional RuntimeError to verify Sentry unhandled exception capturing."""
    _require_non_prod_or_admin(request)
    from app.core.monitoring import capture_exception
    err = RuntimeError("MemeGPT Test Exception for Sentry Verification")
    capture_exception(err)
    raise HTTPException(status_code=500, detail="Intentional test error for Sentry verification")



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
