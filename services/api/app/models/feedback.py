"""Feedback signal schema — valid actions from documentation."""
from pydantic import BaseModel
from typing import Optional

# Signal weights as documented
SIGNAL_WEIGHTS = {
    "view":        0.1,
    "click":       0.5,
    "copy":        1.0,
    "download":    2.0,
    "share":       3.0,
    "thumbs_up":   2.0,
    "thumbs_down": -1.0,
    "skip":        -0.3,
}

VALID_ACTIONS = set(SIGNAL_WEIGHTS.keys())


class FeedbackRequest(BaseModel):
    query_id: Optional[str] = None
    meme_id: str
    action: str   # view | click | copy | download | share | thumbs_up | thumbs_down | skip
    session_id: Optional[str] = "anonymous"
    format: Optional[str] = "gif"


class FeedbackResponse(BaseModel):
    recorded: bool = True
