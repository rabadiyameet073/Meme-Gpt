# 12 — Security Fixes
# NSFW Column, GDPR Query Hashing, Data Retention, JWT Secret

> **Gap Source:** Section 14 of GAP_ANALYSIS_FULL.md  
> **Priority:** P1 (some are P0 for GDPR)  
> **Files to edit:** Multiple backend files

---

## SECURITY GAPS SUMMARY

| Gap | Severity | Fix Location |
|---|---|---|
| No `nsfw` column on Meme model | HIGH | `database.py` (done in doc 02) |
| Raw query text stored (GDPR) | HIGH | `search.py` |
| No data retention auto-purge | MEDIUM | New background job |
| `SECRET_KEY` not set | HIGH | `.env` |
| Rate limit resets on restart | MEDIUM | `core/cache.py` (done in doc 04) |
| NSFW CLIP classifier missing | LOW | `image_analysis_service.py` |

---

## FIX 1 — GDPR: Hash Queries Before Storage

In `d:\Meme GPT\backend\app\api\v1\search.py`, find where `SearchLog` is created.  
Change:

```python
# BEFORE (BAD — stores raw PII query text):
search_log = SearchLog(
    id=...,
    query=user_query,         # ← RAW TEXT, GDPR violation
    result_count=len(results),
    latency_ms=elapsed_ms,
)

# AFTER (CORRECT — store only anonymized hash):
import hashlib
query_hash = hashlib.md5(user_query.strip().lower().encode()).hexdigest()

search_log = SearchLog(
    id=str(uuid.uuid4()),
    query_hash=query_hash,          # ← Only MD5 hash stored
    result_count=len(results),
    latency_ms=elapsed_ms,
    cache_hit=was_cache_hit,        # Log if result came from cache
    top_meme_id=results[0].get("id") if results else None,
    model_used="groq" if groq_used else "fallback",
    emotion_detected=detected_emotion,
)
```

---

## FIX 2 — Data Retention Auto-Purge (30-Day Policy)

**Create** `d:\Meme GPT\backend\app\jobs\retention.py`:

```python
"""
MemeGPT — Data Retention Job.
Per documentation: Search logs older than 30 days are deleted.
Run this daily via cron or startup scheduler.
"""

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("memegpt.retention")

RETENTION_DAYS = 30


def run_retention_cleanup():
    """Delete search logs and feedback older than RETENTION_DAYS."""
    from app.database import SessionLocal, SearchLog, Feedback

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    db = SessionLocal()
    try:
        # Delete old search logs (anonymized hashes — GDPR compliant to delete entirely)
        deleted_logs = (
            db.query(SearchLog)
            .filter(SearchLog.created_at < cutoff)
            .delete()
        )

        # Delete old anonymous feedback
        deleted_feedback = (
            db.query(Feedback)
            .filter(Feedback.created_at < cutoff)
            .delete()
        )

        db.commit()
        logger.info(
            f"Retention cleanup: deleted {deleted_logs} logs, "
            f"{deleted_feedback} feedback older than {RETENTION_DAYS} days"
        )
        return {"deleted_logs": deleted_logs, "deleted_feedback": deleted_feedback}

    except Exception as e:
        db.rollback()
        logger.error(f"Retention cleanup failed: {e}")
        return {"error": str(e)}
    finally:
        db.close()
```

**Schedule it in `main.py` lifespan** using APScheduler:

```python
# Add to requirements.txt:  APScheduler>=3.10.0

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.jobs.retention import run_retention_cleanup

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing startup code ...

    # Schedule retention job: runs daily at 3:00 AM
    scheduler.add_job(
        run_retention_cleanup,
        "cron",
        hour=3,
        minute=0,
        id="retention_cleanup",
    )
    scheduler.start()

    yield  # ← App is running

    scheduler.shutdown()
    # ... existing shutdown code ...
```

---

## FIX 3 — Generate and Set SECRET_KEY

```bash
cd "d:\Meme GPT\backend"
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Copy output to `.env`.

Ensure `config.py` validates SECRET_KEY at startup:

```python
# In config.py Settings class, add validator:
from pydantic import validator

@validator("SECRET_KEY")
def validate_secret_key(cls, v):
    if not v or v == "changeme" or len(v) < 32:
        import warnings
        warnings.warn(
            "SECRET_KEY is not set or too short! JWT tokens will be insecure.",
            SecurityWarning,
        )
    return v
```

---

## FIX 4 — NSFW Filter (Backend Enforcement)

The `nsfw` column has been added to the Meme model in doc 02.  
Now enforce NSFW filtering in search:

In `d:\Meme GPT\backend\app\api\v1\search.py`, ensure:

```python
# Get NSFW preference from request (default False = no NSFW)
nsfw = request.nsfw if hasattr(request, "nsfw") else False

# Pass to recommendation pipeline
results = await recommend_memes(
    user_text=query,
    format_pref=format_pref,
    nsfw=nsfw,  # ← Qdrant filter will exclude NSFW memes
)
```

Qdrant filter in `search_service.py` already handles this (see doc 03):
```python
conditions = [
    FieldCondition(key="nsfw", match=MatchValue(value=nsfw))
]
```

---

## FIX 5 — Security Headers Audit

In `d:\Meme GPT\backend\app\main.py`, verify these headers are added to all responses:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"

        # CSP — allow CDN images
        cdn_base = getattr(settings, "CDN_BASE_URL", "")
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"img-src 'self' {cdn_base} data: blob:; "
            f"script-src 'self' 'unsafe-inline'; "
            f"style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
            f"font-src 'self' fonts.gstatic.com"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## FIX 6 — Input Sanitization (Verify Existing)

Verify `sanitize_input()` in `meme_matcher.py` properly:
- Strips HTML tags
- Limits query length to 500 chars
- Removes null bytes

```python
import re

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input — remove HTML, limit length, strip nulls."""
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Limit length
    return text[:max_length]
```

---

## SECURITY CHECKLIST

After implementing all fixes, verify:

```bash
# 1. Verify SECRET_KEY is set
python -c "from app.config import settings; print('SECRET_KEY set:', bool(settings.SECRET_KEY))"

# 2. Verify no raw queries stored in DB
python -c "
import sqlite3, os
conn = sqlite3.connect('memegpt.db')
rows = conn.execute('SELECT query FROM search_logs LIMIT 5').fetchall()
print('Search log sample:', rows)
conn.close()
# Should show None or missing 'query' column, NOT raw text
"

# 3. Verify NSFW column exists
python -c "
import sqlite3
conn = sqlite3.connect('memegpt.db')
cols = [r[1] for r in conn.execute('PRAGMA table_info(memes)').fetchall()]
print('nsfw column exists:', 'nsfw' in cols)
conn.close()
"
```
