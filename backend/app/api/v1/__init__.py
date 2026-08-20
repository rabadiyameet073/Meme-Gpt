from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.search import router as search_router
from app.api.v1.memes import router as memes_router
from app.api.v1.trending import router as trending_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.auth import router as auth_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.chat import router as chat_router
from app.api.v1.collections import router as collections_router
from app.api.v1.features import router as features_router
from app.api.v1.share import router as share_router
from app.api.v1.suggestion_chips import router as chips_router
from app.api.v1.development import router as dev_router
from app.api.v1.testing import router as testing_router

v1_router = APIRouter()

# Register sub-routers
v1_router.include_router(health_router)
v1_router.include_router(search_router)
v1_router.include_router(memes_router)
v1_router.include_router(trending_router)
v1_router.include_router(feedback_router)
v1_router.include_router(auth_router)
v1_router.include_router(webhooks_router)
v1_router.include_router(chat_router)
v1_router.include_router(collections_router)
v1_router.include_router(features_router)
v1_router.include_router(share_router)
v1_router.include_router(chips_router)
v1_router.include_router(dev_router)
v1_router.include_router(testing_router)

__all__ = ["v1_router"]

