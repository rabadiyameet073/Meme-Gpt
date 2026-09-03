"""
MemeGPT — Main FastAPI Application.

Complete upgraded implementation:
- Real DB-driven tier enforcement & Redis rate limiting
- Sentry error monitoring
- Qdrant collection initialization
- APScheduler 30-day retention cleanup
- Security headers & CSP
- Dynamic SEO sitemap, robots.txt, OG meta endpoints
- Full legacy frontend endpoint compatibility
"""

import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import (
    settings,
    setup_logging,
    CORS_ORIGINS,
    LOG_LEVEL,
)
from app.database import init_db, get_db, SessionLocal
from app.api.v1 import v1_router
from app.api.v1.sitemap import router as sitemap_router
from app.api.v1.categories import get_categories, get_stats
from app.models.search import AnalyzeRequest, SearchRequest
from app.core.logging_config import hash_pii

setup_logging(LOG_LEVEL)
logger = logging.getLogger("memegpt.api")

# ── Optional Sentry SDK ────────────────────────────────────────────────────────
sentry_dsn = getattr(settings, "SENTRY_DSN", "")
if sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=0.1,
            environment=getattr(settings, "APP_ENV", "development"),
            release=getattr(settings, "APP_VERSION", "1.0.0"),
        )
        logger.info("✅ Sentry initialized")
    except Exception as e:
        logger.warning(f"Sentry init skipped: {e}")


# ── Application Lifespan ───────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown lifecycle management."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")

    from app.core.cache import query_cache
    query_cache.clear()
    app.state.cache = query_cache

    # 1. Initialize Qdrant collection
    try:
        from app.services.search_service import create_qdrant_collection, get_collection_info
        create_qdrant_collection(recreate=False)
        info = get_collection_info()
        logger.info(f"Qdrant collection status: {info}")
    except Exception as e:
        logger.warning(f"Qdrant startup init deferred: {e}")

    # 2. Pre-load ML models in a background daemon thread
    import threading
    def _async_load():
        try:
            from app.services.embedding_service import load_models
            load_models()
            logger.info("ML models pre-loaded successfully.")
        except Exception as e:
            logger.warning(f"ML model loading deferred ({e}).")

    threading.Thread(target=_async_load, daemon=True).start()

    # 3. Schedule 30-day retention cleanup
    scheduler = None
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from app.jobs.retention import run_retention_cleanup

        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            run_retention_cleanup,
            "cron",
            hour=3,
            minute=0,
            id="retention_cleanup",
        )
        scheduler.start()
        logger.info("✅ Retention job scheduled (daily at 03:00 UTC)")
    except Exception as e:
        logger.debug(f"APScheduler not started: {e}")

    logger.info("MemeGPT FastAPI Backend ready.")
    yield

    if scheduler:
        try:
            scheduler.shutdown()
        except Exception:
            pass
    logger.info("MemeGPT FastAPI Backend shutting down.")


# ── App Factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="MemeGPT API",
    description="AI-powered conversational meme recommendation engine with multi-format support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ── Middleware Stack ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization", "Accept", "Origin", "User-Agent", "X-Requested-With"],
    max_age=3600,
)


@app.middleware("http")
async def security_and_timing_middleware(request: Request, call_next):
    # Production HTTPS enforcement
    is_prod = getattr(settings, "APP_ENV", "") == "production"
    if is_prod and request.url.scheme == "http" and "localhost" not in (request.url.hostname or ""):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=str(request.url).replace("http://", "https://", 1),
            status_code=301,
        )

    start_time = time.perf_counter()

    # Endpoints exempt from rate limiting
    exempt_paths = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico", "/api/health", "/robots.txt", "/sitemap.xml"}
    path = request.url.path
    is_exempt = any(path == p or path.startswith("/docs") or path.startswith("/static") for p in exempt_paths)

    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )
    api_key_header = (
        request.headers.get("x-api-key", "").strip()
        or request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    )

    tier = "anonymous"
    if api_key_header:
        try:
            from app.core.auth import lookup_api_key_tier
            db = SessionLocal()
            try:
                tier, _ = lookup_api_key_tier(api_key_header, db)
            finally:
                db.close()
        except Exception:
            tier = "anonymous"

    from app.core.auth import get_rate_limit_for_tier
    rate_limit = get_rate_limit_for_tier(tier)

    remaining = rate_limit
    window_seconds = 60
    reset_epoch = int(time.time() + window_seconds)
    if not is_exempt:
        from app.core.rate_limit import rate_limiter
        identifier = f"ip:{client_ip}" if not api_key_header else f"key:{api_key_header}"
        allowed, remaining, retry_after, reset_epoch = rate_limiter.check_with_window(identifier, rate_limit, window_seconds=window_seconds)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. {rate_limit} requests per minute allowed. Please slow down.",
                    "retry_after": retry_after or 60,
                    "limit": rate_limit,
                    "window": f"{window_seconds}s",
                    "tier": tier,
                },
                headers={
                    "Retry-After": str(retry_after or 60),
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_epoch),
                    "X-RateLimit-Window": str(window_seconds),
                    "X-RateLimit-Tier": tier,
                },
            )

    response = await call_next(request)

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    # Response headers
    response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
    response.headers["X-RateLimit-Limit"] = str(rate_limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_epoch)
    response.headers["X-RateLimit-Window"] = str(window_seconds)
    response.headers["X-RateLimit-Tier"] = tier

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"

    cdn_base = getattr(settings, "CDN_BASE_URL", "")
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"img-src 'self' {cdn_base} https://i.imgflip.com https://media.giphy.com https://*.giphy.com https://*.tenor.com data: blob:; "
        f"script-src 'self' 'unsafe-inline'; "
        f"style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        f"font-src 'self' fonts.gstatic.com data:;"
    )

    if request.url.scheme == "https" or is_prod:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ── Exception Handlers ────────────────────────────────────────────────────────
