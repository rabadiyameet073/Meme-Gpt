"""Rate Limiting module for MemeGPT.
Provides sliding-window token tracking and per-tier request quota enforcement
backed by Redis when configured, with graceful in-memory sliding window fallback.
"""
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from app.core.cache import rate_limit_check, get_redis_client, _rate_counts


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
