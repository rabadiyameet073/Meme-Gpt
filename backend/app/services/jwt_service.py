"""JWT token creation and verification for MemeGPT."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)
REFRESH_TOKEN_EXPIRE_DAYS = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if _HAS_BCRYPT:
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    if _HAS_BCRYPT:
        try:
            return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
        except Exception:
            pass
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _get_secret_key() -> str:
    return getattr(settings, "SECRET_KEY", SECRET_KEY)


def _get_algorithm() -> str:
    return getattr(settings, "JWT_ALGORITHM", ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire_minutes = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=expire_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, _get_secret_key(), algorithm=_get_algorithm())


import uuid

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire_days = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=expire_days))
    jti = to_encode.get("jti") or str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    return jwt.encode(to_encode, _get_secret_key(), algorithm=_get_algorithm())


def revoke_token_jti(jti: str) -> bool:
    """Revoke a token's jti in Redis / cache so it cannot be used again (AUTH-07)."""
    if not jti:
        return False
    from app.core.cache import cache_set
    cache_set(f"revoked_jwt:{jti}", 1, ttl=REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return True


def is_jti_revoked(jti: str) -> bool:
    """Check if token's jti is in the revoked blacklist (AUTH-07)."""
    if not jti:
        return False
    from app.core.cache import cache_get
    return cache_get(f"revoked_jwt:{jti}") is not None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[_get_algorithm()])
        jti = payload.get("jti")
        if jti and is_jti_revoked(jti):
            return None
        return payload
    except Exception:
        return None
