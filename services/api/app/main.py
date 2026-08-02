from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import search, memes, trending, feedback, health

app = FastAPI(
    title="MemeGPT API",
    description="AI-powered conversational meme search & recommendation engine",
    version="2.0.0",
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, tags=["Health"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(memes.router, prefix="/api/v1", tags=["Memes"])
app.include_router(trending.router, prefix="/api/v1", tags=["Trending"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])

@app.get("/")
async def root():
    return {"message": "Welcome to MemeGPT API v2.0.0", "status": "online"}
