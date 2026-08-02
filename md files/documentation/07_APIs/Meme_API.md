# MemeGPT — Meme API, Trending API, Feedback API & Rate Limiting

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete specification for all non-search API endpoints — Meme detail, Meme download, Trending, Feedback, and Rate Limiting policies.

---

## Endpoint Summary

| Method | Path | Description | Auth | Rate Limit |
|---|---|---|---|---|
| GET | `/api/v1/memes/{slug}` | Get meme details | None | 60/min |
| GET | `/api/v1/memes/{slug}/download?format=gif` | Download meme file | None | 60/min |
| GET | `/api/v1/trending` | Get trending memes | None | 60/min |
| POST | `/api/v1/feedback` | Record user interaction | None | 120/min |
| GET | `/health` | Health check | None | No limit |

---

## `GET /api/v1/memes/{slug}`

Get full meme details by slug. Used for individual meme SEO pages and detail views.

### Path Parameters

| Param | Type | Description |
|---|---|---|
| `slug` | string | URL-safe meme identifier (e.g., `this-is-fine`) |

### Response (200 OK)

```json
{
  "id": "meme_042",
  "name": "This Is Fine",
  "slug": "this-is-fine",
  "description": "A dog sitting in a burning room saying 'this is fine'",
  "origin": "KC Green's Gunshow webcomic (2013)",
  "categories": ["work", "stress", "acceptance", "chaos"],
  "emotions": ["frustration", "denial", "resignation"],
  "formats": {
    "gif": "https://cdn.memegpt.com/gifs/this-is-fine.gif",
    "image": "https://cdn.memegpt.com/images/this-is-fine.jpg",
    "video": null,
    "webp": "https://cdn.memegpt.com/webp/this-is-fine.webp"
  },
  "preview_url": "https://cdn.memegpt.com/thumbs/this-is-fine.webp",
  "share_url": "https://memegpt.com/meme/this-is-fine",
  "related_memes": ["disaster-girl", "everything-is-fine-dog"],
  "usage_count": 15823,
  "download_count": 4291,
  "popularity_score": 0.87,
  "source": "imgflip",
  "nsfw": false,
  "created_at": "2024-01-15T00:00:00Z",
  "indexed_at": "2024-06-01T12:00:00Z"
}
```

### Error Responses

| Status | When | Response |
|---|---|---|
| 404 | Slug doesn't exist | `{"error": "meme_not_found", "message": "No meme found with slug 'invalid-slug'"}` |

### Implementation

```python
@router.get("/memes/{slug}")
async def get_meme(slug: str, db: Database = Depends(get_db)):
    meme = await db.memes.find_unique(where={"slug": slug})
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    # Increment view count (async, non-blocking)
    background_tasks.add_task(
        db.memes.update,
        where={"slug": slug},
        data={"view_count": {"increment": 1}}
    )
    return meme
```

---

## `GET /api/v1/memes/{slug}/download?format=gif`

Streams or redirects to the CDN file for download. Tracks the download in analytics.

### Query Parameters

| Param | Type | Default | Options |
|---|---|---|---|
| `format` | string | `gif` | `gif`, `image`, `video`, `webp` |

### Response (301 Redirect)

```http
HTTP/1.1 301 Moved Permanently
Location: https://cdn.memegpt.com/gifs/this-is-fine.gif
Content-Type: text/html
```

### Error Responses

| Status | When |
|---|---|
| 404 | Meme not found |
| 400 | Requested format not available for this meme |

### Implementation

```python
@router.get("/memes/{slug}/download")
async def download_meme(
    slug: str,
    format: str = Query(default="gif", pattern="^(gif|image|video|webp)$"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    meme = await get_meme_by_slug(slug)
    url = meme.formats.get(format)
    if not url:
        raise HTTPException(400, f"Format '{format}' not available for this meme")
    
    # Track download (non-blocking)
    background_tasks.add_task(increment_download_count, meme.id)
    
    return RedirectResponse(url=url, status_code=301)
```

---

## `GET /api/v1/trending`

Returns trending memes updated hourly. Based on a composite score of views, downloads, and shares in the last 24 hours.

### Query Parameters

| Param | Type | Default | Options |
|---|---|---|---|
| `category` | string | `all` | `all`, `work`, `gaming`, `relationships`, `tech`, `sports` |
| `limit` | integer | 20 | 1–50 |
| `offset` | integer | 0 | Pagination offset |

### Response (200 OK)

```json
{
  "success": true,
  "category": "work",
  "results": [
    {
      "id": "meme_042",
      "name": "This Is Fine",
      "slug": "this-is-fine",
      "preview_url": "https://cdn.memegpt.com/thumbs/this-is-fine.webp",
      "trending_score": 0.94,
      "view_count_24h": 1523,
      "categories": ["work", "stress"]
    }
  ],
  "total": 245,
  "offset": 0,
  "limit": 20
}
```

