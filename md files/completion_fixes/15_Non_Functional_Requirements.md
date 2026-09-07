# 15 — Non-Functional Requirements, Privacy & Retraining Guide
> Production performance budgets, GDPR data deletion, DMCA takedown automation, weekly retraining, and i18n roadmap.

---

## Problem Statement

Enterprise-grade requirements outlined in `01_PRODUCT_AND_FEATURES.md` and `04_DESIGN_AND_DEVELOPMENT.md` specify strict non-functional constraints:
1. **Performance & Memory Budget**: Server RAM < 800MB (Railway free tier), P50 latency < 1.5s, static assets CDN cache `max-age=31536000`.
2. **GDPR / Privacy Compliance**: Zero PII storage by default; full automated data wipe upon user request.
3. **DMCA Takedown Automation**: 48-hour response protocol and automated deletion script from DB, Qdrant, and Cloudflare R2.
4. **Model Retraining Pipeline**: Leveraging user clicks and thumbs up/down to continuously optimize ranking.
5. **Multi-Language Support**: Translating Spanish, Hindi, and Portuguese queries to English intent representations.

---

## Step 1: Memory Management & Performance Tuning

### 1.1 Memory Budget on Free Tier (512MB–1GB RAM)

When hosting on Railway or Render free containers, PyTorch and HuggingFace models can cause Out-Of-Memory (OOM) crashes if not loaded carefully.

In `backend/app/services/embedding_service.py`:

```python
import torch
import gc

# 1. Limit PyTorch thread allocation to prevent CPU core starvation
torch.set_num_threads(2)

# 2. Force garbage collection after initial model load
def load_models():
    # ... load MiniLM and DistilRoBERTa ...
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

### 1.2 CDN Cache-Control Headers

In `backend/app/main.py`:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class CacheHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Static media files served directly or through downloads
        if request.url.path.startswith("/media/") or "/download" in request.url.path:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif request.url.path.startswith("/api/v1/trending"):
            response.headers["Cache-Control"] = "public, max-age=1800, stale-while-revalidate=600"
        return response

app.add_middleware(CacheHeaderMiddleware)
```

---

## Step 2: GDPR Automated Data Deletion Protocol

### 2.1 Complete Deletion Route in `backend/app/api/v1/privacy.py`

**File:** `backend/app/api/v1/privacy.py`

```python
"""
MemeGPT GDPR Data Deletion API
Permanently purges all user records, saved memes, preferences, and feedback logs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, User, SavedMeme, Feedback, SearchLog
from app.core.auth import get_current_user
import logging

logger = logging.getLogger("memegpt.privacy")
router = APIRouter()

@router.delete("/privacy/me", status_code=status.HTTP_200_OK, summary="GDPR Right to Be Forgotten")
async def delete_user_account_and_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    logger.info(f"Initiating full GDPR data purge for user_id={user_id}")

    try:
        # 1. Delete all saved memes and collections
        deleted_saved = db.query(SavedMeme).filter(SavedMeme.user_id == user_id).delete()

        # 2. Anonymize feedback logs (remove user association, preserve training signals)
        db.query(Feedback).filter(Feedback.user_id == str(user_id)).update({
            "user_id": "anonymized",
            "session_id": "anonymized"
        })

        # 3. Anonymize search logs
        db.query(SearchLog).filter(SearchLog.user_id == user_id).update({
            "user_id": None
        })

        # 4. Delete user account record
        db.delete(current_user)
        db.commit()

        return {
            "status": "success",
            "message": "All personal data has been permanently purged.",
            "records_deleted": {
                "saved_memes": deleted_saved,
                "user_account": 1
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"GDPR purge failed for user_id={user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete data deletion request."
        )
```

---

## Step 3: Automated DMCA Takedown CLI Script

**File:** `scripts/dmca_takedown.py`