from fastapi.exceptions import RequestValidationError
from app.core.errors import MemeGPTException


@app.exception_handler(MemeGPTException)
async def memegpt_exception_handler(request: Request, exc: MemeGPTException):
    payload = {
        "success": False,
        "error": exc.error_code,
        "message": exc.message,
    }
    if exc.details is not None:
        payload["details"] = exc.details
    if exc.retry_after is not None:
        payload["retry_after"] = exc.retry_after

    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for err in exc.errors():
        field_path = ".".join([str(loc) for loc in err.get("loc", []) if loc not in ("body", "query", "path")])
        formatted_errors.append({
            "field": field_path or "root",
            "message": err.get("msg", "Validation error"),
            "type": err.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "validation_error",
            "message": "Request validation failed",
            "details": formatted_errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code_map = {
        400: "invalid_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        422: "validation_error",
        429: "rate_limit_exceeded",
        500: "internal_error",
        502: "upstream_error",
        503: "service_unavailable",
        504: "gateway_timeout",
    }
    code_str = getattr(exc, "error_code", None) or code_map.get(exc.status_code, "http_error")
    msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    payload = {
        "success": False,
        "error": code_str,
        "message": msg,
    }
    if hasattr(exc, "details") and exc.details is not None:
        payload["details"] = exc.details
    if hasattr(exc, "retry_after") and exc.retry_after is not None:
        payload["retry_after"] = exc.retry_after

    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internal_error",
            "message": "Something went wrong on the server. Please try again.",
        },
    )


# ── Static Media Mounting ─────────────────────────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent.parent / "data" / "images"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Mount Versioned API & SEO Routers ─────────────────────────────────────────
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v1_router, prefix="/api")
app.include_router(sitemap_router)


# ── Legacy & Frontend Convenience Route Mounts ────────────────────────────────
@app.get("/api/categories", tags=["Categories & Stats"])
def legacy_categories(db: Session = Depends(get_db)):
    return get_categories(db)


@app.get("/api/stats", tags=["Categories & Stats"])
def legacy_stats(db: Session = Depends(get_db)):
    return get_stats(db)


@app.get("/api/favorites", tags=["Favorites & Collections"])
def legacy_favorites(sessionId: str = Query(default=""), db: Session = Depends(get_db)):
    from app.api.v1.collections import get_favorites
    return get_favorites(sessionId=sessionId, db=db)


@app.post("/api/favorites/toggle", tags=["Favorites & Collections"])
def legacy_toggle(body: dict):
    from app.api.v1.collections import toggle_favorite, ToggleFavoriteRequest
    return toggle_favorite(ToggleFavoriteRequest(**body))


@app.get("/landing", include_in_schema=False)
def get_landing_page():
    landing_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "landing.html"
    if landing_path.exists():
        return FileResponse(str(landing_path), media_type="text/html")
    return JSONResponse({"message": "Landing page available at /landing.html"})


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "MemeGPT API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online",
        "landing": "/landing",
    }


@app.get("/health", tags=["Health & Diagnostics"])
def legacy_health(db: Session = Depends(get_db)):
    from app.api.v1.health import health_check
    return health_check(db=db)


@app.post("/search", tags=["Search & Recommendations"])
async def legacy_search(
    body: SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    from app.api.v1.search import search_memes_endpoint
    return await search_memes_endpoint(body, background_tasks, db)


@app.post("/api/analyze", tags=["Search & Recommendations"])
async def legacy_analyze(
    body: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    from app.api.v1.search import search_memes_endpoint
    req = SearchRequest(
        query=body.query,
        format_preference=body.format_preference or body.formatPreference or "gif",
        limit=5
    )
    return await search_memes_endpoint(req, background_tasks, db)
