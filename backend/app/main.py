import os
import hashlib
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import (
    setup_logging,
    CORS_ORIGINS,
    RATE_LIMIT_PER_MINUTE,
    RATE_LIMIT_WINDOW,
    LOG_LEVEL,
)
from app.database import init_db, get_db
from app.api.v1 import v1_router
from app.models.search import AnalyzeRequest, SearchRequest

from app.core.logging_config import setup_logging, hash_pii

setup_logging(LOG_LEVEL)
logger = logging.getLogger("memegpt.api")


# ── Application Lifespan ───────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown lifecycle management:
    - Initialize database tables
    - Clear and warm query cache
    - Pre-load ML models (MiniLM, DistilRoBERTa) in background thread
    """
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")

    from app.core.cache import query_cache
    query_cache.clear()
    app.state.cache = query_cache

    # Pre-load ML models in a background daemon thread to keep startup fast
    import threading
    def _async_load():
        try:
            from app.services.embedding_service import load_models
            load_models()
            logger.info("ML models pre-loaded successfully.")
        except Exception as e:
            logger.warning(f"ML model loading deferred or skipped ({e}). Using rule-based fallback.")

    threading.Thread(target=_async_load, daemon=True).start()

    logger.info("MemeGPT FastAPI Backend ready.")
    yield
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


# ── Middleware Stack (CORS -> Rate Limit -> Timing & Security Headers) ─────────


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization", "Accept", "Origin", "User-Agent", "X-Requested-With"],
    max_age=3600,
)

from app.core.rate_limit import rate_limiter


@app.middleware("http")
async def security_and_timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    # Rate limiting for API requests (skip internal health checks)
    api_key_header = request.headers.get("X-API-Key", "").strip()
    
    # Determine tier and route rate limit
    tier = "free"
    limit = 60
    window_seconds = 60
    
    is_search = request.url.path.startswith(("/api/v1/search", "/search"))
    is_feedback = request.url.path.startswith(("/api/v1/feedback", "/feedback"))
    
    rate_identifier = getattr(request.client, "host", "127.0.0.1") if request.client else "127.0.0.1"
    
    if api_key_header:
        rate_identifier = f"key:{hashlib.sha256(api_key_header.encode('utf-8')).hexdigest()[:16]}"
        key_clean = api_key_header.lower()
        if "admin" in key_clean or "pro" in key_clean:
            tier = "pro"
            limit = 500 if is_search else 1000
        else:
            tier = "developer"
            limit = 100 if is_search else 300
    else:
        rate_identifier = f"ip:{rate_identifier}"
        tier = "free"
        if is_search:
            limit = 30
        elif is_feedback:
            limit = 120
        else:
            limit = 60

    remaining = limit
    reset_epoch = int(time.time() + 60)

    if request.url.path.startswith(("/api", "/search")) and not request.url.path.endswith("/health"):
        allowed, remaining, retry_after, reset_epoch = rate_limiter.check_with_window(
            rate_identifier, limit, window_seconds=window_seconds
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": f"{limit} requests per minute allowed. Please slow down.",
                    "retry_after": retry_after,
                    "limit": limit,
                    "window": "60s"
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_epoch),
                    "X-RateLimit-Window": "60",
                },
            )

    response = await call_next(request)

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    client_host = request.client.host if request.client else "127.0.0.1"

    logger.info(
        "Request completed",
        extra={
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": elapsed_ms,
                "client_ip_hash": hash_pii(client_host, length=8),
            }
        }
    )

    response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_epoch)
    response.headers["X-RateLimit-Window"] = "60"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.scheme == "https" or os.getenv("APP_ENV") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response



# ── Standardized Exception Handlers ───────────────────────────────────────────

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


# ── Mount Versioned API Routers ───────────────────────────────────────────────


app.include_router(v1_router, prefix="/api/v1")
app.include_router(v1_router, prefix="/api")  # unversioned /api alias


# ── Backward-Compatible Legacy Route Aliases ───────────────────────────────────


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "MemeGPT API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online"
    }


@app.get("/health", tags=["Health & Diagnostics"])
def legacy_health(db: Session = Depends(get_db)):
    from app.api.v1.health import health_check
    return health_check(db)


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
