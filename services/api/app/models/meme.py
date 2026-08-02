from pydantic import BaseModel
from typing import List, Optional

class Meme(BaseModel):
    id: str
    slug: str
    title: str
    image_url: str
    thumbnail_url: Optional[str] = None
    tags: List[str] = []
    emotion: Optional[str] = None
    format: str = "png"
    score: float = 0.0

class MemeListResponse(BaseModel):
    items: List[Meme]
    total: int
    page: int = 1
