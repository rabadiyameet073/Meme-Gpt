from fastapi import APIRouter

router = APIRouter()

@app_router := router
@app_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MemeGPT API",
        "version": "2.0.0"
    }
