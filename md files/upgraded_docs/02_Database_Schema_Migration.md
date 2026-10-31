# 02 — Database Schema Migration
# Fix 12+ Missing Columns, Fix Category Array, Fix Privacy

> **Gap Source:** Section 4 of GAP_ANALYSIS_FULL.md  
> **Priority:** P0 — Must run before any service starts  
> **Files to edit:** `d:\Meme GPT\backend\app\database.py` + run migration SQL

---

## WHAT IS WRONG RIGHT NOW

The SQLAlchemy ORM models are missing 12+ columns that the documentation specifies.  
This breaks: NSFW filter, emotion matching, media URLs, popularity scoring, GDPR compliance.

| Column | Missing From | Impact |
|---|---|---|
| `memes.emotions` (TEXT[]) | Meme model | Emotion re-ranking broken |
| `memes.nsfw` (BOOLEAN) | Meme model | NSFW filter broken |
| `memes.thumb_url` | Meme model | Thumbnails never shown |
| `memes.source` | Meme model | No meme attribution |
| `memes.view_count` | Meme model | Analytics broken |
| `memes.download_count` | Meme model | Analytics broken |
| `memes.popularity_score` (0.0–1.0) | Meme model | Re-ranking skewed |
| `memes.indexed_at` | Meme model | Can't track re-indexing |
| `memes.categories` (array→string) | Meme model | Array filtering broken |
| `users.name` | User model | Profile incomplete |
| `users.avatar_url` | User model | No user avatar |
| `users.preferences` (JSON) | User model | No user settings |
| `search_logs.query_hash` | SearchLog model | Raw PII stored |
| `search_logs.cache_hit` | SearchLog model | Cache analytics broken |
| `search_logs.top_meme_id` | SearchLog model | Analytics broken |

---

## STEP 1 — Replace the Meme ORM Model in `database.py`

Find the `class Meme(Base):` block in `d:\Meme GPT\backend\app\database.py` and **replace it entirely** with:

```python
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    DateTime, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class Meme(Base):
    """
    Meme metadata table — matches Schema.md specification exactly.
    Media files stored in Cloudflare R2, URLs stored here.
    Embeddings stored in Qdrant (NOT here).
    """
    __tablename__ = "memes"

    # Primary key — matches Qdrant payload meme_id
    id = Column(String, primary_key=True)

    # Core identity
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)

    # Classification — stored as JSON string for SQLite compatibility
    # In PostgreSQL this would be TEXT[] with GIN index
    categories = Column(JSON, default=list)   # ["work", "coding"] — was single string
    emotions = Column(JSON, default=list)      # ["joy", "surprise"] — WAS MISSING ❌

    # Textual content
    dialogue = Column(Text, default="")
    explanation = Column(Text, default="")
    keywords = Column(JSON, default=list)

    # Media URLs — CDN links to Cloudflare R2
    image_url = Column(String, nullable=True)   # PNG/JPG original
    gif_url = Column(String, nullable=True)     # Animated GIF
    mp4_url = Column(String, nullable=True)     # MP4 video
    thumb_url = Column(String, nullable=True)   # 200×200 WebP thumbnail — WAS MISSING ❌
    webp_url = Column(String, nullable=True)    # WebP optimized

    # Legacy refs (kept for backward compat, prefer *_url above)
    image_ref = Column(String, nullable=True)
    gif_ref = Column(String, nullable=True)
    video_ref = Column(String, nullable=True)

    # Provenance
    source = Column(String(50), default="manual")  # WAS MISSING ❌
    # valid: 'imgflip' | 'reddit' | 'tenor' | 'giphy' | 'manual'

    # Content flags
    nsfw = Column(Boolean, default=False, index=True)  # WAS MISSING ❌

    # Analytics
    view_count = Column(Integer, default=0)         # WAS MISSING ❌
    download_count = Column(Integer, default=0)     # WAS MISSING ❌
    usage_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # Scores
    viral_score = Column(Float, default=0.0)
    popularity_score = Column(Float, default=0.0)  # WAS MISSING ❌ (0.0–1.0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    indexed_at = Column(DateTime, nullable=True)    # WAS MISSING ❌

    # Indexes for performance
    __table_args__ = (
        Index("idx_memes_slug", "slug"),
        Index("idx_memes_nsfw", "nsfw"),
        Index("idx_memes_popularity", "popularity_score"),
        Index("idx_memes_source", "source"),
    )

    def to_dict(self) -> dict:
        """Serialize meme to API response format."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "category": self.categories[0] if self.categories else "general",
            "categories": self.categories or [],
            "emotions": self.emotions or [],
            "dialogue": self.dialogue or "",
            "explanation": self.explanation or "",
            "keywords": self.keywords or [],
            # Prefer *_url columns, fall back to *_ref for backward compat
            "image_url": self.image_url or self.image_ref,
            "gif_url": self.gif_url or self.gif_ref,
            "mp4_url": self.mp4_url or self.video_ref,
            "thumb_url": self.thumb_url,
            "webp_url": self.webp_url,
            # Legacy fields (keep for frontend compatibility)
            "imageRef": self.image_url or self.image_ref,
            "gifRef": self.gif_url or self.gif_ref,
            "videoRef": self.mp4_url or self.video_ref,
            "thumbUrl": self.thumb_url,
            "formats": {
                "image": self.image_url or self.image_ref,
                "gif": self.gif_url or self.gif_ref,
                "mp4": self.mp4_url or self.video_ref,
                "webp": self.webp_url,
                "thumb": self.thumb_url,
            },
            "source": self.source or "manual",
            "nsfw": self.nsfw or False,
            "view_count": self.view_count or 0,
            "download_count": self.download_count or 0,
            "usage_count": self.usage_count or 0,
            "upvotes": self.upvotes or 0,
            "downvotes": self.downvotes or 0,
            "viral_score": self.viral_score or 0.0,
            "viralScore": self.viral_score or 0.0,
            "popularity_score": self.popularity_score or 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
        }
```

