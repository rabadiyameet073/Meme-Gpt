"""JWT token creation and verification for MemeGPT."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

SECRET_KEY = getattr(settings, "SECRET_KEY", "change-me-in-production")
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


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire_days = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=expire_days))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, _get_secret_key(), algorithm=_get_algorithm())


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[_get_algorithm()])
        return payload
    except Exception:
        return None
