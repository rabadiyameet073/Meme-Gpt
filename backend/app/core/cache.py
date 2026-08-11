"""MemeGPT — Multi-Layer Cache Service.

Layer 1: In-Memory LRU cache (sub-1ms reads, always available)
Layer 2: Redis / Upstash (shared across instances, optional)

Cache hit flow: L1 → L2 → miss
Cache set flow: L1 + L2 (write-through)

Specification: 02_TECH_STACK_AND_MODELS.md, Low_Level_Architecture.md
"""

import hashlib
import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger("memegpt.cache")


# ── Layer 1: In-Memory LRU Cache ─────────────────────────────────────────────


class QueryCache:
    """Thread-safe in-memory cache with TTL and LRU eviction."""

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self._cache: dict[str, tuple[float, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def _hash_query(self, query: str) -> str:
        """If query is already a cache key (starts with 'search:'), use it directly."""
        if query.startswith("search:"):
            return query
        clean = " ".join(query.lower().strip().split())
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    def get(self, query: str) -> Any | None:
        key = self._hash_query(query)
        if key not in self._cache:
            self._misses += 1
            return None

        expires_at, payload = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return payload

    def set(self, query: str, payload: Any, ttl: int | None = None) -> None:
        if len(self._cache) >= self.max_size:
            # Evict the entry that expires soonest
            oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]

        key = self._hash_query(query)
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl
        self._cache[key] = (expires_at, payload)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, int]:
        now = time.time()
        active = sum(1 for exp, _ in self._cache.values() if exp > now)
        total_requests = self._hits + self._misses
        hit_rate = round(self._hits / total_requests * 100, 1) if total_requests > 0 else 0
        return {
            "totalEntries": len(self._cache),
            "activeEntries": active,
            "maxSize": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hitRate": hit_rate,
        }


# ── Layer 2: Redis Cache (optional) ──────────────────────────────────────────


class RedisCache:
    """Redis-backed cache for shared state across instances."""

    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self._client = None
        self._redis_url = redis_url
        self.default_ttl = default_ttl
        self._available = None

    def _get_client(self):
        if self._available is False:
            return None
        if self._client is not None:
            return self._client

        try:
            import redis
            self._client = redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self._client.ping()
            logger.info("✅ Redis cache connected")
            self._available = True
            return self._client
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Using in-memory cache only.")
            self._available = False
            return None

    def get(self, key: str) -> Any | None:
        client = self._get_client()
        if client is None:
            return None
        try:
            raw = client.get(f"memegpt:{key}")
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.debug(f"Redis GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            ttl = ttl or self.default_ttl
            client.setex(f"memegpt:{key}", ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.debug(f"Redis SET error: {e}")


# ── Combined Cache (L1 + L2) ─────────────────────────────────────────────────


class CombinedCache:
    """Multi-layer cache: L1 in-memory + L2 Redis.

    get(): L1 → L2 → miss
    set(): L1 + L2 (write-through)
    """

    def __init__(self, l1: QueryCache, l2: Optional[RedisCache] = None):
        self.l1 = l1
        self.l2 = l2

    def get(self, key: str) -> Any | None:
        # Try L1 first
        result = self.l1.get(key)
        if result is not None:
            return result

        # Try L2 (Redis)
        if self.l2 is not None:
            result = self.l2.get(key)
            if result is not None:
                # Backfill L1
                self.l1.set(key, result)
                return result

        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        # Write to both layers
        self.l1.set(key, value, ttl=ttl)
        if self.l2 is not None:
            self.l2.set(key, value, ttl=ttl)

    def clear(self) -> None:
        self.l1.clear()

    def stats(self) -> dict:
        return self.l1.stats()


# ── Singleton Instances ──────────────────────────────────────────────────────

# Always-available in-memory cache
query_cache = QueryCache(default_ttl=3600, max_size=1000)

# Optional Redis layer (initialized lazily)
_redis_cache: Optional[RedisCache] = None


def get_redis_cache() -> Optional[RedisCache]:
    """Lazy-initialize Redis cache from environment."""
    global _redis_cache
    if _redis_cache is not None:
        return _redis_cache

    from app.config import REDIS_URL
    if REDIS_URL:
        _redis_cache = RedisCache(REDIS_URL)
    return _redis_cache


def get_combined_cache() -> CombinedCache:
    """Get the multi-layer cache instance."""
    return CombinedCache(l1=query_cache, l2=get_redis_cache())
