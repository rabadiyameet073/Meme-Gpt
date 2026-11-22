"""Authentication and Authorization module for MemeGPT.
Implements Phase 1 (Anonymous), Phase 2 (Developer API Keys), and Phase 3 (OAuth/JWT RBAC).
Specification: 07_APIs/Authentication.md, 08_Auth_Middleware_Fix.md
"""
import hashlib
import logging
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from fastapi import Header, HTTPException, Depends, Request, Cookie
from sqlalchemy.orm import Session

from app.database import ApiKey, SessionLocal, get_db, User
from app.config import settings

logger = logging.getLogger("memegpt.auth")

# JWT configuration
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)
REFRESH_TOKEN_EXPIRE_DAYS = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)


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

    @property
    def is_authenticated(self) -> bool:
        return self.tier != "anonymous" or self.user_id is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "rate_limit": self.rate_limit,
            "user_id": self.user_id,
            "is_admin": self.is_admin,
            "key_id": self.key_id,
        }


# Non-production environments where bootstrap keys may be honoured.
_DEV_ENVIRONMENTS = {"development", "dev", "local", "test", "testing", "ci"}


def _load_bootstrap_keys() -> Dict[str, Dict[str, Any]]:
    """Bootstrap API keys supplied exclusively through environment variables.

    No credential is ever baked into source. Values are read from
    ``BOOTSTRAP_{ADMIN,PRO,DEMO}_API_KEY`` and are honoured only when the app
    runs in a non-production environment, so a key copied out of a repository
    cannot be replayed against a deployed instance (AUDIT-REPORT S-1).
    """
    app_env = str(getattr(settings, "APP_ENV", "development") or "development").lower()
    if app_env not in _DEV_ENVIRONMENTS:
        return {}

    specs = (
        ("BOOTSTRAP_ADMIN_API_KEY", "admin", 1000, True),
        ("BOOTSTRAP_PRO_API_KEY", "pro", 300, False),
        ("BOOTSTRAP_DEMO_API_KEY", "free", 120, False),
    )
    keys: Dict[str, Dict[str, Any]] = {}
    for env_name, tier, limit, is_admin in specs:
        raw = (os.getenv(env_name) or "").strip()
        if raw:
            keys[raw] = {"tier": tier, "rate_limit": limit, "is_admin": is_admin}
    return keys


_STATIC_DEV_KEYS = _load_bootstrap_keys()


def get_bootstrap_keys_status() -> Dict[str, Any]:
    """Report whether bootstrap keys are active, without revealing them."""
    env = str(getattr(settings, "APP_ENV", "development") or "development").lower()
    return {
        "active": bool(_STATIC_DEV_KEYS),
        "environment": env,
        "count": len(_STATIC_DEV_KEYS),
        "source": "environment" if _STATIC_DEV_KEYS else "none",
    }


def hash_api_key(key: str) -> str:
    """Calculates SHA-256 hash of API key for secure storage and comparison."""
    return hashlib.sha256(key.strip().encode("utf-8")).hexdigest()


def get_rate_limit_for_tier(tier: str, route_type: str = "general") -> int:
    """Returns requests-per-minute limit for given tier and route type (API-11, API-12)."""
    tier_lower = (tier or "anonymous").lower()
    if route_type == "search":
        limits = {
            "anonymous": getattr(settings, "SEARCH_LIMIT_ANONYMOUS", 30),
            "free": getattr(settings, "SEARCH_LIMIT_FREE", 100),
            "pro": getattr(settings, "SEARCH_LIMIT_PRO", 500),
            "internal": getattr(settings, "SEARCH_LIMIT_INTERNAL", 1000),
            "admin": getattr(settings, "SEARCH_LIMIT_INTERNAL", 1000),
        }
        return limits.get(tier_lower, 30)
    elif route_type == "feedback":
        return getattr(settings, "FEEDBACK_LIMIT_PER_MINUTE", 120)

    limits = {
        "anonymous": getattr(settings, "RATE_LIMIT_ANONYMOUS", 60),
        "free": getattr(settings, "RATE_LIMIT_FREE", 300),
        "pro": getattr(settings, "RATE_LIMIT_PRO", 1000),
        "internal": getattr(settings, "RATE_LIMIT_INTERNAL", 2000),
        "admin": getattr(settings, "RATE_LIMIT_INTERNAL", 2000),
    }
    return limits.get(tier_lower, 60)