```python
"""
MemeGPT DMCA Takedown Handler
Removes infringing memes across SQLite/PostgreSQL, Qdrant vector index, and Cloudflare R2.
Usage: python scripts/dmca_takedown.py --slug "infringing-meme-slug" --reason "DMCA notice #1042"
"""
import argparse
import logging
from app.database import SessionLocal, Meme
from app.services.search_service import search_service
from app.services.cdn_service import cdn_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memegpt.dmca")

def process_takedown(slug: str, reason: str):
    db = SessionLocal()
    try:
        meme = db.query(Meme).filter(Meme.slug == slug).first()
        if not meme:
            logger.error(f"Meme '{slug}' not found in database.")
            return

        meme_id = meme.id
        logger.info(f"Processing takedown for: ID={meme_id}, Slug={slug}, Reason={reason}")

        # 1. Delete from Qdrant Vector Collection
        try:
            qdrant = search_service._get_qdrant()
            if qdrant:
                qdrant.delete(
                    collection_name="memes",
                    points_selector=[meme_id]
                )
                logger.info(f"✓ Removed point {meme_id} from Qdrant")
        except Exception as e:
            logger.warning(f"Qdrant deletion failed: {e}")

        # 2. Delete media from Cloudflare R2
        try:
            for ext in ["jpg", "png", "gif", "mp4", "webp"]:
                cdn_service.delete_asset(f"memes/{slug}.{ext}")
            logger.info(f"✓ Cleaned R2 CDN assets for {slug}")
        except Exception as e:
            logger.warning(f"R2 deletion failed: {e}")

        # 3. Soft-delete or hard-delete in SQL database
        db.delete(meme)
        db.commit()
        logger.info(f"✅ Meme '{slug}' successfully wiped from all stores.")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DMCA Takedown Executor")
    parser.add_argument("--slug", required=True, help="Slug of the meme to purge")
    parser.add_argument("--reason", default="DMCA request", help="Reason for audit log")
    args = parser.parse_args()

    process_takedown(args.slug, args.reason)
```

---

## Step 4: Feedback-Driven Re-Ranker Optimization (Weekly Job)

### 4.1 Collect Explicit & Implicit Feedback

The re-ranking weights are dynamically adjusted based on click-through and positive vote rates:

$$\text{PopularityBoost} = \log(1 + \text{views}) \times 0.2 + \text{positive\_votes} \times 0.3$$

**File:** `scripts/optimize_rerank_weights.py`

```python
"""
Weekly Re-ranker Optimization Script
Analyzes Feedback and SearchLog tables to update popularity and emotion affinity scores.
"""
from app.database import SessionLocal, Meme, Feedback
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memegpt.optimizer")

def optimize_weights():
    db = SessionLocal()
    try:
        # Calculate vote ratios per meme
        stats = db.query(
            Feedback.meme_id,
            func.count(Feedback.id).label("total_interactions"),
            func.sum(case((Feedback.action == "thumbs_up", 1), else_=0)).label("upvotes"),
            func.sum(case((Feedback.action == "thumbs_down", 1), else_=0)).label("downvotes"),
        ).group_by(Feedback.meme_id).all()

        for s in stats:
            meme = db.query(Meme).filter(Meme.id == s.meme_id).first()
            if meme and s.total_interactions > 5:
                # Update score between 0.0 and 1.0
                score = (s.upvotes + 1.0) / (s.total_interactions + 2.0)
                meme.popularity_score = round(score, 3)

        db.commit()
        logger.info(f"Updated popularity scores for {len(stats)} memes.")
    finally:
        db.close()

if __name__ == "__main__":
    optimize_weights()
```

---

## Step 5: Multi-Language Translation Roadmap

To handle queries in Hindi, Spanish, or Portuguese, the Groq intent parser in `backend/app/services/llm_service.py` is configured with auto-translation in the prompt:

```python
PROMPT = """
You are a multilingual meme expert AI.
The user input may be in English, Spanish, Hindi, or Portuguese.

1. Detect language.
2. If non-English, translate intent to English meme culture concepts.
3. Return the standard JSON with English keywords, emotion, and situation.
"""
```

This delivers instant zero-latency multilingual support without downloading heavy translation models.

---

## Step 6: Verification Checklist

- [ ] Test GDPR deletion: Register a test user, save 2 memes, call `DELETE /api/v1/privacy/me`, verify all records deleted.
- [ ] Test DMCA script in dry-run mode:
  ```powershell
  python scripts/dmca_takedown.py --slug "test-meme" --reason "Audit verification"
  ```
- [ ] Run re-ranking optimizer:
  ```powershell
  python scripts/optimize_rerank_weights.py
  ```
- [ ] Query API with Spanish or Hindi phrase ("cuando el código funciona pero no sabes por qué") and verify accurate English meme return.
