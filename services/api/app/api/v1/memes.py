from fastapi import APIRouter, HTTPException
from app.models.meme import Meme

router = APIRouter()

@router.get("/memes/{slug}", response_model=Meme)
async def get_meme(slug: str):
    # Stub response for meme detail
    return Meme(
        id="1",
        slug=slug,
        title=f"Meme for {slug}",
        image_url="https://cdn.memegpt.com/memes/drake-pointing.jpg",
        tags=["trending", "humor"],
        emotion="funny",
        format="png",
        score=0.95
    )
