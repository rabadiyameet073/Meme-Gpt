"""Rate Limiting module for MemeGPT.
Provides sliding-window token tracking and per-tier request quota enforcement
backed by Redis when configured, with graceful in-memory sliding window fallback.
"""
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from app.core.cache import rate_limit_check, get_redis_client, _rate_counts
from fastapi import Request, Response, HTTPException


class RateLimiter:
    """Sliding-window rate limiter per identifier with Redis backing and memory fallback."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check(self, identifier: str, limit: int) -> Tuple[bool, int, int]:
        """Checks rate limit for an identifier.
        Returns:
            (allowed: bool, remaining: int, retry_after: int)
        """
        allowed, remaining, retry_after, _ = self.check_with_window(identifier, limit, self.window_seconds)
        return allowed, remaining, retry_after

    def check_with_window(
        self, identifier: str, limit: int, window_seconds: int = 60
    ) -> Tuple[bool, int, int, int]:
        """Checks rate limit with custom window duration.
        Returns:
            (allowed: bool, remaining: int, retry_after: int, reset_epoch: int)
        """
        now = time.time()
        client = get_redis_client()
        if client:
            allowed, remaining = rate_limit_check(identifier, limit, window_seconds)
            reset_epoch = int(now + window_seconds)
            retry_after = window_seconds if not allowed else 0
            return allowed, remaining, retry_after, reset_epoch

        # In-memory sliding window fallback
        self._history[identifier] = [
            t for t in self._history[identifier] if now - t < window_seconds
        ]

        # Prevent unbounded growth of in-memory fallback dictionary
        if len(self._history) > 1000:
            expired_keys = [
                k for k, timestamps in self._history.items()
                if not timestamps or (now - timestamps[-1] >= window_seconds)
            ]
            for k in expired_keys:
                self._history.pop(k, None)
            if len(self._history) > 1000:
                oldest_keys = sorted(
                    self._history.keys(),
                    key=lambda k: self._history[k][-1] if self._history[k] else 0
                )[:200]
                for k in oldest_keys:
                    self._history.pop(k, None)

        current_count = len(self._history[identifier])
        if current_count >= limit:
            oldest = self._history[identifier][0]
            retry_after = max(1, int(window_seconds - (now - oldest)))
            reset_epoch = int(now + retry_after)
            return False, 0, retry_after, reset_epoch

        self._history[identifier].append(now)
        remaining = max(0, limit - len(self._history[identifier]))
        reset_epoch = int(now + window_seconds)
        return True, remaining, 0, reset_epoch

    def reset(self, identifier: str | None = None):
        """Resets rate history for a specific key or all keys."""
        if identifier:
            self._history.pop(identifier, None)
            _rate_counts.pop(identifier, None)
        else:
            self._history.clear()
            _rate_counts.clear()


# Global singleton instance
rate_limiter = RateLimiter(window_seconds=60)


def require_route_rate_limit(route_name: str):
    """
    FastAPI dependency factory enforcing per-endpoint rate limits (API-11).
    Per Rate_Limiting.md:
      /search: 30 req/min (free), 100 req/min (dev), 500 req/min (pro)
      /feedback: 120 req/min
    """
    async def _route_rate_limit_dependency(request: Request, response: Response):
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "127.0.0.1")
        )
        api_key_header = (
            request.headers.get("x-api-key", "").strip()
            or request.headers.get("authorization", "").removeprefix("Bearer ").strip()
        )
        tier = "anonymous"
        if api_key_header:
            try:
                from app.core.auth import get_cached_api_key_tier
                tier, _ = get_cached_api_key_tier(api_key_header)
            except Exception:
                tier = "anonymous"

        from app.core.auth import get_rate_limit_for_tier
        limit = get_rate_limit_for_tier(tier, route_type=route_name)
        identifier = f"route:{route_name}:ip:{client_ip}" if (not api_key_header or tier == "anonymous") else f"route:{route_name}:key:{api_key_header}"

        window_seconds = 60
        allowed, remaining, retry_after, reset_epoch = rate_limiter.check_with_window(
            identifier, limit, window_seconds=window_seconds
        )

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(reset_epoch)
        response.headers["X-RateLimit-Window"] = str(window_seconds)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": f"{limit} {route_name} requests per minute allowed. Retry after {retry_after} seconds.",
                    "retry_after": retry_after or 60,
                    "limit": limit,
                    "window": f"{window_seconds}s",
                },
                headers={
                    "Retry-After": str(retry_after or 60),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_epoch),
                    "X-RateLimit-Window": str(window_seconds),
                }
            )

    return _route_rate_limit_dependency
