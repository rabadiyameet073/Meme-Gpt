# MemeGPT — ML Pipeline & Training Guide
> This file explains exactly how to collect memes, process them, generate embeddings, index them, and serve results accurately.

---

## 🗺️ Pipeline Overview

There are two separate pipelines:

```
┌─────────────────────────────────────────────────────────────────┐
│  PIPELINE 1: OFFLINE INDEXING (runs once + periodic updates)    │
│                                                                  │
│  Data Sources → Collect → Clean → OCR → Embed → Index to Qdrant │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PIPELINE 2: ONLINE SERVING (runs for every user query, <1.5s)  │
│                                                                  │
│  User Query → Embed → Search → Re-rank → Score → Return Results  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Pipeline 1: Offline Data Collection & Indexing

### Step 1.1 — Meme Data Sources

#### Source A: Reddit (Best Quality, Metadata-Rich)
```python
# Use PRAW (Python Reddit API Wrapper)
pip install praw

import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="MemeGPT/1.0"
)

# Target subreddits (curated list)
MEME_SUBREDDITS = [
    "memes",           # General memes — 20M+ members
    "dankmemes",       # Dank memes — 8M+ members
    "ProgrammerHumor", # Dev/coding memes
    "me_irl",          # Relatable life memes
    "AdviceAnimals",   # Classic reaction memes
    "reactiongifs",    # Pure reaction GIFs
    "HistoryMemes",    # Educational + funny
    "wholesomememes",  # Positive/wholesome
    "BlackPeopleTwitter", # Cultural humor
    "terriblefacebookmemes", # Absurd humor
]

def collect_subreddit_memes(subreddit_name: str, limit: int = 1000):
    subreddit = reddit.subreddit(subreddit_name)
    memes = []
    
    for post in subreddit.top(time_filter="all", limit=limit):
        if post.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4')):
            memes.append({
                "id": post.id,
                "title": post.title,
                "url": post.url,
                "upvotes": post.score,
                "subreddit": subreddit_name,
                "created_utc": post.created_utc,
                "is_nsfw": post.over_18,
                "format": detect_format(post.url),
            })
    return memes
```

#### Source B: Imgflip API (Meme Templates)
```python
import httpx

async def collect_imgflip_memes():
    async with httpx.AsyncClient() as client:
        # Get top 100 meme templates (free, no auth needed)
        response = await client.get("https://api.imgflip.com/get_memes")
        data = response.json()
        
        memes = []
        for meme in data["data"]["memes"]:
            memes.append({
                "id": f"imgflip_{meme['id']}",
                "title": meme["name"],
                "url": meme["url"],
                "format": "png",
                "source": "imgflip",
                "box_count": meme["box_count"]
            })
        return memes
```

#### Source C: Giphy API (GIFs)
```python
async def collect_giphy_memes(search_terms: list, limit_per_term: int = 25):
    GIPHY_API_KEY = "your_api_key"
    memes = []
    
    async with httpx.AsyncClient() as client:
        for term in search_terms:
            response = await client.get(
                "https://api.giphy.com/v1/gifs/search",
                params={
                    "api_key": GIPHY_API_KEY,
                    "q": term,
                    "limit": limit_per_term,
                    "rating": "g",
                    "lang": "en"
                }
            )
            data = response.json()
            for gif in data["data"]:
                memes.append({
                    "id": f"giphy_{gif['id']}",
                    "title": gif["title"],
                    "url": gif["images"]["original"]["url"],
                    "thumb_url": gif["images"]["fixed_width"]["url"],
                    "format": "gif",
                    "source": "giphy",
                    "tags": gif.get("tags", [])
                })
    return memes
```

**Target: Collect 100,000+ memes in Phase 1**
- Reddit: ~60,000 memes (top posts from each subreddit)
- Imgflip: ~1,000 meme templates
- Giphy: ~30,000 GIFs (searched by 300 common meme search terms)
- Tenor: ~10,000 GIFs

---

### Step 1.2 — Data Cleaning & Validation

```python
from PIL import Image
import httpx
import hashlib

