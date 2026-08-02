# MemeGPT — Controllers (Route Handlers)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete catalog of all FastAPI route handlers — endpoint definitions, request validation, response models, and implementation patterns.

---

## Route Registration

```python
# main.py
from fastapi import FastAPI
from app.api.v1 import search, memes, trending, feedback, health

app = FastAPI(title="MemeGPT API", version="1.0.0", lifespan=lifespan)

# Register route modules
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(memes.router, prefix="/api/v1", tags=["Memes"])
app.include_router(trending.router, prefix="/api/v1", tags=["Trending"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])
app.include_router(health.router, tags=["Health"])
```

---

## Route Catalog

| Method | Path | Handler | Service | Auth |
|---|---|---|---|---|
| POST | `/api/v1/search` | `search_memes()` | recommendation.py | None |
| GET | `/api/v1/memes/{slug}` | `get_meme()` | database | None |
| GET | `/api/v1/memes/{slug}/download` | `download_meme()` | cdn_service.py | None |
| GET | `/api/v1/trending` | `get_trending()` | cache.py | None |
| POST | `/api/v1/feedback` | `record_feedback()` | database | None |
| GET | `/health` | `health_check()` | all services | None |

---

## Search Controller

```python
# api/v1/search.py
from fastapi import APIRouter, BackgroundTasks, Request
from app.models.search import SearchRequest, SearchResponse
from app.services.recommendation import recommend_memes

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_memes(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    raw_request: Request
):
    """
    Core search endpoint. Thin handler — delegates everything to service layer.
    """
    import time, uuid
    start = time.time()
    query_id = f"q_{uuid.uuid4().hex[:12]}"
    
    # Delegate to service layer
    results, intent, cached = await recommend_memes(
        user_text=request.query,
        format_pref=request.format_preference,
        nsfw=request.nsfw,
    )
    
    elapsed_ms = int((time.time() - start) * 1000)
    
    # Log search (non-blocking)
    background_tasks.add_task(
        log_search,
        query_id=query_id,
        query_hash=hashlib.md5(request.query.encode()).hexdigest(),
        latency_ms=elapsed_ms,
        result_count=len(results),
        cached=cached,
    )
    
    return SearchResponse(
        success=True,
        query_id=query_id,
        results=results[:request.limit],
        intent_parsed=intent,
        response_time_ms=elapsed_ms,
        cached=cached,
    )
```

---

## Meme Detail Controller

```python
# api/v1/memes.py
@router.get("/memes/{slug}")
async def get_meme(slug: str, background_tasks: BackgroundTasks):
    meme = await db.memes.find_unique(where={"slug": slug})
    if not meme:
        raise HTTPException(404, "Meme not found")
    
    # Track view (non-blocking)
    background_tasks.add_task(increment_view_count, meme.id)
    return meme

@router.get("/memes/{slug}/download")
async def download_meme(
    slug: str,
    format: str = Query(default="gif", pattern="^(gif|image|video|webp)$"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    meme = await db.memes.find_unique(where={"slug": slug})
    if not meme:
        raise HTTPException(404, "Meme not found")
    
    url = build_cdn_url(slug, format)
    background_tasks.add_task(increment_download_count, meme.id)
    return RedirectResponse(url=url, status_code=301)
```

---

## Health Controller

```python
# api/v1/health.py
@router.get("/health")
async def health_check(request: Request):
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - START_TIME),
        "models": {
            "text_model": "loaded" if request.app.state.text_model else "missing",
            "emotion": "loaded" if request.app.state.emotion_pipeline else "missing",
        },
        "services": {
            "redis": await check_redis(),
            "qdrant": await check_qdrant(),
            "database": await check_db(),
        }
    }
```

---

## Controller Design Rules

1. **Controllers are thin** — validate input, call service, return response
2. **No business logic in controllers** — scoring, ranking, caching lives in services
3. **Use `BackgroundTasks`** for analytics — don't block the response
4. **Always use Pydantic response models** — automatic serialization + docs
5. **Return consistent error format** — `{success, error, message}` on all errors

---

> **Related Documents:**
> - [API_Architecture.md](./API_Architecture.md) — Full backend architecture
> - [Services.md](./Services.md) — Service layer implementations
> - [07_APIs/Search_API.md](../07_APIs/Search_API.md) — Search endpoint spec
