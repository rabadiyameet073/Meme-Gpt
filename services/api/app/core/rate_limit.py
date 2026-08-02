# Token bucket rate limiting middleware stub
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute

    async def is_allowed(self, client_ip: str) -> bool:
        return True

rate_limiter = RateLimiter()
