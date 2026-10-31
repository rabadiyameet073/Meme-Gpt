# 01 — Qdrant Cloud Setup + Meme Indexing
> **Priority:** 🔴 CRITICAL BLOCKER — Without this, AI search is completely disabled
> **Time Needed:** ~2 hours
> **Result:** Real semantic vector search returns contextually accurate memes

---

## 🧠 What is Qdrant and Why We Need It

**Qdrant** is a vector database. It stores memes as 384-dimensional float vectors (embeddings from the MiniLM model) and finds the closest matching memes to any user query using cosine similarity.

Without Qdrant connected:
- User types "when your code works first try" → Backend falls back to keyword search in SQLite
- SQLite has no semantic understanding — it just looks for exact word matches
- Results are terrible or empty

With Qdrant connected:
- User types "when your code works first try" → MiniLM converts this to a 384-dim vector → Qdrant finds the 50 most similar memes by angle → CLIP re-ranks → Top 10 returned
- Results are contextually accurate even with completely different words

**Vector Schema in This Project:**
- Collection name: `memes`
- `text` vector: 384-dim (from `all-MiniLM-L6-v2`)
- `image` vector: 512-dim (from `CLIP ViT-B/32`, optional)
- `combined` vector: 896-dim (text + image weighted)

---

## 📋 Step 1 — Create Qdrant Cloud Account

```
1. Go to: https://cloud.qdrant.io
2. Click "Sign Up" (free, no credit card needed)
3. Click "Create Cluster"
4. Settings:
   - Name: memegpt-prod
   - Cloud: AWS
   - Region: us-east-1 (or closest to your Railway region)
   - Plan: FREE (1GB storage — enough for ~500K memes)
5. Click "Create"
6. Wait 1-2 minutes for cluster to start
7. Copy:
   - Cluster URL (looks like: https://abc123.us-east-1.aws.cloud.qdrant.io)
   - API Key (from "API Keys" tab → Create Key)
```

---

## 📋 Step 2 — Add to Your .env File

Open `d:\Meme GPT\.env` and fill in these values:

```env
# ── QDRANT (Vector Search) ────────────────────────
QDRANT_URL=https://YOUR-CLUSTER-ID.us-east-1.aws.cloud.qdrant.io
QDRANT_API_KEY=your_api_key_here
QDRANT_COLLECTION=memes
QDRANT_TIMEOUT=10
```

**Test the connection immediately:**
```powershell
cd "d:\Meme GPT\backend"
python -c "
from app.services.search_service import get_qdrant_client
client = get_qdrant_client()
if client:
    print('✅ Qdrant connected!')
    print(client.get_collections())
else:
    print('❌ Connection failed — check QDRANT_URL and QDRANT_API_KEY')
"
```

---

## 📋 Step 3 — Create the Meme Collection

This creates the `memes` collection with the correct vector dimensions.

```powershell
cd "d:\Meme GPT\backend"
python -c "
from app.services.search_service import create_qdrant_collection, get_collection_info
result = create_qdrant_collection(recreate=False)
print('Collection created:', result)
info = get_collection_info()
print('Collection info:', info)
"
```

**Expected output:**
```
Collection created: True
Collection info: {'name': 'memes', 'status': 'green', 'vectors_count': 0, ...}
```

If you get an error that collection already exists, that's fine — run with `recreate=False`.

---

## 📋 Step 4 — Verify Collection Structure

```python
# Run this to see what vectors are configured
from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

info = client.get_collection("memes")
print("Vectors config:", info.config.params.vectors)
```

**Expected:** Should show text (384), image (512), combined (896) named vectors.

---

## 📋 Step 5 — Index Your Existing Memes into Qdrant

This takes every meme in your SQLite database and puts it into Qdrant with embeddings.

**First, make sure you have memes in the DB. Check:**
```powershell
cd "d:\Meme GPT\backend"
python -c "
from app.database import SessionLocal, Meme
db = SessionLocal()
count = db.query(Meme).count()
print(f'Memes in DB: {count}')
db.close()
"
```

**If count > 0, run the indexing script:**
```powershell
cd "d:\Meme GPT\backend"
python generate_embeddings.py
```

**If that script doesn't exist or fails, use this direct approach:**

Create file `d:\Meme GPT\backend\scripts\reindex_all_to_qdrant.py`:

```python
"""
MemeGPT — Reindex all memes from SQLite to Qdrant.
Run this whenever you add new memes to the DB.
"""
import os
import sys
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reindex")

from app.database import SessionLocal, Meme
from app.services.embedding_service import embed_text, load_models
from app.services.search_service import get_qdrant_client, create_qdrant_collection, COLLECTION_NAME

def build_meme_text(meme) -> str:
    """Build the text representation of a meme for embedding."""
    parts = []
    if meme.name:
        parts.append(meme.name)
    if hasattr(meme, 'explanation') and meme.explanation:
        parts.append(meme.explanation)
    if hasattr(meme, 'dialogue') and meme.dialogue:
        parts.append(meme.dialogue)
    if meme.category:
        parts.append(f"category: {meme.category}")
    if meme.emotion:
        parts.append(f"emotion: {meme.emotion}")
    if hasattr(meme, 'keywords') and meme.keywords:
        kws = meme.keywords if isinstance(meme.keywords, list) else []
        parts.append(f"keywords: {', '.join(kws[:10])}")
    return " | ".join(parts) or meme.name or "meme"


def main():
    logger.info("Loading ML models...")
    load_models()

    logger.info("Connecting to Qdrant...")
    client = get_qdrant_client()
    if not client:
        logger.error("❌ Cannot connect to Qdrant. Check QDRANT_URL and QDRANT_API_KEY in .env")
        return

    logger.info("Creating collection (if not exists)...")
    create_qdrant_collection(recreate=False)

    logger.info("Loading memes from SQLite...")
    db = SessionLocal()
    memes = db.query(Meme).all()
    logger.info(f"Found {len(memes)} memes to index")
    db.close()

    if not memes:
        logger.warning("No memes found in DB. Run seed script first.")
        return

    from qdrant_client.models import PointStruct

    BATCH_SIZE = 50
    total = 0

    for i in range(0, len(memes), BATCH_SIZE):
        batch = memes[i:i + BATCH_SIZE]
        points = []

        for meme in batch:
            try:
                text = build_meme_text(meme)
                vector = embed_text(text)

                payload = {
                    "name": meme.name or "",
                    "slug": meme.slug or str(meme.id),
                    "category": meme.category or "",
                    "emotion": meme.emotion or "",
                    "format": meme.format or "image",
                    "image_url": meme.image_url or "",
                    "gif_url": getattr(meme, "gif_url", "") or "",
                    "thumb_url": getattr(meme, "thumb_url", "") or meme.image_url or "",
                    "usage_count": meme.usage_count or 0,
                    "is_nsfw": meme.is_nsfw if hasattr(meme, "is_nsfw") else False,
                }

                points.append(PointStruct(
                    id=meme.id,
                    vector={"text": vector},
                    payload=payload
                ))
            except Exception as e:
                logger.warning(f"Failed to index meme {meme.id}: {e}")

        if points:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            total += len(points)
            logger.info(f"Indexed {total}/{len(memes)} memes...")

    logger.info(f"✅ Done! Indexed {total} memes into Qdrant.")

    # Verify
    info = client.get_collection(COLLECTION_NAME)
    logger.info(f"Qdrant collection now has {info.vectors_count} vectors")


if __name__ == "__main__":
    main()
```

**Run it:**
```powershell
cd "d:\Meme GPT\backend"
python scripts/reindex_all_to_qdrant.py
```

---

## 📋 Step 6 — Test That Vector Search Works

```powershell
cd "d:\Meme GPT\backend"
python -c "
from app.services.embedding_service import embed_text, load_models
from app.services.search_service import vector_search

load_models()

query = 'when your code works on first try'
print(f'Testing search for: {query}')

vector = embed_text(query)
results = vector_search(vector, limit=5)

print(f'Found {len(results)} results:')
for r in results:
    name = r.get('meme', {}).get('name', 'Unknown')
    score = r.get('score', 0)
    print(f'  [{score:.3f}] {name}')
"
```

**Expected output** (if you have memes indexed):
```
Testing search for: when your code works on first try
Found 5 results:
  [0.847] Surprised Pikachu
  [0.823] That Would Be Great
  [0.801] Success Kid
  ...
```

---

## 📋 Step 7 — Verify in Backend Logs

Start the backend and make a real search:
```powershell
cd "d:\Meme GPT\backend"
uvicorn app.main:app --reload --port 8000
```

In another terminal:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query": "when your code works first try", "limit": 5}'
```

Look for in logs:
```
✅ Qdrant connected: https://your-cluster.qdrant.io
Qdrant collection status: {'vectors_count': 150, ...}
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` | Check QDRANT_URL has `https://` prefix |
| `Unauthorized` | Regenerate API key in Qdrant Cloud dashboard |
| `Collection not found` | Run `create_qdrant_collection(recreate=False)` |
| `Zero results` | Run the reindex script in Step 5 |
| `Import error: qdrant_client` | Run `pip install qdrant-client>=1.9.0` |
| Slow queries (>2s) | Check Qdrant region — should match Railway/backend region |

---

## ✅ Done When

- [ ] `get_qdrant_client()` returns non-None
- [ ] Collection `memes` exists in Qdrant Cloud dashboard
- [ ] Vector count > 0 in collection
- [ ] Search endpoint returns semantically relevant memes
- [ ] Backend logs show `✅ Qdrant connected`

**Next step → `02_Redis_Upstash_Setup.md`**
