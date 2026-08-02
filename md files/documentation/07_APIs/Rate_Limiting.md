# MemeGPT — API Rate Limiting

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Detailed documentation of rate limiting policies, implementation, and client handling.

---

## Rate Limit Tiers

| Tier | Scope | Search Limit | General Limit | Window |
|---|---|---|---|---|
| **Free** (no API key) | Per IP address | 30 req/min | 60 req/min | Sliding window |
| **Developer** (API key) | Per API key | 100 req/min | 300 req/min | Sliding window |
| **Pro** (paid) | Per API key | 500 req/min | 1000 req/min | Sliding window |

---

## Response Headers

Every API response includes rate limit headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1706745600
X-RateLimit-Window: 60
```

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in current window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |
| `X-RateLimit-Window` | Window duration in seconds |

---

## 429 Response

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 23
```

```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "60 requests per minute allowed. Please slow down.",
  "retry_after": 23,
  "limit": 60,
  "window": "60s"
}
```

---

## Implementation

### Token Bucket Algorithm (Redis)

```python
import time
import redis

async def check_rate_limit(key: str, limit: int, window: int) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    pipe = redis.pipeline()
    now = time.time()
    window_start = now - window
    
    pipe.zremrangebyscore(key, 0, window_start)   # Remove old entries
    pipe.zadd(key, {str(now): now})                # Add current request
    pipe.zcard(key)                                 # Count requests in window
    pipe.expire(key, window)                        # Set expiry
    
    _, _, count, _ = pipe.execute()
    return count <= limit
```

---

## Client Best Practices

1. **Check `X-RateLimit-Remaining`** before each request
2. **Implement exponential backoff** on 429 responses
3. **Cache results client-side** to reduce API calls
4. **Batch requests** where possible
5. **Use `Retry-After` header** to know exactly when to retry

---

> **Related Documents:**
> - [API_Overview.md](./API_Overview.md) · [03_Backend/Middleware.md](../03_Backend/Middleware.md) · [11_Security/Security_Overview.md](../11_Security/Security_Overview.md)
