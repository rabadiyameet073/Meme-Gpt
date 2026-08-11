"""Meme Pydantic schemas — matches the full DB schema from documentation."""
from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class MemeFormats(BaseModel):
    gif: Optional[str] = None
    image: Optional[str] = None
    video: Optional[str] = None
    webp: Optional[str] = None


class MemeResult(BaseModel):
    """A single meme returned from search."""
    id: str
    name: str
    slug: str
    relevance_score: float = 0.0
    emotion_match: List[str] = []
    preview_url: Optional[str] = None
    formats: MemeFormats = MemeFormats()
    share_url: Optional[str] = None
    meme_type: str = "reaction"
    categories: List[str] = []
    emotions: List[str] = []
    nsfw: bool = False
    popularity_score: float = 0.0


class MemeDetail(BaseModel):
    """Full meme detail for GET /api/v1/memes/{slug}."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    origin: Optional[str] = None
    categories: List[str] = []
    emotions: List[str] = []
    keywords: List[str] = []
    formats: MemeFormats = MemeFormats()
    related_memes: List[str] = []
    usage_count: int = 0
    download_count: int = 0
    popularity_score: float = 0.0
    nsfw: bool = False
    source: str = "manual"
    created_at: Optional[str] = None


class MemeListResponse(BaseModel):
    items: List[MemeDetail]
    total: int
    page: int = 1
    page_size: int = 20
