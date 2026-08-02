from fastapi import APIRouter
from app.models.search import SearchRequest, SearchResponse
from app.services.recommendation import recommendation_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_memes(req: SearchRequest):
    return await recommendation_service.search(req)
