"""
MemeGPT FastAPI Application Entry Point.
Models loaded once at startup via lifespan hook (not per-request).
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.rate_limit import rate_limiter
from app.api.v1 import search, memes, trending, feedback, health

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("memegpt.main")


# ── Lifespan: load ML models once at startup ──────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MemeGPT API starting up — loading ML models...")
    from app.services.embedding import embedding_service
    from app.services.search_service import search_service
    embedding_service.load_models()   # MiniLM + DistilRoBERTa
    # Trigger Qdrant connection check / local index load
    _ = search_service._get_qdrant()
    logger.info("MemeGPT API ready.")
    yield
    logger.info("MemeGPT API shutting down.")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="MemeGPT API",
    description="AI-powered meme recommendation engine",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve local meme files during development ─────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "public"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Rate limiting + timing middleware ─────────────────────────────────────────
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    start = time.perf_counter()

    # Apply rate limiting to all /api/* paths except /health
    if request.url.path.startswith("/api/v1/") and "health" not in request.url.path:
        client_ip = getattr(request.client, "host", "127.0.0.1")
        if not rate_limiter.is_allowed(client_ip):
            retry = rate_limiter.reset_time(client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": f"{settings.RATE_LIMIT_PER_MINUTE} requests per minute allowed. "
                               f"Retry after {retry} seconds.",
                    "retry_after": retry,
                },
                headers={"Retry-After": str(retry), "X-RateLimit-Remaining": "0"},
            )

    response = await call_next(request)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# ── Error handlers ────────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled {type(exc).__name__} on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "internal_error", "message": "Something went wrong."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(memes.router, prefix="/api/v1", tags=["Memes"])
app.include_router(trending.router, prefix="/api/v1", tags=["Trending"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])


@app.get("/")
async def root():
    return {"message": "MemeGPT API v2.0.0", "docs": "/docs", "status": "online"}


# ── /api/memes — list with pagination + category filter + search ─────────────
@app.get("/api/memes")
async def list_memes(
    category: str = "",
    q: str = "",
    page: int = 1,
    limit: int = 50,
):
    """List memes with optional category filter, text search, and pagination."""
    from app.services.search_service import search_service
    all_memes = list(search_service._local_index)

    # Filter by category
    if category:
        cat_lower = category.lower()
        all_memes = [
            m for m in all_memes
            if cat_lower in [c.lower() for c in m.get("categories", [])]
            or cat_lower == m.get("category", "").lower()
        ]

    # Text search
    if q:
        q_lower = q.lower()
        all_memes = [
            m for m in all_memes
            if q_lower in m.get("name", "").lower()
            or q_lower in " ".join(m.get("keywords", [])).lower()
        ]

    total = len(all_memes)
    start = (page - 1) * limit
    items = all_memes[start : start + limit]

    def _to_item(m: dict) -> dict:
        slug = m.get("slug") or m.get("name", "meme").lower().replace(" ", "-")
        return {
            "id": m.get("id", slug),
            "name": m.get("name", slug),
            "slug": slug,
            "category": m.get("category", "general"),
            "dialogue": m.get("dialogue", m.get("caption", "")),
            "explanation": m.get("explanation", ""),
            "keywords": m.get("keywords", []),
            "imageRef": m.get("image_url"),
            "videoRef": m.get("mp4_url"),
            "gifRef": m.get("gif_url"),
            "viralScore": m.get("popularity_score", 0.0),
            "usageCount": m.get("usage_count", m.get("usageCount", 0)),
            "upvotes": m.get("upvotes", 0),
            "downvotes": m.get("downvotes", 0),
            "createdAt": m.get("created_at"),
        }

    return {"items": [_to_item(m) for m in items], "total": total, "page": page, "pageSize": limit}


# ── /api/categories ──────────────────────────────────────────────────────────
@app.get("/api/categories")
async def get_categories():
    """Return all distinct categories from the meme index."""
    from app.services.search_service import search_service
    cats: set[str] = set()
    for m in search_service._local_index:
        if "categories" in m:
            cats.update(m["categories"])
        elif "category" in m:
            cats.add(m["category"])
    return sorted(cats) or ["general", "coding", "work", "gaming", "relationship", "funny"]


# ── /api/stats ───────────────────────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats():
    """Return aggregate stats for the meme index."""
    from app.services.search_service import search_service
    from app.core.cache import cache_service
    return {
        "total_memes": len(search_service._local_index),
        "cache_connected": cache_service.is_connected,
        "vector_db_connected": search_service._qdrant is not None,
        "version": "2.0.0",
    }