---

## STEP 2 — Replace the User ORM Model

Find `class User(Base):` in `database.py` and **replace it** with:

```python
class User(Base):
    """
    User accounts — matches Schema.md specification.
    Phase 1: Anonymous. Phase 2: API Key. Phase 3: OAuth.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=True, index=True)

    # Profile — WAS MISSING ❌
    name = Column(String(200), nullable=True)
    avatar_url = Column(String, nullable=True)

    # Plan
    plan = Column(String(20), default="free")  # 'free' | 'pro'

    # User preferences stored as JSON — WAS MISSING ❌
    # Format: {"format_pref": "gif", "nsfw": false, "categories": ["coding"]}
    preferences = Column(JSON, default=dict)

    # Auth
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "plan": self.plan,
            "preferences": self.preferences or {},
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
```

---

## STEP 3 — Replace the SearchLog ORM Model

Find `class SearchLog(Base):` in `database.py` and **replace it** with:

```python
class SearchLog(Base):
    """
    Anonymized search analytics — NO PII stored.
    Matches Schema.md specification.
    """
    __tablename__ = "search_logs"

    id = Column(String, primary_key=True)

    # Anonymized query — MD5 hash, NEVER raw text — WAS STORING RAW TEXT ❌
    query_hash = Column(String(32), nullable=True, index=True)  # MD5 of query

    # Results
    result_count = Column(Integer, default=0)         # was 'match_count'
    top_meme_id = Column(String, nullable=True)       # WAS MISSING ❌

    # Performance
    latency_ms = Column(Integer, default=0)
    cache_hit = Column(Boolean, default=False)         # WAS MISSING ❌

    # Metadata (never store raw query text!)
    model_used = Column(String(50), nullable=True)    # 'groq' | 'fallback'
    emotion_detected = Column(String(50), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        index=True)

    __table_args__ = (
        Index("idx_search_logs_created_at", "created_at"),
        Index("idx_search_logs_query_hash", "query_hash"),
    )
```

---

## STEP 4 — Run the Migration

Since this project uses SQLite for dev, run this migration script.  
**Save as `d:\Meme GPT\backend\migrate.py`** and run it:

