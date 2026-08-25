# 04 — Redis Cache — Real Upstash Integration
# Fix in-memory dict → real Redis, persistent across restarts

> **Gap Source:** Section 2 of GAP_ANALYSIS_FULL.md  
> **Priority:** P0  
> **Files to edit:** `d:\Meme GPT\backend\app\core\cache.py`

---

## WHAT IS BROKEN

`app/core/cache.py` uses an **in-memory Python dictionary** as a cache.  
This means:
- Cache resets every time the server restarts
- Cache is NOT shared across multiple server processes/workers
- Rate limit counters reset on restart (users can bypass limits by restarting)
- `REDIS_URL` env var is read by `config.py` but **never used to connect to Redis**

---

## COMPLETE REPLACEMENT: `cache.py`

**Replace the ENTIRE content** of `d:\Meme GPT\backend\app\core\cache.py` with:

```python
"""
MemeGPT — Redis Cache Module (FIXED).

Uses Upstash Redis via redis-py for persistent caching across restarts.
Falls back to in-memory dict if Redis is unavailable (graceful degradation).

Gap Analysis fixes:
- Real Redis connection via REDIS_URL env var
- Persistent TTL-based caching (1 hour for search results)
- Rate limiting counters stored in Redis (not reset on restart)
- Cache key: MD5 hash of query+format+nsfw
"""

import hashlib
import json
import logging
import time
from typing import Any, Optional

from app.config import settings

logger = logging.getLogger("memegpt.cache")

# ──────────────────────────────────────────────────────────────────────────────
# Redis Client Singleton
# ──────────────────────────────────────────────────────────────────────────────

_redis_client = None
_fallback_cache: dict[str, tuple[Any, float]] = {}  # {key: (value, expires_at)}


def get_redis_client():
    """
    Returns real Redis client connected to Upstash.
    Falls back gracefully if Redis is not configured.
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    redis_url = getattr(settings, "REDIS_URL", "") or getattr(settings, "UPSTASH_REDIS_URL", "")

    if not redis_url:
        logger.warning(
            "REDIS_URL not set — cache is in-memory only (not persistent). "
            "Set REDIS_URL in .env for persistent caching."
        )
        return None

    try:
        import redis

        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,          # Return strings, not bytes
            socket_connect_timeout=3,       # Fail fast if unreachable
            socket_timeout=2,               # Timeout on operations
            retry_on_timeout=True,
            health_check_interval=30,
        )
        # Test connectivity
        _redis_client.ping()
        logger.info("✅ Redis connected (Upstash)")
        return _redis_client

    except ImportError:
        logger.error("redis package not installed. Run: pip install redis")
        return None
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} — using in-memory fallback")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Cache Operations
# ──────────────────────────────────────────────────────────────────────────────

def make_cache_key(query: str, format_pref: str = "gif", nsfw: bool = False) -> str:
    """
    Build cache key from search parameters.
    Uses MD5 hash — never stores raw query text (GDPR).
    Format: search:{md5}
    """
    raw = f"{query.strip().lower()}:{format_pref}:{nsfw}"
    return f"search:{hashlib.md5(raw.encode()).hexdigest()}"


def cache_get(key: str) -> Optional[Any]:
    """
    Get value from cache. Returns None on miss.
    Tries Redis first, falls back to in-memory.
    """
    client = get_redis_client()

    if client:
        try:
            value = client.get(key)
            if value is not None:
                logger.debug(f"Cache HIT (Redis): {key[:30]}...")
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis GET failed: {e} — checking fallback")

    # In-memory fallback
    if key in _fallback_cache:
        value, expires_at = _fallback_cache[key]
        if time.time() < expires_at:
            logger.debug(f"Cache HIT (memory): {key[:30]}...")
            return value
        else:
            del _fallback_cache[key]

    return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in cache with TTL (seconds).
    Default TTL: 1 hour (3600s) per specification.
    Returns True on success.
    """
    client = get_redis_client()

    if client:
        try:
            client.setex(key, ttl, json.dumps(value))
            logger.debug(f"Cache SET (Redis): {key[:30]}... TTL={ttl}s")
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed: {e} — using fallback")

    # In-memory fallback
    _fallback_cache[key] = (value, time.time() + ttl)

    # Prevent unbounded growth — evict oldest if >500 keys
    if len(_fallback_cache) > 500:
        oldest = min(_fallback_cache, key=lambda k: _fallback_cache[k][1])
        del _fallback_cache[oldest]

    logger.debug(f"Cache SET (memory): {key[:30]}... TTL={ttl}s")
    return True


def cache_delete(key: str) -> bool:
    """Delete a specific cache key."""
    client = get_redis_client()
    if client:
        try:
            client.delete(key)
            return True
        except Exception:
            pass
    _fallback_cache.pop(key, None)
    return True


def cache_flush_pattern(pattern: str = "search:*") -> int:
    """
    Delete all keys matching pattern.
    Useful for admin cache invalidation.
    """
    client = get_redis_client()
    if client:
        try:
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache flush failed: {e}")
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# Rate Limiting (Redis-backed, persistent)
# ──────────────────────────────────────────────────────────────────────────────

def rate_limit_check(identifier: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
    """
    Check if identifier (IP or API key) has exceeded the rate limit.

    Args:
        identifier: IP address or API key prefix
        limit: Max requests per window
        window_seconds: Time window in seconds

    Returns:
        (allowed: bool, remaining: int)
    """
    key = f"ratelimit:{hashlib.md5(identifier.encode()).hexdigest()}"
    client = get_redis_client()

    if client:
        try:
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = pipe.execute()
            count = results[0]
            remaining = max(limit - count, 0)
            return count <= limit, remaining
        except Exception as e:
            logger.warning(f"Rate limit Redis check failed: {e} — allowing request")
            return True, limit  # Fail open

    # In-memory fallback
    _rate_counts: dict = getattr(cache_flush_pattern, "_counts", {})
    now = time.time()
    record = _rate_counts.get(key, {"count": 0, "reset_at": now + window_seconds})

    if now > record["reset_at"]:
        record = {"count": 0, "reset_at": now + window_seconds}

    record["count"] += 1
    _rate_counts[key] = record

    # Store on function (cheap singleton)
    cache_flush_pattern._counts = _rate_counts

    return record["count"] <= limit, max(limit - record["count"], 0)


# ──────────────────────────────────────────────────────────────────────────────
# Cache Stats
# ──────────────────────────────────────────────────────────────────────────────

def get_cache_stats() -> dict:
    """Returns cache statistics for health endpoint."""
    client = get_redis_client()
    if client:
        try:
            info = client.info("stats")
            return {
                "backend": "redis",
                "connected": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "keys": client.dbsize(),
            }
        except Exception:
            pass

    return {
        "backend": "memory",
        "connected": False,
        "keys": len(_fallback_cache),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Legacy Compatibility (keep old interface working)
# ──────────────────────────────────────────────────────────────────────────────

class _QueryCache:
    """
    Backwards-compatible wrapper.
    Old code uses query_cache.get(key) / query_cache.set(key, val, ttl).
    """
    def get(self, key: str) -> Optional[Any]:
        return cache_get(key)

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        return cache_set(key, value, ttl)

    def delete(self, key: str) -> bool:
        return cache_delete(key)


# Singleton instance used throughout the codebase
query_cache = _QueryCache()
```

