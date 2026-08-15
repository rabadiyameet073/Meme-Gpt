"""MemeGPT — SQLAlchemy Implementation of MemeRepository.
Handles database interactions cleanly for SQLite (dev) and PostgreSQL (prod).
"""
import re
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import (
    SessionLocal,
    Meme,
    MemeVote,
    SearchLog,
    FavoriteMeme,
)
from app.repositories.base import MemeRepository

logger = logging.getLogger("memegpt.repository")


class SQLAlchemyMemeRepository(MemeRepository):
    """Concrete repository implementing MemeRepository via SQLAlchemy."""

    def __init__(self, db_session: Optional[Session] = None):
        self._session = db_session

    def _get_session(self) -> Session:
        if self._session is not None:
            return self._session
        return SessionLocal()

    def get_all_memes(self) -> List[Dict[str, Any]]:
        db = self._get_session()
        try:
            memes = db.query(Meme).order_by(desc(Meme.usage_count)).all()
            return [m.to_dict() for m in memes]
        except Exception as e:
            logger.error(f"Error fetching all memes: {e}")
            return []
        finally:
            if self._session is None:
                db.close()

    def get_meme_by_id(self, meme_id: str) -> Optional[Dict[str, Any]]:
        db = self._get_session()
        try:
            m = db.query(Meme).filter(Meme.id == meme_id).first()
            return m.to_dict() if m else None
        except Exception as e:
            logger.error(f"Error fetching meme by id {meme_id}: {e}")
            return None
        finally:
            if self._session is None:
                db.close()

    def get_meme_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        db = self._get_session()
        try:
            # 1. Try slug column
            m = db.query(Meme).filter(Meme.slug == slug).first()
            if m:
                return m.to_dict()

            # 2. Try matching normalized name slug
            all_memes = db.query(Meme).all()
            for item in all_memes:
                computed_slug = re.sub(r"[^\w\s-]", "", item.name.lower()).strip().replace(" ", "-")
                if computed_slug == slug or item.id == slug:
                    return item.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error fetching meme by slug {slug}: {e}")
            return None
        finally:
            if self._session is None:
                db.close()

    def search_memes(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        db = self._get_session()
        try:
            query = db.query(Meme)
            if "category" in filters and filters["category"]:
                query = query.filter(Meme.category == filters["category"])
            if not filters.get("nsfw", False):
                # safe only
                pass

            limit = filters.get("limit", 15)
            memes = query.order_by(desc(Meme.usage_count)).limit(limit).all()
            return [m.to_dict() for m in memes]
        except Exception as e:
            logger.error(f"Error searching memes with filters {filters}: {e}")
            return []
        finally:
            if self._session is None:
                db.close()

    def record_feedback(
        self,
        meme_id: str,
        action: str,
        session_id: str = "anonymous",
        format: str = "image"
    ) -> bool:
        db = self._get_session()
        try:
            meme = db.query(Meme).filter(Meme.id == meme_id).first()
            if not meme:
                return False

            if action in ("download", "copy", "share"):
                meme.usage_count = (meme.usage_count or 0) + 1
            elif action == "upvote":
                meme.upvotes = (meme.upvotes or 0) + 1
                db.add(MemeVote(meme_id=meme_id, vote=1, session_id=session_id))
            elif action == "downvote":
                meme.downvotes = (meme.downvotes or 0) + 1
                db.add(MemeVote(meme_id=meme_id, vote=-1, session_id=session_id))

            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording feedback for {meme_id}: {e}")
            db.rollback()
            return False
        finally:
            if self._session is None:
                db.close()

    def log_search(
        self,
        query_hash: str,
        result_count: int,
        latency_ms: int,
        cached: bool = False,
        emotion: str = "neutral"
    ) -> bool:
        db = self._get_session()
        try:
            log_entry = SearchLog(
                query=query_hash,
                match_count=result_count,
                latency_ms=latency_ms,
                session_id="anonymous"
            )
            db.add(log_entry)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging search {query_hash}: {e}")
            db.rollback()
            return False
        finally:
            if self._session is None:
                db.close()

    def get_trending(self, limit: int = 12, category: Optional[str] = None) -> List[Dict[str, Any]]:
        db = self._get_session()
        try:
            query = db.query(Meme)
            if category:
                query = query.filter(Meme.category == category)
            memes = query.order_by(desc(Meme.usage_count), desc(Meme.upvotes)).limit(limit).all()
            return [m.to_dict() for m in memes]
        except Exception as e:
            logger.error(f"Error fetching trending memes: {e}")
            return []
        finally:
            if self._session is None:
                db.close()

    def save_meme(self, meme_id: str, session_id: str) -> bool:
        db = self._get_session()
        try:
            existing = (
                db.query(FavoriteMeme)
                .filter(FavoriteMeme.meme_id == meme_id, FavoriteMeme.session_id == session_id)
                .first()
            )
            if existing:
                db.delete(existing)
            else:
                db.add(FavoriteMeme(meme_id=meme_id, session_id=session_id))
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error toggling favorite meme {meme_id}: {e}")
            db.rollback()
            return False
        finally:
            if self._session is None:
                db.close()


def create_repository(db_session: Optional[Session] = None) -> MemeRepository:
    """Repository factory function returning an instantiated MemeRepository."""
    return SQLAlchemyMemeRepository(db_session=db_session)
