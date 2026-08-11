import hashlib
import json
import logging
import re
import time
from collections import defaultdict

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import (
    setup_logging,
    CORS_ORIGINS,
    RATE_LIMIT_PER_MINUTE,
    RATE_LIMIT_WINDOW,
    LOG_LEVEL,
)
from app.database import (
    Meme,
    MemeUsage,
    MemeVote,
    FavouriteMeme as FavoriteMeme,
    SearchLog,
    SessionLocal,
    get_db,
    init_db,
    is_valid_input,
    sanitize_input,
)
from app.meme_matcher import export_markdown, export_txt, match_memes

setup_logging(LOG_LEVEL)
logger = logging.getLogger("memegpt.api")

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup hook: initialize DB and load ML models once."""
    init_db()
    logger.info("Database initialized.")

    # Load ML models in background thread so startup is non-blocking
    import threading
    def _async_load():
        try:
            from app.services.embedding_service import load_models
            load_models()
            logger.info("ML models loaded successfully.")
        except Exception as e:
            logger.warning(f"ML model loading skipped ({e}). Using fallback matching.")

    threading.Thread(target=_async_load, daemon=True).start()

    logger.info("MemeGPT FastAPI backend started successfully.")
    yield


app = FastAPI(
    title="MemeGPT API",
    version="2.0.0",
    description="AI-powered conversational meme search engine with real-time recommendations",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve local meme files during development ─────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent.parent / "data" / "images"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Rate limiting ─────────────────────────────────────────────────────────────

_rate: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def security_and_timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    # Rate limiting for /api paths
    remaining = RATE_LIMIT_PER_MINUTE
    if request.url.path.startswith("/api") and request.url.path != "/api/health":
        ip = getattr(request.client, "host", "127.0.0.1") if request.client else "127.0.0.1"
        now = time.time()
        _rate[ip] = [t for t in _rate[ip] if now - t < RATE_LIMIT_WINDOW]
        if len(_rate[ip]) >= RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. {RATE_LIMIT_PER_MINUTE} requests per minute allowed.",
                    "retry_after": RATE_LIMIT_WINDOW,
                },
                headers={"Retry-After": str(RATE_LIMIT_WINDOW), "X-RateLimit-Remaining": "0"},
            )
        _rate[ip].append(now)
        remaining = max(0, RATE_LIMIT_PER_MINUTE - len(_rate[ip]))

    response = await call_next(request)

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_PER_MINUTE)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ── Error Handlers ────────────────────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code_str = "http_error"
    if exc.status_code == 400:
        code_str = "invalid_request"
    elif exc.status_code == 404:
        code_str = "not_found"
    elif exc.status_code == 422:
        code_str = "validation_error"
    elif exc.status_code == 429:
        code_str = "rate_limit_exceeded"
    elif exc.status_code == 503:
        code_str = "service_unavailable"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": code_str,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled backend exception on {request.method} {request.url.path}: {exc}",
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


# ── Request / Response Models ─────────────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    format_preference: str | None = None
    formatPreference: str | None = None


class CreateMemeRequest(BaseModel):
    name: str
    category: str
    dialogue: str
    explanation: str
    keywords: list[str]
    videoRef: str | None = None
    gifRef: str | None = None


class VoteRequest(BaseModel):
    memeId: str
    vote: int
    sessionId: str


class FavoriteRequest(BaseModel):
    memeId: str
    sessionId: str


class ExportRequest(BaseModel):
    query: str
    format: str
    result: dict


# ── Helper Functions ──────────────────────────────────────────────────────────


def _memes_from_db(db: Session) -> list[dict]:
    memes = db.query(Meme).all()
    return [
        {
            **m.to_dict(),
            "videoRef": m.video_ref,
            "gifRef": m.gif_ref,
        }
        for m in memes
    ]


def _log_search_background(primary_meme_id: str, query: str, match_count: int, confidence: float, latency_ms: float):
    """Background task for async search analytics logging with privacy hash."""
    db = SessionLocal()
    try:
        query_hash = hashlib.md5(query.encode("utf-8")).hexdigest()
        logger.info(f"Logging search (hash: {query_hash[:8]}, latency: {latency_ms}ms)")
        meme = db.query(Meme).filter(Meme.id == primary_meme_id).first()
        if meme:
            meme.usage_count += 1
            db.add(MemeUsage(meme_id=meme.id, query=query, confidence=confidence, session_id="api-session"))
        db.add(SearchLog(query=query, match_count=match_count, latency_ms=latency_ms, session_id="api-session"))
        db.commit()
    except Exception as e:
        logger.error(f"Error in background search log task: {e}")
        db.rollback()
    finally:
        db.close()


def _record_feedback_background(meme_id: str, signal: str, fmt: str = "image"):
    """Background task for recording feedback signals."""
    db = SessionLocal()
    try:
        meme = db.query(Meme).filter(Meme.id == meme_id).first()
        if meme:
            if signal == "upvote":
                meme.upvotes += 1
            elif signal == "downvote":
                meme.downvotes += 1
            elif signal == "copy":
                meme.viral_score += 0.5
                meme.usage_count += 1
            elif signal == "download":
                meme.viral_score += 1.0
                meme.usage_count += 1
            db.commit()
    except Exception as e:
        logger.error(f"Error in background feedback task: {e}")
        db.rollback()
    finally:
        db.close()


# ── Root ──────────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    return {"message": "MemeGPT API v2.0.0", "docs": "/docs", "status": "online"}


# ── Health & Stats ────────────────────────────────────────────────────────────


@app.get("/api/health")
@app.get("/api/v1/health")
def health(db: Session = Depends(get_db)):
    from app.core.cache import query_cache
    from app.services.embedding_service import is_loaded

    return {
        "status": "ok",
        "service": "MemeGPT FastAPI Backend",
        "version": "2.0.0",
        "memeCount": db.query(Meme).count(),
        "modelsLoaded": is_loaded(),
        "cacheStats": query_cache.stats(),
    }


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
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
        "avgLatencyMs": round(avg_latency, 1),
    }


@app.get("/api/categories")
def categories():
    return [
        "coding", "startup", "relationship", "college", "office", "funny",
        "motivation", "unrealistic_goals", "ai", "business", "exam", "failure",
        "success", "gaming", "bollywood", "youtube", "money", "sleep"
    ]


# ── Core Search — AI-Powered Recommendation Pipeline ─────────────────────────


@app.post("/api/analyze")
@app.post("/api/v1/search")
async def analyze(body: AnalyzeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """AI-powered meme search. Uses the full recommendation pipeline:
    Cache → LLM Intent → Emotion → Embedding → Vector Search → Rerank
    """
    query = sanitize_input(body.query)
    if not is_valid_input(query):
        raise HTTPException(400, "Query must be 3-2000 characters")

    fmt_pref = body.format_preference or body.formatPreference or "gif"

    # Get all memes from DB for fallback augmentation
    memes = _memes_from_db(db)
    if not memes:
        raise HTTPException(503, "Database empty. Run: python backend/seed.py")

    # Use AI recommendation pipeline
    try:
        from app.services.recommendation_service import recommend
        result = await recommend(
            user_text=query,
            format_pref=fmt_pref,
            memes_from_db=memes,
        )
    except Exception as e:
        logger.error(f"AI pipeline failed, falling back to rule engine: {e}")
        # Fallback to the original rule-engine matcher
        result = match_memes(query, memes, format_preference=fmt_pref)
        result["cached"] = False

    # Dispatch non-blocking background analytics task
    primary_id = result.get("primary", {}).get("id") if result.get("primary") else None
    if primary_id:
        background_tasks.add_task(
            _log_search_background,
            primary_id,
            query,
            len(result.get("topFive", [])),
            result.get("primary", {}).get("confidence", 0.8),
            result.get("latencyMs", 0),
        )

    return result


# ── Memes CRUD ────────────────────────────────────────────────────────────────


@app.get("/api/memes")
@app.get("/api/v1/memes")
def list_memes(q: str = "", category: str = "", limit: int = 50, page: int = 1, db: Session = Depends(get_db)):
    limit = min(max(limit, 1), 100)
    query = db.query(Meme)
    if category:
        query = query.filter(Meme.category == category)
    memes = query.order_by(Meme.usage_count.desc()).all()

    if q:
        search = sanitize_input(q).lower()
        filtered = []
        for m in memes:
            kws = m.keywords_list()
            if (
                search in m.name.lower()
                or search in m.dialogue.lower()
                or search in m.category.lower()
                or any(search in k.lower() for k in kws)
            ):
                filtered.append(m)
        memes = filtered

    offset = (page - 1) * limit
    paged = memes[offset : offset + limit]

    return {
        "items": [m.to_dict() for m in paged],
        "total": len(memes),
        "page": page,
        "pageSize": limit
    }


@app.get("/api/memes/{meme_id}")
@app.get("/api/v1/memes/{slug_or_id}")
def get_meme_detail(meme_id: str = None, slug_or_id: str = None, db: Session = Depends(get_db)):
    lookup = slug_or_id or meme_id
    meme = db.query(Meme).filter(Meme.id == lookup).first()

    # Try slug lookup
    if not meme:
        meme = db.query(Meme).filter(Meme.slug == lookup).first()

    # Try name-based slug match
    if not meme:
        memes = db.query(Meme).all()
        for m in memes:
            slug_val = re.sub(r"[^\w\s-]", "", m.name.lower()).strip().replace(" ", "-")
            if slug_val == lookup:
                meme = m
                break

    if not meme:
        raise HTTPException(404, "Meme not found")
    return meme.to_dict()


@app.get("/api/v1/memes/{slug_or_id}/download")
def download_meme_v1(slug_or_id: str, format: str = "gif", background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
    meme = db.query(Meme).filter(Meme.id == slug_or_id).first()
    if not meme:
        meme = db.query(Meme).filter(Meme.slug == slug_or_id).first()
    if not meme:
        memes = db.query(Meme).all()
        for m in memes:
            slug_val = re.sub(r"[^\w\s-]", "", m.name.lower()).strip().replace(" ", "-")
            if slug_val == slug_or_id:
                meme = m
                break
    if not meme:
        raise HTTPException(404, "Meme not found")

    fmt = format.lower()
    target_url = None
    if fmt == "gif":
        target_url = meme.gif_ref
    elif fmt in ("video", "mp4"):
        target_url = meme.video_ref
    elif fmt in ("image", "png", "webp"):
        target_url = meme.image_ref

    if not target_url:
        target_url = meme.image_ref or meme.gif_ref or meme.video_ref or f"https://cdn.memegpt.com/images/{meme.id}.png"

    if background_tasks:
        background_tasks.add_task(_record_feedback_background, meme.id, "download", fmt)

    return RedirectResponse(url=target_url, status_code=301)


# ── Trending ──────────────────────────────────────────────────────────────────


@app.get("/api/trending")
@app.get("/api/v1/trending")
def trending(db: Session = Depends(get_db)):
    memes = db.query(Meme).order_by(Meme.usage_count.desc(), Meme.upvotes.desc()).limit(12).all()
    return [m.to_dict() for m in memes]


# ── Favorites ─────────────────────────────────────────────────────────────────


@app.get("/api/favorites")
def list_favorites(sessionId: str, db: Session = Depends(get_db)):
    favs = db.query(FavoriteMeme).filter(FavoriteMeme.session_id == sessionId).all()
    meme_ids = [f.meme_id for f in favs]
    memes = db.query(Meme).filter(Meme.id.in_(meme_ids)).all() if meme_ids else []
    return [m.to_dict() for m in memes]


@app.post("/api/favorites/toggle")
def toggle_favorite(body: FavoriteRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(FavoriteMeme)
        .filter(FavoriteMeme.meme_id == body.memeId, FavoriteMeme.session_id == body.sessionId)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"isFavorite": False}
    else:
        db.add(FavoriteMeme(meme_id=body.memeId, session_id=body.sessionId))
        db.commit()
        return {"isFavorite": True}


# ── Voting ────────────────────────────────────────────────────────────────────


@app.post("/api/vote")
def vote(body: VoteRequest, db: Session = Depends(get_db)):
    if body.vote not in (1, -1):
        raise HTTPException(400, "vote must be 1 or -1")

    existing = (
        db.query(MemeVote)
        .filter(MemeVote.meme_id == body.memeId, MemeVote.session_id == body.sessionId)
        .first()
    )
    meme = db.query(Meme).filter(Meme.id == body.memeId).first()
    if not meme:
        raise HTTPException(404, "Meme not found")

    if existing:
        if existing.vote != body.vote:
            if existing.vote == 1:
                meme.upvotes -= 1
                meme.downvotes += 1
            else:
                meme.downvotes -= 1
                meme.upvotes += 1
            existing.vote = body.vote
    else:
        db.add(MemeVote(meme_id=body.memeId, vote=body.vote, session_id=body.sessionId))
        if body.vote == 1:
            meme.upvotes += 1
        else:
            meme.downvotes += 1

    db.commit()
    return {"success": True}


# ── Feedback (V1 API) ────────────────────────────────────────────────────────


class FeedbackRequest(BaseModel):
    meme_id: str
    signal: str  # copy, download, upvote, downvote
    format: str | None = "image"
    session_id: str | None = "anonymous"


@app.post("/api/v1/feedback")
def feedback_v1(body: FeedbackRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(404, "Meme not found")

    background_tasks.add_task(_record_feedback_background, body.meme_id, body.signal, body.format or "image")
    return {"status": "recorded", "meme_id": body.meme_id, "signal": body.signal}


# ── Export ────────────────────────────────────────────────────────────────────


@app.post("/api/export")
def export(body: ExportRequest):
    fmt = body.format
    if fmt == "txt":
        content = export_txt(body.result, body.query)
        filename = "memegpt-result.txt"
        content_type = "text/plain"
    elif fmt == "markdown":
        content = export_markdown(body.result, body.query)
        filename = "memegpt-result.md"
        content_type = "text/markdown"
    elif fmt == "json":
        content = json.dumps({"query": body.query, **body.result}, indent=2)
        filename = "memegpt-result.json"
        content_type = "application/json"
    else:
        raise HTTPException(400, "format must be txt, json, or markdown")

    return {"content": content, "contentType": content_type, "filename": filename}


# ── Admin ─────────────────────────────────────────────────────────────────────


@app.post("/api/admin/memes")
def create_meme(body: CreateMemeRequest, db: Session = Depends(get_db)):
    meme = Meme(
        name=sanitize_input(body.name),
        category=body.category,
        dialogue=sanitize_input(body.dialogue),
        explanation=sanitize_input(body.explanation),
        keywords=json.dumps([sanitize_input(k) for k in body.keywords]),
        video_ref=body.videoRef,
        gif_ref=body.gifRef,
    )
    db.add(meme)
    db.commit()
    db.refresh(meme)
    return meme.to_dict()


@app.delete("/api/admin/memes/{meme_id}")
def delete_meme(meme_id: str, db: Session = Depends(get_db)):
    meme = db.query(Meme).filter(Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(404, "Meme not found")
    db.delete(meme)
    db.commit()
    return {"success": True}
