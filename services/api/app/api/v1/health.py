"""GET /health — Service health check (no auth required, no rate limit)."""
from fastapi import APIRouter
from app.core.cache import cache_service
from app.services.embedding import embedding_service
from app.services.search_service import search_service

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MemeGPT API",
        "version": "2.0.0",
        "models": {
            "text_embedding": embedding_service._model_loaded,
            "emotion_detection": embedding_service._emotion_loaded,
        },
        "cache": {
            "connected": cache_service.is_connected,
        },
        "vector_db": {
            "connected": search_service._qdrant is not None,
            "local_index_size": len(search_service._local_index),
        },
    }
