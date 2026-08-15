from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.search import router as search_router
from app.api.v1.memes import router as memes_router
from app.api.v1.trending import router as trending_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.auth import router as auth_router

v1_router = APIRouter()

# Register sub-routers
v1_router.include_router(health_router)
v1_router.include_router(search_router)
v1_router.include_router(memes_router)
v1_router.include_router(trending_router)
v1_router.include_router(feedback_router)
v1_router.include_router(auth_router)

__all__ = ["v1_router"]
