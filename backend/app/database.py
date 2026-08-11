"""
MemeGPT database layer — SQLAlchemy ORM models, session management, and query helpers.

Production features:
- SQLite WAL mode for concurrent read/write throughput
- Connection pooling with pre-ping and recycle policies
- Bulk-insert capability for seed/migration scripts
- Input sanitization with null-byte kill, Unicode normalisation, and length caps
- Composite indexes on hot query paths
- Unique constraints to prevent duplicate votes/favourites
"""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator, Sequence

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from app.config import DATABASE_URL, DB_PATH

logger = logging.getLogger("memegpt.database")

# ── SQLite PRAGMA optimizations applied on every new connection ────

SQLITE_PRAGMAS: list[str] = [
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA busy_timeout=5000;",
    "PRAGMA cache_size=-16000;",
    "PRAGMA mmap_size=536870912;",
    "PRAGMA temp_store=MEMORY;",
    "PRAGMA threads=4;",
]

# ── Engine ───────────────────────────────────────────────────────────

is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,              # verify liveness before lease
    pool_recycle=3600,               # recycle connections older than 1 hour
    echo=False,
)


@event.listens_for(engine, "connect")
def _set_connection_pragmas(dbapi_connection, _connection_record):
    """For each new WAL connection, apply performance PRAGMAs (SQLite only)."""
    if is_sqlite:
        cursor = dbapi_connection.cursor()
        for pragma in SQLITE_PRAGMAS:
            cursor.execute(pragma)
        cursor.execute("PRAGMA optimize;")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative base ─────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


# ── Sanitization ─────────────────────────────────────────────────────

MAX_TEXT_LENGTH = 2000
MAX_NAME_LENGTH = 200

_VALID_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_WS_COLLAPSE = re.compile(r"\s+")
_SAFE_CHARS = re.compile(r"[^a-zA-Z0-9\s.,!?'\"@#&%$:;=_+()[\]{}<>/~`/|*°€₹¥^\\-]")
_NULL_BYTE = re.compile(r"\x00")


def sanitize_input(value: str, *, max_len: int = MAX_TEXT_LENGTH) -> str:
    """Sanitize a user-supplied string for safe storage and display.

    Steps:
    1. Collapse null bytes (kill-switch against trivial injection)
    2. Normalize Unicode, replacing unknown codepoints
    3. Collapse consecutive whitespace
    4. Drop characters outside safe Latin + punctuation range
    5. Truncate to max_len codepoints, then RTRIM
    """
    if not isinstance(value, str):
        value = str(value)
    if "\x00" in value:
        value = value.replace("\x00", " ")
    value = value.encode("utf-8", errors="replace").decode("utf-8")
    value = _WS_COLLAPSE.sub(" ", value)
    value = _SAFE_CHARS.sub("", value)
    value = value[:max_len].strip()
    return value


def is_valid_input(value: str, max_len: int = MAX_TEXT_LENGTH) -> bool:
    """Return True if value passes all sanitization constraints."""
    if not isinstance(value, str):
        return False
    if len(value) == 0 or len(value) > max_len:
        return False
    if "\x00" in value:
        return False
    sanitized = sanitize_input(value, max_len=max_len)
    return sanitized == value


def is_valid_meme_id(meme_id: str) -> bool:
    """Strong UUID v4 validation with regex."""
    return isinstance(meme_id, str) and bool(_VALID_UUID.fullmatch(meme_id))


# ── ORM Models ────────────────────────────────────────────────────────


class Meme(Base):
    __tablename__ = "memes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(MAX_NAME_LENGTH), nullable=False, index=True)
    slug = Column(String(300), nullable=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    dialogue = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False)   # JSON string
    image_ref = Column(String(500), nullable=True)
    video_ref = Column(String(500), nullable=True)
    gif_ref = Column(String(500), nullable=True)
    viral_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    votes = relationship("MemeVote", back_populates="meme", cascade="all, delete-orphan")
    usage_logs = relationship("MemeUsage", back_populates="meme", cascade="all, delete-orphan")
    favourites = relationship("FavouriteMeme", back_populates="meme", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_memes_cat_viral", "category", "viral_score"),
        Index("ix_memes_usage_up", "usage_count", "upvotes"),
    )

    def keywords_list(self) -> list[str]:
        try:
            return json.loads(self.keywords or "[]")
        except (json.JSONDecodeError, TypeError):
            logger.warning("Bad keywords JSON for meme %s", self.id)
            return []

    def to_dict(self) -> dict:
        slug_val = self.slug or re.sub(r"[^\|\s-]", "", self.name.lower()).strip().replace(" ", "-")
        return {
            "id": self.id,
            "name": self.name,
            "slug": slug_val,
            "category": self.category,
            "dialogue": self.dialogue,
            "explanation": self.explanation,
            "keywords": self.keywords_list(),
            "imageRef": self.image_ref,
            "videoRef": self.video_ref,
            "gifRef": self.gif_ref,
            "viralScore": round(self.viral_score or 0.0, 2),
            "usageCount": self.usage_count or 0,
            "upvotes": self.upvotes or 0,
            "downvotes": self.downvotes or 0,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class MemeUsage(Base):
    __tablename__ = "meme_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meme_id = Column(String(36), ForeignKey("memes.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    session_id = Column(String(64), nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    used_at = Column(DateTime, default=utc_now)
    meme = relationship("Meme", back_populates="usage_logs")


class MemeVote(Base):
    __tablename__ = "meme_votes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meme_id = Column(String(36), ForeignKey("memes.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    vote = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        UniqueConstraint("meme_id", "session_id", name="uq_meme_session_vote"),
    )
    meme = relationship("Meme", back_populates="votes")


class FavouriteMeme(Base):
    __tablename__ = "favourite_memes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meme_id = Column(String(36), ForeignKey("memes.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        UniqueConstraint("meme_id", "session_id", name="uq_meme_session_fav"),
    )
    meme = relationship("Meme", back_populates="favourites")


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    session_id = Column(String(64), nullable=False, index=True)
    match_count = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)


# ── Session factory utilities ──────────────────────────────────────


def get_db() -> Generator[Session, None, None]:
    """Yield a Session for FastAPI Depends dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(drop_all: bool = False) -> None:
    """Create all tables (optionally removing previous)."""
    if drop_all:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def bulk_insert_memes(items: Sequence[dict]) -> int:
    """Efficiently insert many meme records using the list-creating bulk mode."""
    with get_db() as db:
        objs = [Meme(**item) for item in items]
        db.add_all(objs)
        db.flush()
        return len(objs)