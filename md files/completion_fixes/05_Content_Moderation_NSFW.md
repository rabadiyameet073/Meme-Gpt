# 05 — Content Moderation & NSFW Filter Guide
> Implement CLIP-based NSFW classification, community flagging, and admin review queue.

---

## Problem Statement

| Feature | Spec Requirement | Current Status |
|---------|-----------------|----------------|
| NSFW classifier | CLIP-based, mandatory | ❌ Only a boolean field on Meme model |
| Community flagging | Users report inappropriate memes | ❌ Not implemented |
| Auto-removal | 5+ flags → review queue | ❌ Not implemented |
| Admin review dashboard | Manual review of flagged memes | 🟡 AdminTab exists but no moderation queue |

---

## Step 1: Create NSFW Classification Service

**File (create new):** `backend/app/services/nsfw_service.py`

```python
"""
NSFW Content Classification using CLIP zero-shot.
Uses CLIP's text-image alignment to classify memes as safe/nsfw.
Runs during indexing and on user-uploaded content.
"""
import logging
import os
from typing import Tuple

logger = logging.getLogger("memegpt.nsfw")

_clip_model = None
_clip_processor = None
MODELS_CACHE_DIR = os.getenv("MODELS_CACHE_DIR", "./model_cache")

NSFW_LABELS = ["safe content", "nsfw adult content", "violent content", "hate speech imagery"]
NSFW_THRESHOLD = 0.45  # Score above this = flagged


def _load_clip():
    global _clip_model, _clip_processor
    if _clip_model is not None:
        return
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        _clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32", cache_dir=MODELS_CACHE_DIR
        )
        _clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32", cache_dir=MODELS_CACHE_DIR
        )
        logger.info("✅ NSFW CLIP classifier loaded")
    except Exception as e:
        logger.error(f"Failed to load CLIP for NSFW: {e}")


def classify_image(image_path: str) -> Tuple[bool, float, str]:
    """
    Classify an image as NSFW or safe using CLIP zero-shot.

    Returns: (is_nsfw: bool, confidence: float, category: str)
    """
    _load_clip()
    if _clip_model is None:
        return False, 0.0, "safe content"

    try:
        import torch
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        inputs = _clip_processor(
            text=NSFW_LABELS, images=image, return_tensors="pt", padding=True
        )

        with torch.no_grad():
            outputs = _clip_model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]

        scores = {label: float(prob) for label, prob in zip(NSFW_LABELS, probs)}
        nsfw_score = max(scores.get("nsfw adult content", 0), scores.get("violent content", 0))
        top_label = max(scores, key=scores.get)

        is_nsfw = nsfw_score > NSFW_THRESHOLD
        return is_nsfw, nsfw_score, top_label

    except Exception as e:
        logger.warning(f"NSFW classification failed: {e}")
        return False, 0.0, "safe content"


def classify_image_from_url(url: str) -> Tuple[bool, float, str]:
    """Download image from URL and classify."""
    import tempfile, requests
    try:
        resp = requests.get(url, timeout=10)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(resp.content)
            return classify_image(f.name)
    except Exception:
        return False, 0.0, "safe content"
```

---

## Step 2: Add Flagging Model to Database

**Add to:** `backend/app/database.py`

```python
class MemeFlag(Base):
    """Community flagging — users report inappropriate memes."""
    __tablename__ = "meme_flags"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    meme_id = Column(String(64), ForeignKey("memes.id"), nullable=False, index=True)
    reporter_ip = Column(String(45), nullable=True)  # Anonymous reporting
    reporter_user_id = Column(String(64), nullable=True)
    reason = Column(String(50), nullable=False)  # 'nsfw' | 'offensive' | 'copyright' | 'spam' | 'other'
    details = Column(Text, default="")
    status = Column(String(20), default="pending")  # 'pending' | 'reviewed' | 'removed' | 'dismissed'
    reviewed_by = Column(String(64), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    meme = relationship("Meme", backref="flags")

    __table_args__ = (
        Index("idx_flags_meme_status", "meme_id", "status"),
    )
```

Also add to the `Meme` model:
```python
# In the Meme class, add:
flag_count = Column(Integer, default=0)
moderation_status = Column(String(20), default="approved")  # 'approved' | 'pending_review' | 'removed'
```