### Trending Score Calculation

```python
def calculate_trending_score(meme, time_window_hours=24):
    """
    Composite trending score — recalculated hourly via cron.
    """
    views_24h = get_feedback_count(meme.id, "view", hours=time_window_hours)
    downloads_24h = get_feedback_count(meme.id, "download", hours=time_window_hours)
    shares_24h = get_feedback_count(meme.id, "share", hours=time_window_hours)
    thumbs_up = get_feedback_count(meme.id, "thumbs_up", hours=time_window_hours)
    
    raw_score = (
        views_24h * 0.1 +
        downloads_24h * 2.0 +
        shares_24h * 3.0 +
        thumbs_up * 2.0
    )
    
    # Normalize to 0.0–1.0
    return min(1.0, raw_score / 1000)
```

---

## `POST /api/v1/feedback`

Records user interactions for model improvement. Every action updates the meme's popularity score in the weekly retraining cycle.

### Request

```json
{
  "query_id": "q_xyz789",
  "meme_id": "meme_042",
  "action": "download",
  "session_id": "sess_abc123"
}
```

### Valid Actions & Signal Weights

| Action | Weight | Description | When Recorded |
|---|---|---|---|
| `view` | +0.1 | Meme appeared in results | Auto (on search response) |
| `click` | +0.5 | User clicked to preview | User clicks MemeCard |
| `copy` | +1.0 | Copied to clipboard | User clicks "Copy" button |
| `download` | +2.0 | Downloaded file | User clicks "Download" |
| `share` | +3.0 | Shared via native share | User clicks "Share" |
| `thumbs_up` | +2.0 | Explicit positive vote | User clicks 👍 |
| `thumbs_down` | -1.0 | Explicit negative vote | User clicks 👎 |
| `skip` | -0.3 | Scrolled past without interaction | Auto (5s visible, no click) |

### Response (200 OK)

```json
{
  "recorded": true
}
```

### Implementation

```python
@router.post("/feedback")
async def record_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    # Validate action
    valid_actions = {"view","click","copy","download","share","thumbs_up","thumbs_down","skip"}
    if feedback.action not in valid_actions:
        raise HTTPException(400, f"Invalid action: {feedback.action}")
    
    # Record async (don't block response)
    background_tasks.add_task(
        insert_feedback,
        session_id=feedback.session_id,
        meme_id=feedback.meme_id,
        query_id=feedback.query_id,
        action=feedback.action
    )
    
    return {"recorded": True}
```

---

## Rate Limiting Policy

### Tiers

| Tier | Overall Limit | Search Limit | Window | Key |
|---|---|---|---|---|
| **Free (anonymous)** | 60 req/min | 30 req/min | Per IP | Client IP |
| **Pro (authenticated)** | 300 req/min | 120 req/min | Per API key | `X-API-Key` header |
| **Internal** | Unlimited | Unlimited | — | Internal service token |

### Rate Limit Response Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1706745600
```

### 429 Error Response

```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "60 requests per minute allowed. Retry after 23 seconds.",
  "retry_after": 23
}
```

### Implementation (Token Bucket via Redis)

```python
import time
from redis import Redis

async def check_rate_limit(client_ip: str, endpoint: str) -> bool:
    """Token bucket rate limiter using Redis ZADD."""
    key = f"ratelimit:{client_ip}:{endpoint}"
    now = time.time()
    window = 60  # 1 minute window
    limit = 30 if endpoint == "search" else 60
    
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)  # Remove expired tokens
    pipe.zadd(key, {str(now): now})               # Add current request
    pipe.zcard(key)                                # Count requests in window
    pipe.expire(key, window)                       # Auto-cleanup
    _, _, count, _ = pipe.execute()
    
    return count <= limit
```

---

## Best Practices

1. **Always return consistent JSON** — even for 404 and 500 errors
2. **Use `BackgroundTasks`** for all analytics writes — never block the response
3. **Include rate limit headers** on every response — not just 429s
4. **Validate action enum** server-side — don't trust client input
5. **Increment view counts async** — meme detail page shouldn't wait for DB writes
6. **Cache trending results** for 5 minutes — reduces database load dramatically
7. **Use `301` for downloads** — client can cache the CDN redirect

---

## Edge Cases

| Scenario | Behavior |
|---|---|
| Download format not available | 400 with "Format not available" message |
| Feedback for non-existent meme | Accepted silently (eventual consistency) |
| Duplicate feedback (same action) | Accepted (idempotent writes) |
| Trending with no data | Return empty results array, not an error |
| Rate limit on feedback endpoint | Higher limit (120/min) — encourage more feedback |

---

> **Related Documents:**
> - [API_Overview.md](./API_Overview.md) — All endpoints summary
> - [Search_API.md](./Search_API.md) — Core search endpoint
> - [03_Backend/API_Architecture.md](../03_Backend/API_Architecture.md) — Backend architecture
