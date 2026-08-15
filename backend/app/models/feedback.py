from typing import Optional
from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    meme_id: str = Field(..., description="Target meme ID")
    signal: Optional[str] = Field(
        None,
        description="Feedback signal: view, click, copy, download, share, upvote, downvote, skip"
    )
    action: Optional[str] = Field(
        None,
        description="Alternative signal field name for compatibility"
    )
    format: Optional[str] = Field("image", description="Format associated with feedback")
    session_id: Optional[str] = Field("anonymous", description="Session ID")
    query_id: Optional[str] = Field(None, description="Query ID")

    def get_signal(self) -> str:
        return self.signal or self.action or "click"


class VoteRequest(BaseModel):
    memeId: str = Field(..., description="Target meme ID")
    vote: int = Field(..., description="Vote value (+1 for upvote, -1 for downvote)")
    sessionId: str = Field(..., description="Client session identifier")


class FavoriteRequest(BaseModel):
    memeId: str = Field(..., description="Target meme ID")
    sessionId: str = Field(..., description="Client session identifier")