async def validate_and_clean_meme(meme: dict) -> dict | None:
    """Returns cleaned meme or None if invalid."""
    
    # 1. Skip NSFW (unless safe mode disabled in future)
    if meme.get("is_nsfw"):
        return None
    
    # 2. Try to fetch the media
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.head(meme["url"])
            if response.status_code != 200:
                return None
            content_type = response.headers.get("content-type", "")
            content_length = int(response.headers.get("content-length", 0))
    except:
        return None
    
    # 3. Skip files that are too large (>10MB) or too small (<5KB)
    if content_length > 10_000_000 or content_length < 5_000:
        return None
    
    # 4. Validate content type
    valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4"]
    if not any(t in content_type for t in valid_types):
        return None
    
    # 5. Generate unique hash (deduplication)
    meme["hash"] = hashlib.md5(meme["url"].encode()).hexdigest()
    
    # 6. Normalize format
    meme["format"] = detect_format_from_content_type(content_type)
    
    return meme
```

---

### Step 1.3 — OCR: Extract Text From Meme Images

```python
import pytesseract
from PIL import Image
import httpx
import io

async def extract_text_from_meme(image_url: str) -> str:
    """Download image and extract any text in it."""
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(image_url)
            img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Tesseract OCR config:
        # --psm 6 = Assume a single uniform block of text
        # --oem 3 = Use both legacy and LSTM engine
        config = '--psm 6 --oem 3'
        text = pytesseract.image_to_string(img, config=config)
        
        # Clean up extracted text
        text = ' '.join(text.split())  # normalize whitespace
        return text if len(text) > 3 else ""
    except:
        return ""
```

---

### Step 1.4 — Build the Meme Text Corpus (What Gets Embedded)

Each meme gets a single text string that represents its full meaning. This is what gets embedded into a vector.

```python
def build_meme_corpus_text(meme: dict) -> str:
    """
    Combine all textual signals into one rich text string for embedding.
    The quality of this text directly determines search quality.
    """
    parts = []
    
    # Reddit post title (most informative)
    if meme.get("title"):
        parts.append(meme["title"])
    
    # OCR text from the image
    if meme.get("ocr_text") and len(meme["ocr_text"]) > 5:
        parts.append(meme["ocr_text"])
    
    # Subreddit name as context
    if meme.get("subreddit"):
        subreddit = meme["subreddit"].replace("_", " ")
        parts.append(f"from {subreddit}")
    
    # Tags
    if meme.get("tags"):
        parts.append("tags: " + ", ".join(meme["tags"][:10]))
    
    # Emotion and humor type (if detected)
    if meme.get("emotion"):
        parts.append(f"emotion: {meme['emotion']}")
    if meme.get("humor_type"):
        parts.append(f"humor: {meme['humor_type']}")
    
    return " | ".join(parts)

# Example output:
# "When your code works on first try | Nobody: Me when I hit run | 
#  from ProgrammerHumor | tags: programming, coding, relatable | 
#  emotion: surprised | humor: relatable"
```

---

### Step 1.5 — Generate Embeddings

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

# Load model ONCE at startup
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_memes_batch(memes: list[dict], batch_size: int = 64) -> list[np.ndarray]:
    """
    Generate embeddings for a batch of memes.
    Process in batches for memory efficiency.
    """
    corpus_texts = [build_meme_corpus_text(meme) for meme in memes]
    
    all_vectors = []
    for i in tqdm(range(0, len(corpus_texts), batch_size), desc="Generating embeddings"):
        batch = corpus_texts[i:i + batch_size]
        vectors = embedding_model.encode(
            batch,
            normalize_embeddings=True,  # Important for cosine similarity!
            show_progress_bar=False
        )
        all_vectors.extend(vectors)
    
    return all_vectors

# Stats: 100K memes × 22ms = ~36 minutes on laptop CPU. Run overnight.
```

---

### Step 1.6 — Pre-compute CLIP Tags (Optional, Improves Quality)

