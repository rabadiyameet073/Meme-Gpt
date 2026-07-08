import json
import re
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from app.config import DB_PATH


class Base(DeclarativeBase):
    pass


class Meme(Base):
    __tablename__ = "memes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    dialogue = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False)  # JSON array
    video_ref = Column(String, nullable=True)
    gif_ref = Column(String, nullable=True)
    viral_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    votes = relationship("MemeVote", back_populates="meme", cascade="all, delete-orphan")
    usage_logs = relationship("MemeUsage", back_populates="meme", cascade="all, delete-orphan")

    def keywords_list(self) -> list[str]:
        return json.loads(self.keywords or "[]")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "dialogue": self.dialogue,
            "explanation": self.explanation,
            "keywords": self.keywords_list(),
            "videoRef": self.video_ref,
            "gifRef": self.gif_ref,
            "viralScore": self.viral_score,
            "usageCount": self.usage_count,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
        }


class MemeVote(Base):
    __tablename__ = "meme_votes"
    __table_args__ = (UniqueConstraint("meme_id", "session_id", name="uq_meme_session"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meme_id = Column(String, ForeignKey("memes.id", ondelete="CASCADE"), nullable=False)
    vote = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    meme = relationship("Meme", back_populates="votes")


class MemeUsage(Base):
    __tablename__ = "meme_usage"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meme_id = Column(String, ForeignKey("memes.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    meme = relationship("Meme", back_populates="usage_logs")


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    result_count = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


HTML_TAG = re.compile(r"<[^>]*>")
SCRIPT_PATTERN = re.compile(r"javascript:|on\w+\s*=", re.I)
MAX_INPUT = 2000


def sanitize_input(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = HTML_TAG.sub("", text)
    text = SCRIPT_PATTERN.sub("", text)
    return text.strip()[:MAX_INPUT]


def is_valid_input(text: str) -> bool:
    return 3 <= len(text) <= MAX_INPUT
