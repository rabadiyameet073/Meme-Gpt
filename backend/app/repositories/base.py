"""MemeGPT — Repository Pattern Contract Interface.
Matches specifications from 03_Backend/Repository_Pattern.md.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class MemeRepository(ABC):
    """Abstract base repository defining data access methods for memes and analytics."""

    @abstractmethod
    def get_all_memes(self) -> List[Dict[str, Any]]:
        """Return all memes with their metadata as plain dicts."""
        pass

    @abstractmethod
    def get_meme_by_id(self, meme_id: str) -> Optional[Dict[str, Any]]:
        """Get single meme by UUID. Returns None if not found."""
        pass

    @abstractmethod
    def get_meme_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get single meme by URL-friendly slug or name."""
        pass

    @abstractmethod
    def search_memes(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and search memes by metadata attributes."""
        pass

    @abstractmethod
    def record_feedback(
        self,
        meme_id: str,
        action: str,
        session_id: str = "anonymous",
        format: str = "image"
    ) -> bool:
        """Record user interactions (download, copy, upvote, downvote, share)."""
        pass

    @abstractmethod
    def log_search(
        self,
        query_hash: str,
        result_count: int,
        latency_ms: int,
        cached: bool = False,
        emotion: str = "neutral"
    ) -> bool:
        """Log search performance and query hash for trending analytics."""
        pass

    @abstractmethod
    def get_trending(self, limit: int = 12, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return trending memes based on usage counts and upvotes."""
        pass

    @abstractmethod
    def save_meme(self, meme_id: str, session_id: str) -> bool:
        """Save a meme to user session favorites."""
        pass
