from fastapi import APIRouter
from app.models.meme import MemeListResponse, Meme

router = APIRouter()

@router.get("/trending", response_model=MemeListResponse)
async def get_trending_memes():
    return MemeListResponse(
        items=[
            Meme(
                id="1",
                slug="drake-pointing",
                title="Drake Pointing",
                image_url="https://cdn.memegpt.com/memes/drake-pointing.jpg",
                tags=["popular", "decision"],
                score=0.98
            )
        ],
        total=1
    )
