from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    meme_id: str
    query: str
    action: str  # "click", "copy", "favorite", "downvote"
    rating: float = 1.0

class FeedbackResponse(BaseModel):
    status: str = "success"
    message: str = "Feedback recorded"
