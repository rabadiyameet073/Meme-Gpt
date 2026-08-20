from typing import Optional
from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    meme_id: str = Field(..., description="Target meme ID (e.g. meme_042)")
    query_id: Optional[str] = Field(None, description="Query identifier (e.g. q_xyz789)")
    action: Optional[str] = Field(
        None,
        description="Action signal: view, click, copy, download, share, thumbs_up, thumbs_down, skip"
    )
    signal: Optional[str] = Field(
        None,
        description="Legacy alias for action"
    )
    format: Optional[str] = Field("image", description="Format associated with feedback")
    session_id: Optional[str] = Field("anonymous", description="Client session identifier")

    def get_action(self) -> str:
        act = (self.action or self.signal or "click").lower().strip()
        if act == "upvote":
            return "thumbs_up"
        if act == "downvote":
            return "thumbs_down"
        return act

    def get_signal(self) -> str:
        return self.get_action()


class VoteRequest(BaseModel):
    memeId: str = Field(..., description="Target meme ID")
    vote: int = Field(..., description="Vote value (+1 for upvote, -1 for downvote)")
    sessionId: str = Field(..., description="Client session identifier")


class FavoriteRequest(BaseModel):
    memeId: str = Field(..., description="Target meme ID")
    sessionId: str = Field(..., description="Client session identifier")
