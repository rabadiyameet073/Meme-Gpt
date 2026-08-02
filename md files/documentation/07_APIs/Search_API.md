# MemeGPT — Search API (Complete Specification)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete specification for `POST /api/v1/search` — MemeGPT's core endpoint. Accepts natural language text and returns AI-ranked meme recommendations.

---

## Endpoint

```
POST /api/v1/search
```

---

## Request

### Headers

| Header | Required | Description |
|---|---|---|
| `Content-Type` | ✅ | Must be `application/json` |
| `X-API-Key` | ❌ | Pro tier API key (Phase 2) |
| `Origin` | ❌ | Required for CORS validation |

### Body

```json
{
  "query": "my boss scheduled a meeting that could have been an email",
  "format_preference": "gif",
  "nsfw": false,
  "limit": 5,
  "session_id": "sess_abc123",
  "filters": {
    "categories": ["work"],
    "exclude_ids": ["meme_123"]
  }
}
```

### Field Reference

| Field | Type | Required | Default | Validation | Description |
|---|---|---|---|---|---|
| `query` | string | ✅ | — | 1–2000 characters | Natural language input |
| `format_preference` | string | ❌ | `"gif"` | `gif\|image\|video\|any` | Preferred format |
| `nsfw` | boolean | ❌ | `false` | — | Include NSFW content |
| `limit` | integer | ❌ | `5` | 1–20 | Maximum results |
| `session_id` | string | ❌ | `null` | — | Anonymous session for tracking |
| `filters.categories` | string[] | ❌ | `[]` | — | Filter by category |
| `filters.exclude_ids` | string[] | ❌ | `[]` | — | Exclude specific memes |

---

## Response (200 OK)

```json
{
  "success": true,
  "query_id": "q_xyz789",
  "results": [
    {
      "id": "meme_042",
      "name": "This Is Fine",
      "slug": "this-is-fine",
      "relevance_score": 0.94,
      "emotion_match": ["frustration", "acceptance"],
      "preview_url": "https://cdn.memegpt.com/thumbs/this-is-fine.webp",
      "formats": {
        "gif": "https://cdn.memegpt.com/gifs/this-is-fine.gif",
        "image": "https://cdn.memegpt.com/images/this-is-fine.jpg",
        "video": null,
        "webp": "https://cdn.memegpt.com/webp/this-is-fine.webp"
      },
      "share_url": "https://memegpt.com/meme/this-is-fine?ref=q_xyz789",
      "meme_type": "reaction",
      "categories": ["work", "stress", "relatable"]
    }
  ],
  "intent_parsed": {
    "emotion": "frustration",
    "situation": "unnecessary meeting at work",
    "tone": "sarcastic"
  },
  "response_time_ms": 487,
  "cached": false
}
```

### Response Field Reference

| Field | Type | Description |
|---|---|---|
| `success` | boolean | Always `true` for successful responses |
| `query_id` | string | Unique ID for this search (used in feedback) |
| `results[]` | array | Ordered by `relevance_score` (highest first) |
| `results[].id` | string | Meme identifier |
| `results[].name` | string | Human-readable meme name |
| `results[].slug` | string | URL-safe slug for SEO pages |
| `results[].relevance_score` | float | 0.0–1.0 composite score |
| `results[].emotion_match` | string[] | Detected emotions matching this meme |
| `results[].preview_url` | string | WebP thumbnail URL (fast loading) |
| `results[].formats` | object | Available format URLs (null if unavailable) |
| `results[].share_url` | string | Shareable link to meme page |
| `results[].meme_type` | string | `reaction\|comparison\|advice\|relatable\|wholesome` |
| `results[].categories` | string[] | Content categories |
| `intent_parsed` | object | AI-detected intent (for debugging/UI) |
| `response_time_ms` | integer | Server-side processing time |
| `cached` | boolean | Whether result came from cache |

---

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "error": "invalid_request",
  "message": "Query must be between 1 and 2000 characters"
}
```

### 422 Validation Error

```json
{
  "success": false,
  "error": "validation_error",
  "message": "Request validation failed",
  "details": [
    {"field": "query", "message": "Field required", "type": "missing"},
    {"field": "limit", "message": "Input should be less than or equal to 20", "type": "less_than_equal"}
  ]
}
```

### 429 Rate Limit Exceeded

```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "30 search requests per minute allowed. Retry after 23 seconds.",
  "retry_after": 23
}
```

### 500 Internal Error

```json
{
  "success": false,
  "error": "internal_error",
  "message": "Something went wrong. Please try again."
}
```

### 503 Service Unavailable

```json
{
  "success": false,
  "error": "service_unavailable",
  "message": "Search service is temporarily unavailable. Please try again in a few minutes."
}
```

---

## Error Summary

| Status | Code | When | Client Action |
|---|---|---|---|
| 400 | `invalid_request` | Missing query or bad format | Show validation error |
| 422 | `validation_error` | Pydantic validation failed | Show field-level errors |
| 429 | `rate_limit_exceeded` | >30 searches/min | Show countdown timer |
| 500 | `internal_error` | Server failure | Retry once, show error |
| 503 | `service_unavailable` | Qdrant/Groq down | Show "try again later" |

---

## Examples

### cURL

```bash
curl -X POST https://api.memegpt.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Monday morning feeling",
    "format_preference": "gif",
    "limit": 5
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('https://api.memegpt.com/api/v1/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'when the code finally works',
    format_preference: 'gif',
    limit: 5
  })
});

const data = await response.json();
if (data.success) {
  data.results.forEach(meme => {
    console.log(`${meme.name} — ${Math.round(meme.relevance_score * 100)}% match`);
  });
}
```

### Python (httpx)

```python
import httpx

async def search_memes(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.memegpt.com/api/v1/search",
            json={"query": query, "format_preference": "gif", "limit": 5},
            timeout=5.0
        )
        return response.json()
```

---

## Performance

| Metric | Target | Actual |
|---|---|---|
| P50 latency | <1.0s | ~560ms |
| P95 latency | <3.0s | ~1.2s |
| Cache hit latency | <50ms | ~15ms |
| Cache hit rate | >50% | ~60% |
| Max concurrent | 50 req | Tested |

---

## Rate Limiting

| Tier | Limit | Window | Key |
|---|---|---|---|
| Free | **30 req/min** | Per IP | `X-Forwarded-For` |
| Pro | 120 req/min | Per API key | `X-API-Key` header |

### Response Headers (every response)

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 27
X-RateLimit-Reset: 1706745600
```

---

> **Related Documents:**
> - [API_Overview.md](./API_Overview.md) — All endpoints summary
> - [Meme_API.md](./Meme_API.md) — Meme detail, download, trending, feedback
> - [03_Backend/API_Architecture.md](../03_Backend/API_Architecture.md) — Backend architecture
> - [03_Backend/Services.md](../03_Backend/Services.md) — Service layer implementation
