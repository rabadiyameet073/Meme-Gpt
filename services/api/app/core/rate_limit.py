"""
Token-bucket rate limiting.
60 req/min per IP (unauthenticated), 300/min (authenticated).
"""
import time
from collections import defaultdict
from typing import Dict, List


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, window_seconds: int = 60):
        self.rpm = requests_per_minute
        self.window = window_seconds
        self._buckets: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        bucket = self._buckets[client_ip]
        # Remove timestamps outside the window
        self._buckets[client_ip] = [t for t in bucket if now - t < self.window]
        if len(self._buckets[client_ip]) >= self.rpm:
            return False
        self._buckets[client_ip].append(now)
        return True

    def remaining(self, client_ip: str) -> int:
        now = time.time()
        bucket = [t for t in self._buckets.get(client_ip, []) if now - t < self.window]
        return max(0, self.rpm - len(bucket))

    def reset_time(self, client_ip: str) -> int:
        """Seconds until the oldest request expires."""
        now = time.time()
        bucket = [t for t in self._buckets.get(client_ip, []) if now - t < self.window]
        if not bucket:
            return 0
        return int(self.window - (now - min(bucket)))


rate_limiter = RateLimiter(requests_per_minute=60)