```python
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

# Load CLIP model (only for indexing, not serving)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Predefined candidate labels for meme categories
EMOTION_LABELS = [
    "happy and laughing", "angry and frustrated", "shocked and surprised",
    "crying and sad", "confused and puzzled", "sarcastic and eye-rolling",
    "celebrating and winning", "tired and exhausted"
]

TOPIC_LABELS = [
    "programming and coding", "relationships and dating", "work and office",
    "food and eating", "gaming", "sports", "school and studying",
    "social media", "politics", "family"
]

async def classify_meme_with_clip(image: Image.Image) -> dict:
    """Get zero-shot classification of meme image using CLIP."""
    
    # Classify emotion
    inputs = clip_processor(
        text=EMOTION_LABELS, images=image, 
        return_tensors="pt", padding=True
    )
    with torch.no_grad():
        outputs = clip_model(**inputs)
    emotion_probs = outputs.logits_per_image.softmax(dim=1)[0]
    detected_emotion = EMOTION_LABELS[emotion_probs.argmax().item()]
    
    # Classify topic
    inputs = clip_processor(
        text=TOPIC_LABELS, images=image,
        return_tensors="pt", padding=True
    )
    with torch.no_grad():
        outputs = clip_model(**inputs)
    topic_probs = outputs.logits_per_image.softmax(dim=1)[0]
    detected_topic = TOPIC_LABELS[topic_probs.argmax().item()]
    
    return {
        "emotion": detected_emotion,
        "topic": detected_topic,
        "emotion_confidence": float(emotion_probs.max()),
        "topic_confidence": float(topic_probs.max())
    }
```

---

### Step 1.7 — Index Into Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue
)

client = QdrantClient(
    url="https://your-cluster.qdrant.io",
    api_key="your_api_key"
)

# Create collection (run ONCE)
def create_meme_collection():
    client.create_collection(
        collection_name="memes",
        vectors_config=VectorParams(
            size=384,           # MiniLM-L6-v2 dimension
            distance=Distance.COSINE  # Cosine similarity
        )
    )
    
    # Create payload indexes for filtering
    client.create_payload_index("memes", "format", "keyword")
    client.create_payload_index("memes", "emotion", "keyword")
    client.create_payload_index("memes", "humor_type", "keyword")
    client.create_payload_index("memes", "is_nsfw", "bool")
    client.create_payload_index("memes", "upvotes", "integer")

# Upload memes in batches
def index_memes_to_qdrant(memes: list[dict], vectors: list):
    points = []
    
    for meme, vector in zip(memes, vectors):
        point = PointStruct(
            id=meme["id"],
            vector=vector.tolist(),
            payload={
                "title": meme.get("title", ""),
                "format": meme.get("format", "image"),
                "media_url": meme.get("media_url", ""),
                "thumb_url": meme.get("thumb_url", ""),
                "source": meme.get("source", ""),
                "subreddit": meme.get("subreddit", ""),
                "upvotes": meme.get("upvotes", 0),
                "tags": meme.get("tags", []),
                "emotion": meme.get("emotion", ""),
                "humor_type": meme.get("humor_type", ""),
                "is_nsfw": meme.get("is_nsfw", False),
                "created_at": meme.get("created_at", ""),
            }
        )
        points.append(point)
    
    # Upload in batches of 100
    for i in range(0, len(points), 100):
        batch = points[i:i+100]
        client.upsert(collection_name="memes", points=batch)
        
    print(f"Indexed {len(points)} memes")
```

---

## 🔍 Pipeline 2: Online Query Serving

### Step 2.1 — Embed User Query

```python
def embed_query(query_text: str) -> np.ndarray:
    """Convert user query to embedding vector."""
    vector = embedding_model.encode(
        query_text,
        normalize_embeddings=True  # Must match how memes were embedded
    )
    return vector
