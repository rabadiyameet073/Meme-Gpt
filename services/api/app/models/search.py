from pydantic import BaseModel
from typing import List, Optional
from app.models.meme import Meme

class SearchRequest(BaseModel):
    query: str
    limit: int = 12
    format_filter: Optional[str] = None
    emotion_filter: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    parsed_intent: Optional[dict] = None
    results: List[Meme]
    total_found: int