---

## Step 3: Create Flagging API

**File (create new):** `backend/app/api/v1/moderation.py`

```python
"""Content moderation — flagging, review queue, admin actions."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db, Meme, MemeFlag, utc_now

router = APIRouter(prefix="/moderation", tags=["Content Moderation"])


class FlagRequest(BaseModel):
    meme_id: str
    reason: str  # 'nsfw' | 'offensive' | 'copyright' | 'spam' | 'other'
    details: Optional[str] = ""


@router.post("/flag", summary="Flag a meme as inappropriate")
async def flag_meme(body: FlagRequest, request: Request, db: Session = Depends(get_db)):
    """Community flagging. Auto-queues meme for review after 5 flags."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    if body.reason not in ("nsfw", "offensive", "copyright", "spam", "other"):
        raise HTTPException(status_code=400, detail="Invalid reason")

    flag = MemeFlag(
        meme_id=body.meme_id,
        reporter_ip=request.client.host if request.client else None,
        reason=body.reason,
        details=body.details or "",
    )
    db.add(flag)

    # Increment flag count
    meme.flag_count = (meme.flag_count or 0) + 1

    # Auto-queue for review after 5 flags
    if meme.flag_count >= 5 and meme.moderation_status == "approved":
        meme.moderation_status = "pending_review"

    db.commit()

    return {"flagged": True, "total_flags": meme.flag_count}


@router.get("/queue", summary="Get moderation review queue (admin)")
async def get_review_queue(db: Session = Depends(get_db)):
    """Returns memes pending review, sorted by flag count."""
    memes = (
        db.query(Meme)
        .filter(Meme.moderation_status == "pending_review")
        .order_by(Meme.flag_count.desc())
        .limit(50)
        .all()
    )
    return {
        "queue": [
            {
                **m.to_dict(),
                "flag_count": m.flag_count,
                "flags": [
                    {"reason": f.reason, "details": f.details, "created_at": f.created_at.isoformat()}
                    for f in m.flags
                ],
            }
            for m in memes
        ]
    }


class ReviewAction(BaseModel):
    meme_id: str
    action: str  # 'approve' | 'remove'


@router.post("/review", summary="Admin review action")
async def review_meme(body: ReviewAction, db: Session = Depends(get_db)):
    """Admin approves or removes a flagged meme."""
    meme = db.query(Meme).filter(Meme.id == body.meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    if body.action == "approve":
        meme.moderation_status = "approved"
        meme.flag_count = 0
        # Dismiss all pending flags
        db.query(MemeFlag).filter(
            MemeFlag.meme_id == body.meme_id, MemeFlag.status == "pending"
        ).update({"status": "dismissed", "reviewed_at": utc_now()})
    elif body.action == "remove":
        meme.moderation_status = "removed"
        db.query(MemeFlag).filter(
            MemeFlag.meme_id == body.meme_id, MemeFlag.status == "pending"
        ).update({"status": "reviewed", "reviewed_at": utc_now()})
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'remove'")

    db.commit()
    return {"status": meme.moderation_status}
```

---

## Step 4: Register the Router

**Add to:** `backend/app/api/v1/__init__.py`

```python
from app.api.v1.moderation import router as moderation_router
v1_router.include_router(moderation_router)
```

---

## Step 5: Filter Out Removed Memes in Search

**Modify:** `backend/app/api/v1/search.py`

In the `_memes_from_db` function, add a filter:

```python
def _memes_from_db(db: Session) -> list[dict]:
    memes = db.query(Meme).filter(
        Meme.moderation_status != "removed"  # ← Add this filter
    ).all()
    return [...]
```

---

## Verification Checklist

- [ ] NSFW service classifies images as safe/nsfw with confidence scores
- [ ] `MemeFlag` table exists in database
- [ ] `POST /api/v1/moderation/flag` creates a flag record
- [ ] Meme auto-queued for review after 5 flags
- [ ] `GET /api/v1/moderation/queue` returns flagged memes (admin)
- [ ] `POST /api/v1/moderation/review` approves or removes memes
- [ ] Removed memes are excluded from search results