```

---

### Step 2.2 — Vector Search in Qdrant

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest

def search_memes(
    query_vector: list,
    limit: int = 50,   # Fetch 50 candidates for re-ranking
    format_filter: str = None,
    emotion_filter: str = None,
    safe_mode: bool = True
) -> list:
    
    # Build filters
    must_conditions = []
    
    if safe_mode:
        must_conditions.append(
            FieldCondition(key="is_nsfw", match=MatchValue(value=False))
        )
    
    if format_filter:
        must_conditions.append(
            FieldCondition(key="format", match=MatchValue(value=format_filter))
        )
    
    if emotion_filter:
        must_conditions.append(
            FieldCondition(key="emotion", match=MatchValue(value=emotion_filter))
        )
    
    query_filter = Filter(must=must_conditions) if must_conditions else None
    
    # Execute search
    results = client.search(
        collection_name="memes",
        query_vector=query_vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
        score_threshold=0.3  # Minimum similarity score
    )
    
    return results
```

---

### Step 2.3 — CLIP Re-ranking (The Key Quality Step)

```python
def rerank_with_clip(
    query_text: str, 
    candidate_memes: list,
    top_k: int = 10
) -> list:
    """
    Re-rank top 50 vector search results using CLIP text-image similarity.
    This is what makes MemeGPT more accurate than keyword search.
    """
    
    reranked = []
    
    for meme in candidate_memes:
        # Download thumbnail for CLIP scoring
        try:
            response = httpx.get(meme.payload["thumb_url"], timeout=5)
            img = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            # Get CLIP score
            inputs = clip_processor(
                text=[query_text],
                images=img,
                return_tensors="pt",
                padding=True
            )
            with torch.no_grad():
                outputs = clip_model(**inputs)
            clip_score = float(outputs.logits_per_image[0][0])
            
        except:
            clip_score = 0.0  # If image fails, use 0
        
        # Compute final composite score
        vector_score = meme.score          # 0 to 1 — semantic similarity
        popularity_score = min(meme.payload.get("upvotes", 0) / 100000, 1.0)  # normalized
        
        final_score = (
            vector_score * 0.55 +      # Semantic match (most important)
            clip_score * 0.30 +        # Visual relevance
            popularity_score * 0.15    # Popularity boost
        )
        
        reranked.append({
            **meme.payload,
            "id": meme.id,
            "vector_score": vector_score,
            "clip_score": clip_score,
            "final_score": final_score
        })
    
    # Sort by final score, return top K
    reranked.sort(key=lambda x: x["final_score"], reverse=True)
    return reranked[:top_k]
```

---

### Step 2.4 — Full Search Endpoint (FastAPI)

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel
import redis.asyncio as redis

app = FastAPI()
cache = redis.from_url("redis://your-upstash-url")
CACHE_TTL = 3600  # 1 hour cache for identical queries

class SearchRequest(BaseModel):
    query: str
    format: str | None = None    # "gif", "image", "video"
    emotion: str | None = None   # "happy", "sad", "angry", etc.
    limit: int = 10
    safe_mode: bool = True

@app.post("/api/v1/search")
async def search_memes_endpoint(request: SearchRequest):
    
    # 1. Cache check (identical query → instant return)
    cache_key = f"search:{request.query}:{request.format}:{request.emotion}"
    cached = await cache.get(cache_key)
    if cached:
        return {"results": json.loads(cached), "from_cache": True}
    
    # 2. Embed query
    query_vector = embed_query(request.query)
    
    # 3. Vector search (50 candidates)
    candidates = search_memes(
        query_vector=query_vector.tolist(),
        limit=50,
        format_filter=request.format,
        emotion_filter=request.emotion,
        safe_mode=request.safe_mode
    )
    
    # 4. CLIP re-ranking → top 10
    top_memes = rerank_with_clip(
        query_text=request.query,
        candidate_memes=candidates,
        top_k=request.limit
    )
    
    # 5. Cache result
    await cache.setex(cache_key, CACHE_TTL, json.dumps(top_memes))
    
    return {"results": top_memes, "from_cache": False}
