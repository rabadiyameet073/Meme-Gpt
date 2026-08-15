"""Rate Limiting module for MemeGPT.
Provides sliding-window token tracking and per-tier request quota enforcement.
"""
import time
from collections import defaultdict
from typing import Dict, List, Tuple


class RateLimiter:
    """In-memory sliding-window rate limiter per identifier."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check(self, identifier: str, limit: int) -> Tuple[bool, int, int]:
        """Checks rate limit for an identifier.
        Returns:
            (allowed: bool, remaining: int, retry_after: int)
        """
        now = time.time()
        # Clean expired timestamps outside the sliding window
        self._history[identifier] = [
            t for t in self._history[identifier] if now - t < self.window_seconds
        ]

        current_count = len(self._history[identifier])
        if current_count >= limit:
            oldest = self._history[identifier][0]
            retry_after = max(1, int(self.window_seconds - (now - oldest)))
            return False, 0, retry_after

        self._history[identifier].append(now)
        remaining = max(0, limit - len(self._history[identifier]))
        return True, remaining, 0

    def reset(self, identifier: str | None = None):
        """Resets rate history for a specific key or all keys."""
        if identifier:
            self._history.pop(identifier, None)
        else:
            self._history.clear()


# Global singleton instance
rate_limiter = RateLimiter(window_seconds=60)
