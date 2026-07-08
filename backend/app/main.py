import json
import time
from collections import defaultdict
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import (
    Meme,
    MemeUsage,
    MemeVote,
    SearchLog,
    get_db,
    init_db,
    is_valid_input,
    sanitize_input,
)
from app.meme_matcher import export_markdown, export_txt, match_memes

app = FastAPI(title="MemeGPT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limit: 60 req/min per IP
_rate: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 60
WINDOW = 60


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api"):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        _rate[ip] = [t for t in _rate[ip] if now - t < WINDOW]
        if len(_rate[ip]) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Too many requests. Wait a minute.")
        _rate[ip].append(now)
    return await call_next(request)


@app.on_event("startup")
def startup():
    init_db()


class AnalyzeRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)


class CreateMemeRequest(BaseModel):
    name: str
    category: str
    dialogue: str
    explanation: str
    keywords: list[str]
    videoRef: str | None = None
    gifRef: str | None = None


class VoteRequest(BaseModel):
    memeId: str
    vote: int
    sessionId: str


class ExportRequest(BaseModel):
    query: str
    format: str
    result: dict


def _memes_from_db(db: Session) -> list[dict]:
    memes = db.query(Meme).all()
    return [
        {
            **m.to_dict(),
            "videoRef": m.video_ref,
            "gifRef": m.gif_ref,
        }
        for m in memes
    ]


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok", "memeCount": db.query(Meme).count()}


@app.get("/api/categories")
def categories():
    return [
        "coding", "startup", "relationship", "college", "office", "funny",
        "motivation", "unrealistic_goals", "ai", "business", "exam", "failure",
        "success", "gaming", "bollywood", "youtube",
    ]


@app.post("/api/analyze")
def analyze(body: AnalyzeRequest, db: Session = Depends(get_db)):
    query = sanitize_input(body.query)
    if not is_valid_input(query):
        raise HTTPException(400, "Query must be 3-2000 characters")

    memes = _memes_from_db(db)
    if not memes:
        raise HTTPException(503, "Database empty. Run: python backend/seed.py")

    result = match_memes(query, memes)

    meme = db.query(Meme).filter(Meme.id == result["primary"]["id"]).first()
    if meme:
        meme.usage_count += 1
        db.add(MemeUsage(meme_id=meme.id, query=query, score=result["primary"]["confidence"]))
        db.add(SearchLog(query=query, result_count=len(result["topFive"]), latency_ms=result["latencyMs"]))
        db.commit()

    return result


@app.get("/api/memes")
def list_memes(q: str = "", category: str = "", limit: int = 50, db: Session = Depends(get_db)):
    limit = min(limit, 100)
    query = db.query(Meme)
    if category:
        query = query.filter(Meme.category == category)
    memes = query.order_by(Meme.usage_count.desc()).all()

    if q:
        search = sanitize_input(q).lower()
        filtered = []
        for m in memes:
            kws = m.keywords_list()
            if (
                search in m.name.lower()
                or search in m.dialogue.lower()
                or search in m.category.lower()
                or any(search in k.lower() for k in kws)
            ):
                filtered.append(m)
        memes = filtered[:limit]
    else:
        memes = memes[:limit]

    return [m.to_dict() for m in memes]


@app.get("/api/trending")
def trending(db: Session = Depends(get_db)):
    memes = db.query(Meme).order_by(Meme.usage_count.desc(), Meme.upvotes.desc()).limit(10).all()
    return [m.to_dict() for m in memes]


@app.post("/api/admin/memes")
def create_meme(body: CreateMemeRequest, db: Session = Depends(get_db)):
    meme = Meme(
        name=sanitize_input(body.name),
        category=body.category,
        dialogue=sanitize_input(body.dialogue),
        explanation=sanitize_input(body.explanation),
        keywords=json.dumps([sanitize_input(k) for k in body.keywords]),
        video_ref=body.videoRef,
        gif_ref=body.gifRef,
    )
    db.add(meme)
    db.commit()
    db.refresh(meme)
    return meme.to_dict()


@app.delete("/api/admin/memes/{meme_id}")
def delete_meme(meme_id: str, db: Session = Depends(get_db)):
    meme = db.query(Meme).filter(Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(404, "Meme not found")
    db.delete(meme)
    db.commit()
    return {"success": True}


@app.post("/api/vote")
def vote(body: VoteRequest, db: Session = Depends(get_db)):
    if body.vote not in (1, -1):
        raise HTTPException(400, "vote must be 1 or -1")

    existing = (
        db.query(MemeVote)
        .filter(MemeVote.meme_id == body.memeId, MemeVote.session_id == body.sessionId)
        .first()
    )
    meme = db.query(Meme).filter(Meme.id == body.memeId).first()
    if not meme:
        raise HTTPException(404, "Meme not found")

    if existing:
        if existing.vote != body.vote:
            if existing.vote == 1:
                meme.upvotes -= 1
                meme.downvotes += 1
            else:
                meme.downvotes -= 1
                meme.upvotes += 1
            existing.vote = body.vote
    else:
        db.add(MemeVote(meme_id=body.memeId, vote=body.vote, session_id=body.sessionId))
        if body.vote == 1:
            meme.upvotes += 1
        else:
            meme.downvotes += 1

    db.commit()
    return {"success": True}


@app.post("/api/export")
def export(body: ExportRequest):
    fmt = body.format
    if fmt == "txt":
        content = export_txt(body.result, body.query)
        filename = "memegpt-result.txt"
        content_type = "text/plain"
    elif fmt == "markdown":
        content = export_markdown(body.result, body.query)
        filename = "memegpt-result.md"
        content_type = "text/markdown"
    elif fmt == "json":
        content = json.dumps({"query": body.query, **body.result}, indent=2)
        filename = "memegpt-result.json"
        content_type = "application/json"
    else:
        raise HTTPException(400, "format must be txt, json, or markdown")

    return {"content": content, "contentType": content_type, "filename": filename}