---

## STEP 2 — Install Redis

```bash
cd "d:\Meme GPT\backend"
pip install redis
```

Add to `requirements.txt`:
```
redis>=5.0.0
```

---

## STEP 3 — Update `recommendation_service.py` to Use New Cache API

Find the cache usage in `recommendation_service.py` and ensure it uses:
```python
from app.core.cache import cache_get, cache_set, make_cache_key

# Build cache key
cache_key = make_cache_key(user_text, format_pref, nsfw)

# Check cache
cached = cache_get(cache_key)
if cached:
    return cached

# ... run pipeline ...

# Store result
cache_set(cache_key, result, ttl=3600)
```

---

## STEP 4 — Update Rate Limiting in `main.py`

Replace the in-memory rate limiting middleware with Redis-backed check:

```python
from app.core.cache import rate_limit_check

# In the rate limit middleware:
allowed, remaining = rate_limit_check(
    identifier=client_ip,
    limit=rate_limit,
    window_seconds=60
)
if not allowed:
    return JSONResponse(
        status_code=429,
        content={"error": "rate_limit_exceeded", "retry_after": 60},
        headers={"Retry-After": "60", "X-RateLimit-Remaining": "0"},
    )
```

---

## STEP 5 — Test Redis Connection

```bash
cd "d:\Meme GPT\backend"
python -c "
from app.core.cache import get_redis_client, cache_set, cache_get
client = get_redis_client()
if client:
    print('✅ Redis connected!')
    cache_set('test_key', {'hello': 'world'}, ttl=60)
    result = cache_get('test_key')
    print('Cache test:', result)
else:
    print('⚠️ Redis not connected — using in-memory fallback')
"
```
