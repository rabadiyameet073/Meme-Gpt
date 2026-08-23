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
from app.api.v1.security import router as security_router
from app.api.v1.privacy import router as privacy_router
from app.api.v1.validation import router as validation_router
from app.api.v1.rate_limiting import router as rate_limiting_router
from app.api.v1.deployment import router as deployment_router
from app.api.v1.project_management import router as project_management_router
from app.api.v1.troubleshooting import router as troubleshooting_router
from app.api.v1.faq import router as faq_router
from app.api.v1.mobile import router as mobile_router
from app.api.v1.references import router as references_router
from app.api.v1.marketing import router as marketing_router
from app.api.v1.appendix import router as appendix_router

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
v1_router.include_router(security_router)
v1_router.include_router(privacy_router)
v1_router.include_router(validation_router)
v1_router.include_router(rate_limiting_router)
v1_router.include_router(deployment_router)
v1_router.include_router(project_management_router)
v1_router.include_router(troubleshooting_router)
v1_router.include_router(faq_router)
v1_router.include_router(mobile_router)
v1_router.include_router(references_router)
v1_router.include_router(marketing_router)
v1_router.include_router(appendix_router)

__all__ = ["v1_router"]


