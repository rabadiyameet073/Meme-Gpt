from fastapi import APIRouter
from app.models.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest):
    return FeedbackResponse(status="success", message=f"Recorded {req.action} for {req.meme_id}")
