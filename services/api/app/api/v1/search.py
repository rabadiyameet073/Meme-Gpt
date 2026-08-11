"""POST /api/v1/search — Core AI-powered meme search endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.search import SearchRequest, SearchResponse
from app.services.recommendation import recommendation_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_memes(req: SearchRequest):
    """
    AI-powered meme search.
    Input: natural language text (any length up to 2000 chars).
    Output: top-5 meme recommendations with CDN URLs and relevance scores.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    return await recommendation_service.recommend(
        user_text=req.query,
        format_pref=req.format_preference,
        nsfw=req.nsfw,
        session_id=req.session_id,
    )