def lookup_api_key_tier(raw_key: str, db: Session) -> tuple[str, bool]:
    """
    Look up API key in DB and return (tier, is_admin).
    Returns ("anonymous", False) if key not found or revoked.
    """
    if not raw_key:
        return "anonymous", False

    key = raw_key.strip()
    if key in _STATIC_DEV_KEYS:
        info = _STATIC_DEV_KEYS[key]
        return info["tier"], info.get("is_admin", False)

    key_hash = hash_api_key(key)

    try:
        record = db.query(ApiKey).filter(
            ApiKey.key_hash == key_hash,
            ApiKey.revoked == False,
        ).first()

        if not record:
            app_env = str(getattr(settings, "APP_ENV", "development") or "development").lower()
            if (key.startswith("pk_test_") or key.startswith("mgpt_test_")) and app_env in _DEV_ENVIRONMENTS:
                return "free", False
            return "anonymous", False

        tier = record.tier or "free"
        is_admin = tier.lower() in ("admin", "internal")
        return tier, is_admin

    except Exception as e:
        logger.warning(f"DB key lookup failed: {e}")
        return "free", False


_KEY_TIER_CACHE: Dict[str, Tuple[str, bool, float]] = {}


def invalidate_api_key_cache(raw_key: Optional[str] = None):
    """Invalidate cached API key tiers in memory and Redis on creation or revocation."""
    global _KEY_TIER_CACHE
    if raw_key:
        clean_k = raw_key.strip()
        _KEY_TIER_CACHE.pop(clean_k, None)
        try:
            from app.core.cache import get_redis_client
            rc = get_redis_client()
            if rc:
                rc.delete(f"apikey_tier:{hash_api_key(clean_k)}")
        except Exception:
            pass
    else:
        _KEY_TIER_CACHE.clear()
        try:
            from app.core.cache import cache_flush_pattern
            cache_flush_pattern("apikey_tier:*")
        except Exception:
            pass


def get_cached_api_key_tier(raw_key: str, db: Optional[Session] = None) -> tuple[str, bool]:
    """
    O(1) cached lookup of API key tier and admin status (BE-08).
    Avoids opening per-request database sessions on the hot path.
    Uses memory LRU + Redis TTL cache.
    """
    if not raw_key:
        return "anonymous", False

    key = raw_key.strip()
    if key in _STATIC_DEV_KEYS:
        info = _STATIC_DEV_KEYS[key]
        return info["tier"], info.get("is_admin", False)

    app_env = str(getattr(settings, "APP_ENV", "development") or "development").lower()
    if (key.startswith("pk_test_") or key.startswith("mgpt_test_")) and app_env in _DEV_ENVIRONMENTS:
        return "free", False

    now = time.time()
    cached = _KEY_TIER_CACHE.get(key)
    if cached and now < cached[2]:
        return cached[0], cached[1]

    # Check Redis for distributed cache across multi-worker instances
    try:
        from app.core.cache import get_redis_client
        rc = get_redis_client()
        if rc:
            h = hash_api_key(key)
            redis_val = rc.get(f"apikey_tier:{h}")
            if redis_val:
                import json
                parsed = json.loads(redis_val if isinstance(redis_val, str) else redis_val.decode("utf-8"))
                tier, is_admin = parsed["tier"], parsed["is_admin"]
                _KEY_TIER_CACHE[key] = (tier, is_admin, now + 300.0)
                return tier, is_admin
    except Exception:
        pass

    close_db = False
    if db is None:
        from app.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        tier, is_admin = lookup_api_key_tier(key, db)
        _KEY_TIER_CACHE[key] = (tier, is_admin, now + 300.0)  # 5 min TTL
        if len(_KEY_TIER_CACHE) > 2000:
            expired = [k for k, v in _KEY_TIER_CACHE.items() if now >= v[2]]
            for k in expired:
                _KEY_TIER_CACHE.pop(k, None)

        # Store in Redis
        try:
            from app.core.cache import get_redis_client
            rc = get_redis_client()
            if rc:
                import json
                h = hash_api_key(key)
                rc.setex(f"apikey_tier:{h}", 300, json.dumps({"tier": tier, "is_admin": is_admin}))
        except Exception:
            pass

        return tier, is_admin
    finally:
        if close_db:
            db.close()


