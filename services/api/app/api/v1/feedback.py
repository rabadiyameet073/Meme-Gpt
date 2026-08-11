"""POST /api/v1/feedback — Record user interaction signals."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.feedback import FeedbackRequest, FeedbackResponse, VALID_ACTIONS

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Record a user interaction signal.
    Valid actions: view | click | copy | download | share | thumbs_up | thumbs_down | skip
    """
    if req.action not in VALID_ACTIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid action '{req.action}'. Valid: {sorted(VALID_ACTIONS)}"
        )
    background_tasks.add_task(_record_signal, req.meme_id, req.action)
    return FeedbackResponse(recorded=True)


def _record_signal(meme_id: str, action: str) -> None:
    """Background task: update popularity score based on action weight."""
    from app.models.feedback import SIGNAL_WEIGHTS
    from app.core.cache import cache_service
    try:
        weight = SIGNAL_WEIGHTS.get(action, 0)
        if weight != 0:
            key = f"feedback:{meme_id}:score"
            current = cache_service.get(key) or 0.0
            cache_service.set(key, current + weight, ttl=604800)  # 7 days
    except Exception:
        pass
