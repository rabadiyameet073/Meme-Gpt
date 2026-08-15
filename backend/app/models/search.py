from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemeResult(BaseModel):
    id: str
    name: str
    category: str
    dialogue: str
    explanation: str
    keywords: List[str] = []
    video_ref: Optional[str] = None
    gif_ref: Optional[str] = None
    image_ref: Optional[str] = None
    viral_score: float = 0.0
    usage_count: int = 0
    upvotes: int = 0
    downvotes: int = 0
    confidence: Optional[float] = None
    similarity_score: Optional[float] = None
    composite_score: Optional[float] = None
    emotion_match: Optional[List[str]] = None
    formats: Optional[Dict[str, Optional[str]]] = None
    preview_url: Optional[str] = None
    share_url: Optional[str] = None
    meme_type: Optional[str] = "reaction"


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language search query"
    )
    format_preference: Optional[str] = Field(
        "gif",
        description="Preferred meme format: gif, png, mp4, webp, any"
    )
    nsfw: bool = Field(False, description="Include NSFW results")
    limit: int = Field(5, ge=1, le=20, description="Number of results to return")
    session_id: Optional[str] = Field(None, description="Client session tracking ID")


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    format_preference: Optional[str] = None
    formatPreference: Optional[str] = None


class SearchResponse(BaseModel):
    success: bool = True
    query_id: str
    results: List[Dict[str, Any]]
    intent_parsed: Optional[Dict[str, Any]] = None
    response_time_ms: int = 0
    cached: bool = False
    primary: Optional[Dict[str, Any]] = None
    topFive: Optional[List[Dict[str, Any]]] = None
    bestMatch: Optional[Dict[str, Any]] = None
