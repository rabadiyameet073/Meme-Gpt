"""
Redis Cache Layer — with in-memory fallback for local dev without Redis.
Cache keys:
  search:{hash_of_query}  TTL 1 hour
  trending:{category}     TTL 30 minutes
  meme:{id}               TTL 24 hours
  ratelimit:{ip}          TTL 1 minute
"""
import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger("core.cache")


class InMemoryCache:
    """Fallback in-memory cache when Redis is unavailable."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def flushdb(self) -> None:
        self._store.clear()


class CacheService:
    """
    Redis-backed cache with transparent fallback to in-memory.
    All values are JSON-serialised for Redis compatibility.
    """

    def __init__(self):
        self._redis = None
        self._fallback = InMemoryCache()
        self._using_fallback = False
        self._connect()

    def _connect(self) -> None:
        from app.core.config import settings
        try:
            import redis
            self._redis = redis.from_url(
                settings.UPSTASH_REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._redis.ping()
            logger.info("Redis cache connected successfully.")
        except Exception as e:
            logger.warning(f"Redis unavailable — using in-memory cache fallback: {e}")
            self._redis = None
            self._using_fallback = True

    def get(self, key: str) -> Optional[Any]:
        if self._redis:
            try:
                raw = self._redis.get(key)
                if raw:
                    return json.loads(raw)
                return None
            except Exception as e:
                logger.warning(f"Redis GET failed, falling back: {e}")
        return self._fallback.get(key)

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        if self._redis:
            try:
                self._redis.setex(key, ttl, json.dumps(value))
                return
            except Exception as e:
                logger.warning(f"Redis SET failed, falling back: {e}")
        self._fallback.set(key, value, ttl)

    def delete(self, key: str) -> None:
        if self._redis:
            try:
                self._redis.delete(key)
                return
            except Exception:
                pass
        self._fallback.delete(key)

    @property
    def is_connected(self) -> bool:
        return self._redis is not None


cache_service = CacheService()
