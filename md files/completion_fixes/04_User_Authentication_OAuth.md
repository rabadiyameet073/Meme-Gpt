# 04 — User Authentication & OAuth Guide
> Add Google/GitHub OAuth, JWT tokens, user registration, and profile management.

---

## Problem Statement

Currently the backend has:
- ✅ API key authentication (tiered: anonymous/free/pro/admin)
- ✅ JWT constants defined in `core/auth.py`
- ❌ No OAuth provider (Google, GitHub)
- ❌ No user registration / login UI
- ❌ No user profile management
- ❌ No session tokens

---

## Architecture Decision

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend auth | FastAPI + python-jose (JWT) | Already using FastAPI |
| OAuth providers | Google + GitHub via httpx | Simple, no heavy library |
| Frontend auth | NextAuth.js (in apps/web) | Spec requirement |
| Vite SPA auth | Custom JWT flow | Vite can't use NextAuth |
| Token storage | HttpOnly cookies + localStorage | Secure + accessible |

---

## Step 1: Add Dependencies

```powershell
cd "d:\Meme GPT\backend"
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

Add to `backend/requirements.txt`:
```
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

---

## Step 2: Create User Model in Database

**Add to:** `backend/app/database.py` (after the existing `Meme` class)

```python
class User(Base):
    """User accounts — supports OAuth and email/password."""
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth users

    # OAuth
    oauth_provider = Column(String(50), nullable=True)  # 'google' | 'github' | None
    oauth_id = Column(String(255), nullable=True)

    # Plan & preferences
    plan = Column(String(20), default="free")  # 'free' | 'pro' | 'team'
    preferences = Column(JSON, default=dict)   # {format_pref, nsfw, categories}

    # Rate limiting
    rate_limit = Column(Integer, default=120)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    saved_memes = relationship("SavedMeme", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_oauth", "oauth_provider", "oauth_id"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "plan": self.plan,
            "preferences": self.preferences or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
```

Run migration:
```powershell
cd "d:\Meme GPT\backend"
python -c "from app.database import Base, engine; Base.metadata.create_all(engine); print('✅ Tables created')"
```

---

## Step 3: Create JWT Token Service

**File (create new):** `backend/app/services/jwt_service.py`

```python
"""JWT token creation and verification for MemeGPT."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

SECRET_KEY = getattr(settings, "SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

## Step 4: Create OAuth Service

**File (create new):** `backend/app/services/oauth_service.py`

```python
"""OAuth provider integration for Google and GitHub."""
import httpx
import logging
from typing import Optional, Dict

from app.config import settings

logger = logging.getLogger("memegpt.oauth")

# Google OAuth
GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = getattr(settings, "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")

# GitHub OAuth
GITHUB_CLIENT_ID = getattr(settings, "GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = getattr(settings, "GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = getattr(settings, "GITHUB_REDIRECT_URI", "http://localhost:8000/api/v1/auth/github/callback")


def get_google_auth_url() -> str:
    """Generate Google OAuth consent URL."""
    return (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline"
    )


async def exchange_google_code(code: str) -> Optional[Dict]:
    """Exchange authorization code for Google user info."""
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            logger.error(f"Google token exchange failed: {token_resp.text}")
            return None

        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        # Get user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            return None

        user_info = user_resp.json()
        return {
            "provider": "google",
            "oauth_id": user_info["id"],
            "email": user_info["email"],
            "name": user_info.get("name", ""),
            "avatar_url": user_info.get("picture", ""),
        }


def get_github_auth_url() -> str:
    """Generate GitHub OAuth URL."""
    return (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={GITHUB_REDIRECT_URI}&"
        f"scope=user:email"
    )


async def exchange_github_code(code: str) -> Optional[Dict]:
    """Exchange authorization code for GitHub user info."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        if not access_token:
            return None

        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_resp.json()

        # Get email (may be private)
        email_resp = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        emails = email_resp.json()
        primary_email = next((e["email"] for e in emails if e.get("primary")), user_info.get("email", ""))

        return {
            "provider": "github",
            "oauth_id": str(user_info["id"]),
            "email": primary_email,
            "name": user_info.get("name") or user_info.get("login", ""),
            "avatar_url": user_info.get("avatar_url", ""),
        }
```

---

## Step 5: Create Auth API Routes

**File (replace):** `backend/app/api/v1/auth.py`

Add OAuth routes alongside existing API key auth:

```python
"""Authentication routes — API keys + OAuth (Google, GitHub)."""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.database import User, get_db, utc_now
from app.services.jwt_service import (
    create_access_token, create_refresh_token, decode_token,
    hash_password, verify_password,
)
from app.services.oauth_service import (
    get_google_auth_url, exchange_google_code,
    get_github_auth_url, exchange_github_code,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/google/login")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    return {"url": get_google_auth_url()}


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    user_info = await exchange_google_code(code)
    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")
    return await _oauth_login(user_info, db)


@router.get("/github/login")
async def github_login():
    """Redirect user to GitHub OAuth."""
    return {"url": get_github_auth_url()}


@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback."""
    user_info = await exchange_github_code(code)
    if not user_info:
        raise HTTPException(status_code=400, detail="GitHub authentication failed")
    return await _oauth_login(user_info, db)


async def _oauth_login(user_info: dict, db: Session) -> dict:
    """Create or find user from OAuth info, return JWT tokens."""
    user = db.query(User).filter(User.email == user_info["email"]).first()

    if not user:
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            avatar_url=user_info["avatar_url"],
            oauth_provider=user_info["provider"],
            oauth_id=user_info["oauth_id"],
            plan="free",
        )
        db.add(user)

    user.last_login = utc_now()
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.get("/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current user from JWT token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": user.to_dict()}
```

---

## Step 6: Add OAuth Config to `.env`

```env
# ── OAuth (Google) ────────────────────────────────────────────────
# GET FROM: https://console.cloud.google.com → APIs & Services → Credentials
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# ── OAuth (GitHub) ────────────────────────────────────────────────
# GET FROM: https://github.com/settings/applications/new
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback
```

---

## Step 7: Add Config Vars to `backend/app/config.py`

```python
# ── OAuth ─────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/v1/auth/github/callback")
```

---

## Verification Checklist

- [ ] `User` model exists in `database.py`
- [ ] Database migration creates `users` table
- [ ] `GET /api/v1/auth/google/login` returns OAuth URL
- [ ] `GET /api/v1/auth/github/login` returns OAuth URL
- [ ] OAuth callback creates user + returns JWT
- [ ] `GET /api/v1/auth/me` returns user profile with valid JWT
- [ ] Existing API key auth still works alongside OAuth
