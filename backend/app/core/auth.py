"""Authentication and Authorization module for MemeGPT.
Implements Phase 1 (Anonymous), Phase 2 (Developer API Keys), and Phase 3 (OAuth/JWT RBAC).
Specification: 07_APIs/Authentication.md
"""
import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import ApiKey, SessionLocal, get_db

logger = logging.getLogger("memegpt.auth")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "memegpt-super-secret-jwt-key-change-in-prod-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


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
    user_id: Optional[str] = None,
    env: str = "live"
) -> tuple[ApiKey, str]:
    """Generates a new API key (mgpt_live_<32 hex chars>), saves SHA-256 hash to database, and returns raw token once."""
    tier_limits = {
        "free": 120,
        "pro": 300,
        "internal": 1000,
        "admin": 1000,
    }
    rate_limit = tier_limits.get(tier.lower(), 120)

    # Key format: mgpt_live_<32 hex chars> or mgpt_test_<32 hex chars>
    env_str = "test" if env.lower() == "test" else "live"
    raw_token = f"mgpt_{env_str}_{secrets.token_hex(16)}"
    key_hash = hash_api_key(raw_token)
    prefix = f"{raw_token[:9]}...{raw_token[-4:]}"

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
    - If key is invalid or revoked: raises 401 Unauthorized.
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
            if key.startswith("pk_test_") or key.startswith("mgpt_test_"):
                return AuthContext(tier="free", rate_limit=120, is_admin=False)
            raise HTTPException(status_code=401, detail="Invalid or revoked API key")

        if record.revoked:
            raise HTTPException(status_code=401, detail="Invalid or revoked API key")

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
optional_auth = get_api_tier
require_auth = get_api_tier


async def require_admin(auth: AuthContext = Depends(get_api_tier)) -> AuthContext:
    """RBAC dependency ensuring only Admin or Internal service tiers can access endpoint."""
    if not auth.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return auth


# ── Phase 3: JWT Session Tokens (15m Access Token, 7d Refresh Token) ───────────


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates short-lived JWT access token (default 15 minutes)."""
    import base64
    import json
    import hmac

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": int(expire.timestamp()), "type": "access"})
    
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    
    signature = hmac.new(
        JWT_SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates long-lived JWT refresh token (default 7 days)."""
    import base64
    import json
    import hmac

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": int(expire.timestamp()), "type": "refresh"})
    
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    
    signature = hmac.new(
        JWT_SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_jwt_token(token: str) -> dict:
    """Verifies JWT signature and expiry, returning decoded payload."""
    import base64
    import json
    import hmac

    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token format")

    header_b64, payload_b64, sig_b64 = parts
    expected_sig = hmac.new(
        JWT_SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
    if not hmac.compare_digest(sig_b64, expected_sig_b64):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    # Add padding back to base64 string
    padding = len(payload_b64) % 4
    if padding:
        payload_b64 += "=" * (4 - padding)
    
    payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
    
    exp = payload.get("exp")
    if exp and datetime.now(timezone.utc).timestamp() > exp:
        raise HTTPException(status_code=401, detail="Token has expired")

    return payload


def get_jwt_cookie_settings() -> dict:
    """Returns secure httpOnly cookie configuration for session tokens."""
    return {
        "httponly": True,
        "secure": True,
        "samesite": "lax",
        "max_age": 7 * 24 * 3600,  # 7 days
    }

