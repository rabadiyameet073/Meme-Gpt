from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemeSchema(BaseModel):
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
    slug: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CreateMemeRequest(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    dialogue: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)
    keywords: List[str] = Field(default_factory=list)
    videoRef: Optional[str] = None
    gifRef: Optional[str] = None
    imageRef: Optional[str] = None


class ExportRequest(BaseModel):
    query: str
    format: str = Field(..., pattern="^(txt|json|markdown)$")
    result: Dict[str, Any]