def generate_api_key(
    db: Session,
    tier: str = "free",
    name: str = "Default API Key",
    user_id: Optional[str] = None,
    env: str = "live"
) -> tuple[ApiKey, str]:
    """Generates a new API key (mgpt_live_<32 hex chars>), saves SHA-256 hash to database, and returns raw token once."""
    rate_limit = get_rate_limit_for_tier(tier)

    env_str = "test" if env.lower() == "test" else "live"
    raw_token = f"mgpt_{env_str}_{secrets.token_hex(16)}"
    key_hash = hash_api_key(raw_token)
    prefix = f"{raw_token[:9]}...{raw_token[-4:]}"

    api_key = ApiKey(
        id=str(secrets.token_hex(8)),
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

    invalidate_api_key_cache(raw_token)
    return api_key, raw_token


async def get_api_tier(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> AuthContext:
    """Extracts and validates credentials from X-API-Key header, Authorization Bearer, or cookie."""
    if isinstance(x_api_key, str) and x_api_key.strip():
        key = x_api_key.strip()

        if key in _STATIC_DEV_KEYS:
            info = _STATIC_DEV_KEYS[key]
            return AuthContext(
                tier=info["tier"],
                rate_limit=info["rate_limit"],
                is_admin=info.get("is_admin", False),
                key_id="static-dev-key"
            )

        close_db = False
        if db is None or not isinstance(db, Session):
            db = SessionLocal()
            close_db = True

        try:
            hashed = hash_api_key(key)
            record = db.query(ApiKey).filter(ApiKey.key_hash == hashed).first()

            if not record:
                app_env = str(getattr(settings, "APP_ENV", "development") or "development").lower()
                if (key.startswith("pk_test_") or key.startswith("mgpt_test_")) and app_env in _DEV_ENVIRONMENTS:
                    return AuthContext(tier="free", rate_limit=120, is_admin=False)
                raise HTTPException(status_code=401, detail="Invalid or revoked API key")

            if record.revoked:
                raise HTTPException(status_code=401, detail="Invalid or revoked API key")

            is_admin = record.tier.lower() in ("admin", "internal")
            return AuthContext(
                tier=record.tier,
                rate_limit=record.rate_limit or get_rate_limit_for_tier(record.tier),
                user_id=record.user_id,
                is_admin=is_admin,
                key_id=record.id
            )
        finally:
            if close_db:
                db.close()

    # If no X-API-Key provided, inspect JWT Authorization header or access_token cookie
    raw_jwt = None
    if isinstance(authorization, str) and authorization.strip().lower().startswith("bearer "):
        raw_jwt = authorization.strip()[7:].strip()
    elif isinstance(access_token_cookie, str) and access_token_cookie.strip():
        raw_jwt = access_token_cookie.strip()

    if raw_jwt:
        try:
            from app.services.jwt_service import decode_token
            payload = decode_token(raw_jwt)
            if payload and "sub" in payload:
                user_id = str(payload["sub"])
                close_db = False
                if db is None or not isinstance(db, Session):
                    db = SessionLocal()
                    close_db = True
                try:
                    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
                    if user:
                        is_admin = bool(user.is_admin or (user.plan and user.plan.lower() in ("admin", "internal")))
                        return AuthContext(
                            tier=user.plan or "free",
                            rate_limit=user.rate_limit or get_rate_limit_for_tier(user.plan or "free"),
                            user_id=user.id,
                            is_admin=is_admin,
                            key_id=None
                        )
                finally:
                    if close_db:
                        db.close()
        except Exception as e:
            logger.debug(f"JWT decode error in get_api_tier: {e}")

    return AuthContext(tier="anonymous", rate_limit=60, user_id=None, is_admin=False)


verify_api_key = get_api_tier
optional_auth = get_api_tier


async def require_auth(auth: AuthContext = Depends(get_api_tier)) -> AuthContext:
    """RBAC dependency requiring an authenticated caller (API key or JWT)."""
    if not auth.is_authenticated:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth

require_user = require_auth


async def require_admin(auth: AuthContext = Depends(get_api_tier)) -> AuthContext:
    """RBAC dependency ensuring only Admin or Internal service tiers can access endpoint."""
    if not auth.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return auth


from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def verify_jwt_token(token: str) -> dict:
    """Verifies JWT signature and expiry, returning decoded payload."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_jwt_cookie_settings() -> dict:
    """Returns secure httpOnly cookie configuration for session tokens."""
    return {
        "httponly": True,
        "secure": True,
        "samesite": "lax",
        "max_age": 7 * 24 * 3600,
    }


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Any:
    """FastAPI dependency to extract current User from Bearer token or session cookie."""
    from app.database import User
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token", "").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated: Bearer token required")

    payload = None
    try:
        from app.services.jwt_service import decode_token
        payload = decode_token(token)
    except Exception:
        pass

    if not payload:
        try:
            payload = verify_jwt_token(token)
        except Exception:
            pass

    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
