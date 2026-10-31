# 08 — Auth Middleware Fix
# Fix DB-Based Tier Enforcement (Not String Matching)

> **Gap Source:** Section 6 of GAP_ANALYSIS_FULL.md  
> **Priority:** P1  
> **Files to edit:** `d:\Meme GPT\backend\app\main.py` and `d:\Meme GPT\backend\app\core\auth.py`

---

## WHAT IS BROKEN

Current middleware in `main.py` determines API tier by string matching:
```python
# BAD — anyone can pass "pro_mygeneratedkey" and get Pro limits:
if "admin" in api_key:
    tier = "internal"
elif "pro" in api_key:
    tier = "pro"
```

This is a security vulnerability. The tier should be looked up from the DB using the SHA-256 hash of the key.

---

## FIX 1 — `core/auth.py` — Real DB Tier Lookup

Add this function to `d:\Meme GPT\backend\app\core\auth.py`:

```python
import hashlib
from functools import lru_cache
from typing import Optional

from app.config import settings


def hash_api_key(raw_key: str) -> str:
    """SHA-256 hash of raw API key — this is what's stored in DB."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def lookup_api_key_tier(raw_key: str, db) -> tuple[str, bool]:
    """
    Look up API key in DB and return (tier, is_admin).
    Returns ("anonymous", False) if key not found or revoked.

    FIXED: Previously used string matching — now uses real DB lookup.
    """
    from app.database import ApiKey

    if not raw_key:
        return "anonymous", False

    key_hash = hash_api_key(raw_key)

    try:
        record = db.query(ApiKey).filter(
            ApiKey.key_hash == key_hash,
            ApiKey.revoked == False,
        ).first()

        if not record:
            return "anonymous", False

        tier = record.tier or "free"
        is_admin = tier in ("admin", "internal")
        return tier, is_admin

    except Exception as e:
        import logging
        logging.getLogger("memegpt.auth").warning(f"DB key lookup failed: {e}")
        return "free", False  # Fail open with free tier


def get_rate_limit_for_tier(tier: str) -> int:
    """Returns requests-per-minute limit for given tier."""
    limits = {
        "anonymous": getattr(settings, "RATE_LIMIT_ANONYMOUS", 60),
        "free": getattr(settings, "RATE_LIMIT_FREE", 120),
        "pro": getattr(settings, "RATE_LIMIT_PRO", 300),
        "internal": getattr(settings, "RATE_LIMIT_INTERNAL", 1000),
        "admin": getattr(settings, "RATE_LIMIT_INTERNAL", 1000),
    }
    return limits.get(tier, 60)
```

---

## FIX 2 — `main.py` — Real Middleware

Replace the rate limiting middleware in `d:\Meme GPT\backend\app\main.py`:

```python
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware — FIXED to use DB for tier lookup.
    Previously used string matching on API key content (security bug).
    """

    # Endpoints exempt from rate limiting
    EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/favicon.ico", "/api/health"}

    async def dispatch(self, request: Request, call_next):
        # Skip exempt paths
        path = request.url.path
        if any(path.startswith(p) for p in self.EXEMPT_PATHS):
            return await call_next(request)

        # Get client identifier
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.client.host
            or "unknown"
        )

        # Get API key from header
        api_key = (
            request.headers.get("x-api-key", "")
            or request.headers.get("authorization", "").removeprefix("Bearer ").strip()
        )

        # Determine tier from DB (not string matching!)
        tier = "anonymous"
        if api_key:
            try:
                from app.database import SessionLocal
                from app.core.auth import lookup_api_key_tier
                db = SessionLocal()
                try:
                    tier, is_admin = lookup_api_key_tier(api_key, db)
                finally:
                    db.close()
            except Exception:
                tier = "anonymous"

        # Get rate limit for this tier
        from app.core.auth import get_rate_limit_for_tier
        rate_limit = get_rate_limit_for_tier(tier)

        # Check rate limit using Redis-backed counter
        from app.core.cache import rate_limit_check
        identifier = api_key if api_key else client_ip
        allowed, remaining = rate_limit_check(identifier, rate_limit, window_seconds=60)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit of {rate_limit} req/min exceeded.",
                    "retry_after": 60,
                    "tier": tier,
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Tier": tier,
                },
            )

        # Add tier headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Tier"] = tier
        return response


# Register the middleware (in main.py, replace existing rate limit middleware):
app.add_middleware(RateLimitMiddleware)
```

---

## FIX 3 — Ensure `ApiKey` Model Has `key_hash` Column

In `d:\Meme GPT\backend\app\database.py`, ensure the `ApiKey` model has:

```python
class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), default="Default API Key")
    key_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256
    prefix = Column(String(20), nullable=False)  # First 8 chars of raw key
    tier = Column(String(20), default="free")    # free|pro|internal|admin
    user_id = Column(String, nullable=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, nullable=True)  # Override global tier limit

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "prefix": self.prefix,
            "tier": self.tier,
            "rate_limit": self.rate_limit or get_rate_limit_for_tier(self.tier),
            "revoked": self.revoked,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
```

---

## FIX 4 — `generate_api_key` in `core/auth.py`

Ensure key generation stores the hash:

```python
def generate_api_key(db, tier: str = "free", name: str = "Default", user_id: str = None):
    """Generate new API key, store hash in DB, return raw key once."""
    import secrets
    import uuid as _uuid

    # Generate random key
    raw_key = f"mgpt_{tier[:4]}_{secrets.token_hex(16)}"
    key_hash = hash_api_key(raw_key)
    prefix = raw_key[:12] + "..."

    from app.database import ApiKey
    record = ApiKey(
        id=str(_uuid.uuid4()),
        name=name,
        key_hash=key_hash,
        prefix=prefix,
        tier=tier,
        user_id=user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Return record + raw key (ONLY time raw key is returned)
    return record, raw_key
```

---

## VERIFICATION

```bash
# Create a test API key
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key", "tier": "free"}'

# Use the returned raw_key in next request:
curl http://localhost:8000/api/v1/search \
  -H "X-API-Key: mgpt_free_..." \
  # Response headers should show:
  # X-RateLimit-Tier: free
  # X-RateLimit-Limit: 120
```
