"""Authentication and Authorization module for MemeGPT.
Implements Phase 1 (Anonymous), Phase 2 (Developer API Keys), and Phase 3 (RBAC).
"""
import hashlib
import logging
import secrets
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import ApiKey, SessionLocal, get_db

logger = logging.getLogger("memegpt.auth")


class AuthContext:
    """Represents the authenticated caller's security and rate-limiting context."""
    def __init__(
        self,
        tier: str = "anonymous",
        rate_limit: int = 60,
        user_id: Optional[str] = None,
        is_admin: bool = False,
        key_id: Optional[str] = None
    ):
        self.tier = tier
        self.rate_limit = rate_limit
        self.user_id = user_id
        self.is_admin = is_admin
        self.key_id = key_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "rate_limit": self.rate_limit,
            "user_id": self.user_id,
            "is_admin": self.is_admin,
            "key_id": self.key_id,
        }


# Hardcoded bootstrap keys for development / internal services
_STATIC_DEV_KEYS = {
    "memegpt_dev_demo_key": {"tier": "free", "rate_limit": 120, "is_admin": False},
    "memegpt_pro_demo_key": {"tier": "pro", "rate_limit": 300, "is_admin": False},
    "memegpt_admin_secret_key": {"tier": "admin", "rate_limit": 1000, "is_admin": True},
}


def hash_api_key(key: str) -> str:
    """Calculates SHA-256 hash of API key for secure storage and comparison."""
    return hashlib.sha256(key.strip().encode("utf-8")).hexdigest()


def generate_api_key(
    db: Session,
    tier: str = "free",
    name: str = "Default API Key",
    user_id: Optional[str] = None
) -> tuple[ApiKey, str]:
    """Generates a new API key, saves SHA-256 hash to database, and returns raw token once."""
    tier_limits = {
        "free": 120,
        "pro": 300,
        "internal": 1000,
        "admin": 1000,
    }
    rate_limit = tier_limits.get(tier.lower(), 120)

    # Key format: pk_live_<32 hex chars>
    raw_token = f"pk_live_{secrets.token_hex(16)}"
    key_hash = hash_api_key(raw_token)
    prefix = f"{raw_token[:8]}...{raw_token[-4:]}"

    api_key = ApiKey(
        key_hash=key_hash,
        name=name,
        prefix=prefix,
        tier=tier.lower(),
        rate_limit=rate_limit,
        user_id=user_id,
        revoked=False
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return api_key, raw_token


async def get_api_tier(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> AuthContext:
    """Extracts and validates API key from X-API-Key header.
    - If no key provided: returns Anonymous tier (60 req/min).
    - If key is static bootstrap key: resolves tier immediately.
    - If key in DB: checks revoked flag and returns caller tier + rate limit.
    - If key is revoked: raises 403 Forbidden.
    - If key is invalid: raises 401 Unauthorized.
    """
    if not x_api_key:
        return AuthContext(tier="anonymous", rate_limit=60, user_id=None, is_admin=False)

    key = x_api_key.strip()

    # Check static developer keys first
    if key in _STATIC_DEV_KEYS:
        info = _STATIC_DEV_KEYS[key]
        return AuthContext(
            tier=info["tier"],
            rate_limit=info["rate_limit"],
            is_admin=info.get("is_admin", False),
            key_id="static-dev-key"
        )

    # Handle direct invocations where db is not injected by FastAPI
    close_db = False
    if db is None or not isinstance(db, Session):
        db = SessionLocal()
        close_db = True

    try:
        # Check database for key_hash
        hashed = hash_api_key(key)
        record = db.query(ApiKey).filter(ApiKey.key_hash == hashed).first()

        if not record:
            # Check standard prefix fallback for local development mocking
            if key.startswith("pk_test_"):
                return AuthContext(tier="free", rate_limit=120, is_admin=False)
            raise HTTPException(status_code=401, detail="Invalid API key")

        if record.revoked:
            raise HTTPException(status_code=403, detail="API key has been revoked")

        is_admin = record.tier.lower() in ("admin", "internal")
        return AuthContext(
            tier=record.tier,
            rate_limit=record.rate_limit,
            user_id=record.user_id,
            is_admin=is_admin,
            key_id=record.id
        )
    finally:
        if close_db:
            db.close()


verify_api_key = get_api_tier


async def require_admin(auth: AuthContext = Depends(get_api_tier)) -> AuthContext:
    """RBAC dependency ensuring only Admin or Internal service tiers can access endpoint."""
    if not auth.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return auth