```

---

## 📈 Model Quality Evaluation

### Metrics to Track

| Metric | Description | Target |
|---|---|---|
| **Precision@5** | Of top 5 results, % that are relevant | > 80% |
| **Precision@10** | Of top 10 results, % that are relevant | > 70% |
| **Mean Reciprocal Rank (MRR)** | How early the best result appears | > 0.7 |
| **Click-through rate** | % of searches where user copies/downloads | > 40% |
| **Zero-result rate** | % of queries with score < 0.3 | < 5% |
| **P50 latency** | Median search response time | < 1.5s |
| **P99 latency** | 99th percentile response time | < 3s |

### Test Dataset (Create This First)
```python
# Create a golden test set of 200 query-meme pairs
TEST_CASES = [
    {
        "query": "when your code works on first try",
        "expected_meme_ids": ["meme_abc", "meme_xyz"],
        "expected_emotion": "surprised"
    },
    {
        "query": "Monday morning feeling",
        "expected_meme_ids": ["meme_111", "meme_222"],
        "expected_emotion": "tired"
    },
    # ... 198 more cases
]

def evaluate_model(test_cases: list) -> dict:
    precision_at_5 = []
    
    for case in test_cases:
        results = search_memes_full(case["query"])
        top_5_ids = [r["id"] for r in results[:5]]
        
        hits = sum(1 for id in top_5_ids if id in case["expected_meme_ids"])
        precision_at_5.append(hits / 5)
    
    return {
        "precision@5": sum(precision_at_5) / len(precision_at_5),
        "num_test_cases": len(test_cases)
    }
```

---

## 🔄 Continuous Improvement (Feedback Loop)

### Signal Collection (Privacy-Preserving)
```python
# Every time a user copies or downloads a meme, log:
feedback_event = {
    "query_hash": md5(query),  # NOT the actual query
    "result_position": 3,      # Which position they clicked (1-10)
    "action": "download",      # "copy" | "download" | "share" | "skip"
    "timestamp": now()
}
# Store in Supabase analytics table
```

### Weekly Retraining Signal
- Identify memes at positions 6-10 that get more clicks than positions 1-5 → boost them
- Identify queries that get 0 copies/downloads → add to "bad results" list
- Increase weight of popular memes in scoring formula
- Add new memes from Reddit weekly (run indexing pipeline every Sunday 2am)

---

## 🗂️ Meme Category Taxonomy

Define these categories for all indexed memes. Each meme gets ONE primary category:

```python
MEME_CATEGORIES = {
    "reactions": ["surprised", "angry", "sad", "happy", "confused", "disgusted"],
    "topics": ["programming", "relationships", "work", "school", "food", "gaming", 
               "sports", "politics", "family", "social_media", "money", "health"],
    "humor_types": ["relatable", "wholesome", "dark", "absurd", "ironic", 
                    "self_deprecating", "observational"],
    "formats": ["image", "gif", "video", "sticker"],
    "templates": ["drake", "distracted_boyfriend", "two_buttons", "change_my_mind",
                  "this_is_fine", "expanding_brain", "women_yelling_at_cat"]
}
```

---

## ⚡ Performance Optimization

### Key Bottlenecks & Solutions

| Bottleneck | Solution | Impact |
|---|---|---|
| Embedding generation (~10ms) | Pre-compute during indexing; only embed queries at query time | No change at query time |
| CLIP re-ranking (slow if downloading images live) | Pre-download thumbnails to CDN; score from CDN URLs | -500ms |
| Cold vector search (Qdrant) | Keep Qdrant service warm with /health pings every 5 min | -200ms |
| Repeated identical queries | Redis cache with 1hr TTL | -1400ms (instant) |
| CLIP model loading | Load at server startup, keep in memory | One-time cost |

### Target Latency Budget
```
Query embedding generation:    10ms
Qdrant vector search:          80ms
CLIP re-ranking (10 images):  200ms
Redis read/write:               5ms
Network overhead:              50ms
─────────────────────────────────────
TOTAL:                        345ms  (well under 1.5s target ✅)

With Redis cache hit:          15ms  ✅✅
```

---

*Document Version: 1.0 | Last Updated: 2026 | Owner: Founder*