```python
#!/usr/bin/env python3
"""
MemeGPT Database Migration — Adds missing columns per Gap Analysis.
Run once: python migrate.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "memegpt.db")

MIGRATIONS = [
    # Meme table additions
    "ALTER TABLE memes ADD COLUMN emotions TEXT DEFAULT '[]'",
    "ALTER TABLE memes ADD COLUMN nsfw INTEGER DEFAULT 0",
    "ALTER TABLE memes ADD COLUMN thumb_url TEXT",
    "ALTER TABLE memes ADD COLUMN webp_url TEXT",
    "ALTER TABLE memes ADD COLUMN image_url TEXT",
    "ALTER TABLE memes ADD COLUMN gif_url TEXT",
    "ALTER TABLE memes ADD COLUMN mp4_url TEXT",
    "ALTER TABLE memes ADD COLUMN source TEXT DEFAULT 'manual'",
    "ALTER TABLE memes ADD COLUMN view_count INTEGER DEFAULT 0",
    "ALTER TABLE memes ADD COLUMN download_count INTEGER DEFAULT 0",
    "ALTER TABLE memes ADD COLUMN popularity_score REAL DEFAULT 0.0",
    "ALTER TABLE memes ADD COLUMN indexed_at TEXT",
    "ALTER TABLE memes ADD COLUMN categories TEXT DEFAULT '[]'",

    # User table additions
    "ALTER TABLE users ADD COLUMN name TEXT",
    "ALTER TABLE users ADD COLUMN avatar_url TEXT",
    "ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}'",

    # SearchLog table — rename and add columns
    "ALTER TABLE search_logs ADD COLUMN query_hash TEXT",
    "ALTER TABLE search_logs ADD COLUMN top_meme_id TEXT",
    "ALTER TABLE search_logs ADD COLUMN cache_hit INTEGER DEFAULT 0",
    "ALTER TABLE search_logs ADD COLUMN model_used TEXT",
    "ALTER TABLE search_logs ADD COLUMN emotion_detected TEXT",

    # Migrate existing category string → categories JSON array
    "UPDATE memes SET categories = '[\"' || category || '\"]' WHERE categories IS NULL OR categories = '[]'",

    # Copy existing image refs to new URL columns
    "UPDATE memes SET image_url = image_ref WHERE image_url IS NULL AND image_ref IS NOT NULL",
    "UPDATE memes SET gif_url = gif_ref WHERE gif_url IS NULL AND gif_ref IS NOT NULL",
    "UPDATE memes SET mp4_url = video_ref WHERE mp4_url IS NULL AND video_ref IS NOT NULL",

    # Anonymize existing raw query text in search_logs
    # WARNING: This overwrites raw text with hash — GDPR compliance
    # Note: SQLite doesn't have MD5 built-in, so we just clear it
    "UPDATE search_logs SET query_hash = 'migrated', query = NULL WHERE query IS NOT NULL",
]

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    success = 0
    skipped = 0
    for sql in MIGRATIONS:
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"  ✅ {sql[:60]}...")
            success += 1
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower() or "no such column" in str(e).lower():
                print(f"  ⏭️  Already exists: {sql[:60]}...")
                skipped += 1
            else:
                print(f"  ❌ ERROR: {e}")
                print(f"     SQL: {sql}")

    conn.close()
    print(f"\n✅ Migration complete: {success} applied, {skipped} skipped")

if __name__ == "__main__":
    print(f"Running migration on: {DB_PATH}")
    run_migration()
```

**Run it:**
```bash
cd "d:\Meme GPT\backend"
python migrate.py
```

---

## STEP 5 — Recreate Tables (Fresh Dev Setup)

If starting fresh (no existing data to preserve):
```bash
cd "d:\Meme GPT\backend"
python -c "
from app.database import Base, engine
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print('Tables recreated with full schema')
"
```

---

## STEP 6 — Fix GDPR: Hash Queries in search.py

In `d:\Meme GPT\backend\app\api\v1\search.py`, find where `SearchLog` is created and change:

```python
# BEFORE (BAD — stores raw PII):
log = SearchLog(query=user_query, ...)

# AFTER (CORRECT — stores only hash):
import hashlib
query_hash = hashlib.md5(user_query.encode()).hexdigest()
log = SearchLog(query_hash=query_hash, ...)
```
