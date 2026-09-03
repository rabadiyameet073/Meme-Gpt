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
from typing import Any, Optional, Tuple, Dict

from app.config import settings

logger = logging.getLogger("memegpt.cache")

# ──────────────────────────────────────────────────────────────────────────────
# Redis Client Singleton
# ──────────────────────────────────────────────────────────────────────────────

_redis_client = None
_fallback_cache: Dict[str, Tuple[Any, float]] = {}  # {key: (value, expires_at)}
_rate_counts: Dict[str, Dict[str, Any]] = {}


class UpstashRestClient:
    """Lightweight HTTP REST client for Upstash Redis when running over HTTP."""
    def __init__(self, rest_url: str, rest_token: str):
        self.url = rest_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {rest_token}"}
        import httpx
        self._client = httpx.Client(timeout=3.0, headers=self.headers)

    def ping(self) -> bool:
        resp = self._client.post(f"{self.url}/ping")
        return resp.status_code == 200

    def get(self, key: str) -> Optional[str]:
        resp = self._client.post(f"{self.url}/get/{key}")
        if resp.status_code == 200:
            return resp.json().get("result")
        return None

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        cmd = [self.url, "set", key, str(value)]
        if ex:
            cmd.extend(["ex", str(ex)])
        resp = self._client.post("/".join(cmd))
        return resp.status_code == 200

    def setex(self, key: str, time_sec: int, value: str) -> bool:
        return self.set(key, value, ex=time_sec)

    def delete(self, *keys: str) -> int:
        deleted = 0
        for k in keys:
            resp = self._client.post(f"{self.url}/del/{k}")
            if resp.status_code == 200:
                deleted += int(resp.json().get("result", 0) or 0)
        return deleted

    def pipeline(self):
        class UpstashPipeline:
            def __init__(self, parent):
                self.parent = parent
                self.commands = []

            def incr(self, key: str):
                self.commands.append(["INCR", key])
                return self

            def expire(self, key: str, seconds: int):
                self.commands.append(["EXPIRE", key, seconds])
                return self

            def execute(self):
                resp = self.parent._client.post(f"{self.parent.url}/pipeline", json=self.commands)
                if resp.status_code == 200:
                    results = resp.json()
                    return [r.get("result") for r in results]
                return [1, 1]
        return UpstashPipeline(self)


def get_redis_client():
    """
    Returns real Redis client connected to Upstash.
    Supports both redis-py (redis://, rediss://) and Upstash REST API (https://).
    Falls back gracefully if Redis is not configured.
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    redis_url = getattr(settings, "REDIS_URL", "") or getattr(settings, "UPSTASH_REDIS_URL", "")
    rest_url = getattr(settings, "UPSTASH_REDIS_REST_URL", "")
    rest_token = getattr(settings, "UPSTASH_REDIS_REST_TOKEN", "")

    # 1. Check for Upstash REST API credentials
    if rest_url and rest_token:
        try:
            client = UpstashRestClient(rest_url, rest_token)
            client.ping()
            _redis_client = client
            logger.info("✅ Redis connected (Upstash REST API)")
            return _redis_client
        except Exception as e:
            logger.warning(f"Upstash REST API connection failed: {e}")

    # 2. Check for redis_url starting with https://
    if redis_url and redis_url.startswith("http"):
        if rest_token:
            try:
                client = UpstashRestClient(redis_url, rest_token)
                client.ping()
                _redis_client = client
                logger.info("✅ Redis connected (Upstash REST API)")
                return _redis_client
            except Exception as e:
                logger.warning(f"Upstash REST API connection failed: {e}")

    # 3. Check for standard Redis connection string (redis://, rediss://)
    global _warned_missing_redis
    if not redis_url:
        if not globals().get("_warned_missing_redis", False):
            globals()["_warned_missing_redis"] = True
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
            return True, limit  # Fail open

    # In-memory fallback
    now = time.time()
    record = _rate_counts.get(key, {"count": 0, "reset_at": now + window_seconds})

    if now > record["reset_at"]:
        record = {"count": 0, "reset_at": now + window_seconds}

    record["count"] += 1
    _rate_counts[key] = record

    # Store on function for compatibility if accessed
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

    def clear(self) -> None:
        cache_flush_pattern("search:*")

    def stats(self) -> dict:
        return get_cache_stats()

    def get_stats(self) -> dict:
        return get_cache_stats()


# Singleton instance used throughout the codebase
query_cache = _QueryCache()
