"""
MemeGPT — Redis Cache Module (FIXED & FULL SPECIFICATION).

Uses Upstash Redis via redis-py for persistent caching across restarts.
Falls back to in-memory dict if Redis is unavailable (graceful degradation).

Specification:
- 04_Redis_Cache.md
- Section 2 of GAP_ANALYSIS_FULL.md
"""

import hashlib
import json
import logging
import time
from typing import Any, Optional, Tuple, Dict

from app.config import settings

logger = logging.getLogger("memegpt.cache")

# ──────────────────────────────────────────────────────────────────────────────
# Redis Client Singleton
# ──────────────────────────────────────────────────────────────────────────────

_redis_client = None
_fallback_cache: Dict[str, Tuple[Any, float]] = {}  # {key: (value, expires_at)}
_rate_counts: Dict[str, Dict[str, Any]] = {}


def get_redis_client():
    """
    Returns real Redis client connected to Upstash / local Redis.
    Falls back gracefully if Redis is not configured.
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    redis_url = (
        getattr(settings, "REDIS_URL", "")
        or getattr(settings, "UPSTASH_REDIS_URL", "")
        or getattr(settings, "UPSTASH_REDIS_REST_URL", "")
    )

    if not redis_url:
        logger.info(
            "REDIS_URL not set — cache is in-memory only. "
            "Set REDIS_URL in .env for persistent caching."
        )
        return None

    try:
        import redis

        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=2,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        _redis_client.ping()
        logger.info("✅ Redis connected (Upstash / Redis)")
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
    raw = f"{str(query).strip().lower()}:{format_pref}:{nsfw}"
    return f"search:{hashlib.md5(raw.encode('utf-8')).hexdigest()}"


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
    Default TTL: 1 hour (3600s).
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
        try:
            oldest = min(_fallback_cache, key=lambda k: _fallback_cache[k][1])
            del _fallback_cache[oldest]
        except Exception:
            pass

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

    # Fallback clear matching in-memory
    prefix = pattern.replace("*", "")
    matching = [k for k in list(_fallback_cache.keys()) if k.startswith(prefix)]
    for k in matching:
        _fallback_cache.pop(k, None)
    return len(matching)


# ──────────────────────────────────────────────────────────────────────────────
# Rate Limiting (Redis-backed, persistent)
# ──────────────────────────────────────────────────────────────────────────────

def rate_limit_check(identifier: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
    """
    Check if identifier (IP or API key) has exceeded the rate limit.

    Args:
        identifier: IP address or API key prefix
        limit: Max requests per window
        window_seconds: Time window in seconds

    Returns:
        (allowed: bool, remaining: int)
    """
    key = f"ratelimit:{hashlib.md5(identifier.encode('utf-8')).hexdigest()}"
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
            return True, limit

    # In-memory fallback
    now = time.time()
    record = _rate_counts.get(key, {"count": 0, "reset_at": now + window_seconds})

    if now > record["reset_at"]:
        record = {"count": 0, "reset_at": now + window_seconds}

    record["count"] += 1
    _rate_counts[key] = record

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
# Legacy Compatibility
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

    def clear(self) -> None:
        cache_flush_pattern("search:*")

    def stats(self) -> dict:
        return get_cache_stats()

    def get_stats(self) -> dict:
        return get_cache_stats()


query_cache = _QueryCache()
