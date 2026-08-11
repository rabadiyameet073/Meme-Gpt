"""Search request / response schemas matching API spec."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.models.meme import MemeResult


class SearchFilters(BaseModel):
    categories: List[str] = []
    exclude_ids: List[str] = []


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    format_preference: str = "gif"   # gif | image | video | any
    nsfw: bool = False
    limit: int = Field(default=5, ge=1, le=20)
    session_id: Optional[str] = None
    filters: SearchFilters = SearchFilters()


class ParsedIntent(BaseModel):
    emotion: str = "neutral"
    situation: str = ""
    tone: str = "humorous"
    keywords: List[str] = []
    meme_format: str = "reaction"


class SearchResponse(BaseModel):
    success: bool = True
    query_id: str = ""
    results: List[MemeResult] = []
    intent_parsed: Optional[ParsedIntent] = None
    response_time_ms: int = 0
    cached: bool = False
