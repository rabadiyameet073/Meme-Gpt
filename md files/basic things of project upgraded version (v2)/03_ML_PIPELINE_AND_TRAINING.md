# 03 — MemeGPT: ML Pipeline, Vector Embeddings & Training
> How to collect, process, embed, index, and serve memes with AI — step by step.

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   OFFLINE PIPELINE (Run Once / Nightly)             │
│                                                                     │
│  DATA SOURCES                                                       │
│  Imgflip API + Reddit Dataset + Tenor API + Manual curation         │
│           │                                                         │
│           ▼                                                         │
│  DOWNLOAD & STORE                                                   │
│  Download images/GIFs → Cloudflare R2                               │
│           │                                                         │
│           ▼                                                         │
│  PREPROCESSING                                                      │
│  OCR (text extraction) + BLIP (caption) + Tesseract + Tag generation│
│           │                                                         │
│           ▼                                                         │
│  EMBEDDING GENERATION                                               │
│  MiniLM (text embed) + CLIP (image embed) → Combined 896-dim vector │
│           │                                                         │
│           ▼                                                         │
│  VECTOR INDEXING                                                    │
│  Upsert all vectors + metadata into Qdrant                          │
│           │                                                         │
│           ▼                                                         │
│  METADATA STORAGE                                                   │
│  Store meme records in Supabase PostgreSQL                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ONLINE PIPELINE (Per User Request)                │
│                                                                     │
│  USER INPUT: "I fixed a bug that took me 3 days in 5 minutes"       │
│           │                                                         │
│           ▼                                                         │
│  INTENT PARSING (Groq API — ~300ms)                                 │
│  → {emotion: "joy", situation: "solved hard problem fast", ...}     │
│           │                                                         │
│           ▼                                                         │
│  EMOTION DETECTION (DistilRoBERTa — local, ~100ms)                  │
│  → primary: "joy", secondary: "surprise"                            │
│           │                                                         │
│           ▼                                                         │
│  QUERY BUILDING                                                     │
│  Combine intent + emotion into rich query text                      │
│           │                                                         │
│           ▼                                                         │
│  QUERY EMBEDDING (MiniLM — local, ~50ms)                            │
│  → 384-dim vector                                                   │
│           │                                                         │
│           ▼                                                         │
│  VECTOR SEARCH (Qdrant — ~50ms)                                     │
│  → Top 10 similar memes by cosine similarity                        │
│           │                                                         │
│           ▼                                                         │
│  RE-RANKING (Python — ~10ms)                                        │
│  → Apply popularity, emotion match, format boost                    │
│           │                                                         │
│           ▼                                                         │
│  RESPONSE (< 1.5s total)                                            │
│  → Top 5 meme results with CDN URLs                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Data Collection

### Script: `scripts/download_datasets.py`

```python
"""
Download all meme data from free sources.
Run once to build the initial dataset.
"""
import os
import json
import requests
from pathlib import Path
from datasets import load_dataset

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── SOURCE 1: Imgflip Top 100 Templates ───────────────────────────
def download_imgflip():
    """Free API — no key needed. Returns top 100 popular meme templates."""
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    memes = response.json()["data"]["memes"]
    
    results = []
    for meme in memes:
        # Download the image
        img_response = requests.get(meme["url"])
        img_path = OUTPUT_DIR / f"images/{meme['id']}.jpg"
        img_path.parent.mkdir(exist_ok=True)
        img_path.write_bytes(img_response.content)
        
        results.append({
            "id": f"imgflip_{meme['id']}",
            "name": meme["name"],
            "source": "imgflip",
            "image_path": str(img_path),
            "image_url": meme["url"],
            "box_count": meme["box_count"],  # Number of text boxes
        })
    
    print(f"✓ Downloaded {len(results)} Imgflip templates")
    return results

# ─── SOURCE 2: HuggingFace Reddit Meme Dataset ─────────────────────
def download_reddit_dataset():
    """6500+ memes with Reddit metadata."""
    dataset = load_dataset("headsmanjaeger/reddit-meme-dataset", split="train")
    
    results = []
    for item in dataset:
        # Note: URLs only, actual download done separately
        results.append({
            "id": f"reddit_{item['id']}",
            "name": item.get("title", ""),
            "source": "reddit",
            "image_url": item.get("url", ""),
            "subreddit": item.get("subreddit", ""),
            "score": item.get("score", 0),
        })
    
    print(f"✓ Loaded {len(results)} Reddit memes")
    return results

# ─── SOURCE 3: Tenor GIF API ────────────────────────────────────────
def download_tenor_gifs(api_key: str, categories: list):
    """Animated GIFs for popular meme categories."""
    results = []
    
    for category in categories:
        url = f"https://tenor.googleapis.com/v2/search"
        params = {"q": f"{category} meme", "key": api_key, "limit": 50, "media_filter": "gif"}
        response = requests.get(url, params=params)
        
        for item in response.json().get("results", []):
            gif_url = item["media_formats"]["gif"]["url"]
            results.append({
                "id": f"tenor_{item['id']}",
                "name": item.get("title", category),
                "source": "tenor",
                "gif_url": gif_url,
                "category": category,
            })
    
    print(f"✓ Downloaded {len(results)} Tenor GIFs")
    return results

# ─── MAIN ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    all_memes = []
    all_memes.extend(download_imgflip())
    all_memes.extend(download_reddit_dataset())
    
    # Save master list
    with open("data/raw/memes_master.json", "w") as f:
        json.dump(all_memes, f, indent=2)
    
    print(f"\n✅ Total memes collected: {len(all_memes)}")
```

---

## Step 2: Preprocessing

### Script: `scripts/preprocess_memes.py`

```python
"""
For each meme:
1. Extract text (OCR)
2. Generate caption (BLIP)
3. Detect emotions/tags (Groq LLM)
4. Build rich text description
"""
import json
import pytesseract
from PIL import Image, ImageFilter
from transformers import BlipProcessor, BlipForConditionalGeneration
from groq import Groq
import torch

# Load BLIP model (446MB — runs once)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

def extract_text_ocr(image_path: str) -> str:
    """Extract text overlaid on meme image."""
    try:
        img = Image.open(image_path).convert('L')
        img = img.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, config='--psm 6 --oem 3')
        return text.strip()
    except Exception:
        return ""

def generate_caption_blip(image_path: str) -> str:
    """Generate natural language description of the meme image."""
    try:
        img = Image.open(image_path).convert('RGB')
        inputs = blip_processor(img, return_tensors="pt")
        with torch.no_grad():
            out = blip_model.generate(**inputs, max_new_tokens=60)
        return blip_processor.decode(out[0], skip_special_tokens=True)
    except Exception:
        return ""

def generate_meme_tags(name: str, ocr_text: str, caption: str) -> dict:
    """Use Groq LLM to generate rich semantic tags for the meme."""
    prompt = f"""
Meme name: {name}
Text visible in meme: {ocr_text}
Image description: {caption}

Generate meme metadata. Return ONLY this JSON:
{{
  "emotions": ["joy", "surprise"],
  "situations": ["winning unexpected", "software bug fixed"],
  "tone": "humorous",
  "keywords": ["victory", "celebration", "unexpected win"],
  "cultural_refs": [],
  "meme_type": "reaction",
  "best_for": ["when something finally works", "unexpected success"]
}}
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"emotions": [], "situations": [], "tone": "neutral", "keywords": [], "best_for": []}

def build_meme_text_description(meme: dict, tags: dict) -> str:
    """
    Build a comprehensive text representation of the meme.
    This is what gets embedded by MiniLM.
    The richer this text, the better the search quality.
    """
    parts = [
        f"Meme: {meme['name']}",
        f"Description: {meme.get('caption', '')}",
        f"Text on image: {meme.get('ocr_text', '')}",
        f"Emotions: {', '.join(tags.get('emotions', []))}",
        f"Situations: {', '.join(tags.get('situations', []))}",
        f"Keywords: {', '.join(tags.get('keywords', []))}",
        f"Best used for: {', '.join(tags.get('best_for', []))}",
        f"Meme type: {tags.get('meme_type', '')}",
    ]
    return "\n".join(p for p in parts if p.split(": ")[1].strip())

def preprocess_all_memes():
    with open("data/raw/memes_master.json") as f:
        raw_memes = json.load(f)
    
    processed = []
    for i, meme in enumerate(raw_memes):
        print(f"Processing {i+1}/{len(raw_memes)}: {meme['name']}")
        
        image_path = meme.get("image_path", "")
        ocr_text = extract_text_ocr(image_path) if image_path else ""
        caption = generate_caption_blip(image_path) if image_path else ""
        tags = generate_meme_tags(meme["name"], ocr_text, caption)
        text_description = build_meme_text_description(
            {**meme, "ocr_text": ocr_text, "caption": caption}, tags
        )
        
        processed.append({
            **meme,
            "ocr_text": ocr_text,
            "caption": caption,
            "tags": tags,
            "text_description": text_description,
            "emotions": tags.get("emotions", []),
            "situations": tags.get("situations", []),
            "keywords": tags.get("keywords", []),
            "meme_type": tags.get("meme_type", ""),
        })
    
    with open("data/processed/memes_processed.json", "w") as f:
        json.dump(processed, f, indent=2)
    
    print(f"✅ Preprocessed {len(processed)} memes")

if __name__ == "__main__":
    preprocess_all_memes()
```

---

## Step 3: Embedding Generation

### Script: `scripts/generate_embeddings.py`

```python
"""
Generate text + image embeddings for all preprocessed memes.
These become the searchable vectors in Qdrant.
"""
import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
from PIL import Image

# Load models
text_model = SentenceTransformer('all-MiniLM-L6-v2')  # 80MB
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")   # 400MB
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_text_embedding(text: str) -> list[float]:
    """384-dimensional text embedding."""
    embedding = text_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def get_image_embedding(image_path: str) -> list[float]:
    """512-dimensional CLIP image embedding."""
    try:
        img = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            features = clip_model.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
        return features[0].tolist()
    except Exception:
        return [0.0] * 512

def get_combined_embedding(
    text_emb: list[float],
    image_emb: list[float],
    text_weight: float = 0.65,
    image_weight: float = 0.35
) -> list[float]:
    """
    Weighted combination: text contributes 65%, image 35%.
    Text gets higher weight because meme search is primarily semantic.
    Combined dimension: 384 + 512 = 896.
    """
    text_arr = np.array(text_emb) * text_weight
    image_arr = np.array(image_emb) * image_weight
    
    combined = np.concatenate([text_arr, image_arr])
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    
    return combined.tolist()

def generate_all_embeddings():
    with open("data/processed/memes_processed.json") as f:
        memes = json.load(f)
    
    for i, meme in enumerate(memes):
        print(f"Embedding {i+1}/{len(memes)}: {meme['name']}")
        
        # Text embedding from rich description
        text_emb = get_text_embedding(meme["text_description"])
        
        # Image embedding (if local image exists)
        image_emb = get_image_embedding(meme.get("image_path", ""))
        
        # Combined embedding
        combined_emb = get_combined_embedding(text_emb, image_emb)
        
        meme["text_embedding"] = text_emb        # 384-dim
        meme["image_embedding"] = image_emb      # 512-dim
        meme["combined_embedding"] = combined_emb  # 896-dim (normalized)
    
    with open("data/embeddings/memes_with_embeddings.json", "w") as f:
        json.dump(memes, f)
    
    print(f"✅ Generated embeddings for {len(memes)} memes")

if __name__ == "__main__":
    generate_all_embeddings()
```

---

## Step 4: Vector Indexing in Qdrant

### Script: `scripts/index_qdrant.py`

```python
"""
Create Qdrant collection and upsert all meme embeddings.
Run after generate_embeddings.py
"""
import json
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    CreateCollection, HnswConfigDiff
)

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"]
)

COLLECTION_NAME = "memes"

def create_collection():
    """
    Create meme collection with 3 named vector spaces.
    text: for semantic search
    image: for visual search
    combined: for hybrid search (default)
    """
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "text": VectorParams(
                size=384,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100)
            ),
            "image": VectorParams(
                size=512,
                distance=Distance.COSINE,
            ),
            "combined": VectorParams(
                size=896,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=32, ef_construct=200)
            ),
        }
    )
    print(f"✓ Created collection '{COLLECTION_NAME}'")

def index_memes(batch_size: int = 100):
    """Upsert memes in batches for efficiency."""
    with open("data/embeddings/memes_with_embeddings.json") as f:
        memes = json.load(f)
    
    for batch_start in range(0, len(memes), batch_size):
        batch = memes[batch_start:batch_start + batch_size]
        
        points = []
        for meme in batch:
            # Qdrant requires integer or UUID IDs
            # Hash the string ID to a consistent integer
            point_id = abs(hash(meme["id"])) % (10**18)
            
            point = PointStruct(
                id=point_id,
                vectors={
                    "text": meme["text_embedding"],
                    "image": meme["image_embedding"],
                    "combined": meme["combined_embedding"],
                },
                payload={
                    # All searchable/filterable metadata stored here
                    "meme_id": meme["id"],
                    "name": meme["name"],
                    "slug": meme["name"].lower().replace(" ", "-"),
                    "emotions": meme.get("emotions", []),
                    "situations": meme.get("situations", []),
                    "keywords": meme.get("keywords", []),
                    "meme_type": meme.get("meme_type", "reaction"),
                    "source": meme.get("source", ""),
                    "image_url": meme.get("image_url", ""),
                    "gif_url": meme.get("gif_url", ""),
                    "mp4_url": meme.get("mp4_url", ""),
                    "thumb_url": meme.get("thumb_url", ""),
                    "has_gif": bool(meme.get("gif_url")),
                    "has_video": bool(meme.get("mp4_url")),
                    "nsfw": meme.get("nsfw", False),
                    "popularity_score": min(1.0, meme.get("score", 0) / 10000),
                    "view_count": 0,
                    "download_count": 0,
                }
            )
            points.append(point)
        
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  Indexed batch {batch_start}–{batch_start + len(batch)}")
    
    print(f"✅ Indexed {len(memes)} memes in Qdrant")

def verify_index():
    """Confirm the index is working."""
    info = client.get_collection(COLLECTION_NAME)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Vectors count: {info.vectors_count}")
    print(f"Status: {info.status}")
    
    # Test search
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    test_query = "when the code finally works"
    test_vector = model.encode(test_query, normalize_embeddings=True).tolist()
    
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=("text", test_vector),
        limit=3
    )
    
    print(f"\nTest search: '{test_query}'")
    for r in results:
        print(f"  Score: {r.score:.3f} | Meme: {r.payload['name']}")

if __name__ == "__main__":
    create_collection()
    index_memes()
    verify_index()
```

---

## Step 5: Real-Time Recommendation Service

### `app/services/recommendation.py`

```python
"""
Core recommendation engine — called for every user request.
Target latency: < 1.5 seconds total.
"""
import json
import hashlib
from groq import Groq
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
import redis

# ─── Model initialization (loaded once at startup) ──────────────────
text_model = SentenceTransformer('all-MiniLM-L6-v2')

emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
cache = redis.from_url(os.environ["UPSTASH_REDIS_URL"])

# ─── Step A: Parse Intent with LLM ──────────────────────────────────
async def parse_intent(user_text: str) -> dict:
    """Groq inference: ~200-400ms"""
    prompt = f"""Analyze this text for meme recommendation. Return ONLY JSON:
"{user_text}"

{{
  "situation": "concise one-sentence situation description",
  "emotion_hint": "joy|sadness|anger|surprise|fear|disgust|neutral",
  "tone": "sarcastic|sincere|humorous|frustrated|excited|proud|anxious|relatable",
  "keywords": ["word1", "word2"],
  "meme_format": "reaction|comparison|advice|relatable|wholesome|achievement|failure",
  "intensity": 0.7
}}"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=200
    )
    return json.loads(response.choices[0].message.content)

# ─── Step B: Detect Emotion Locally ─────────────────────────────────
def detect_emotion(text: str) -> dict:
    """Local model inference: ~100ms"""
    results = emotion_pipeline(text[:512])[0]  # Truncate for speed
    # Sort by score and return top 2
    sorted_emotions = sorted(results, key=lambda x: x['score'], reverse=True)
    return {
        "primary": sorted_emotions[0]["label"],
        "secondary": sorted_emotions[1]["label"] if len(sorted_emotions) > 1 else None,
        "confidence": sorted_emotions[0]["score"]
    }

# ─── Step C: Build Query Text ────────────────────────────────────────
def build_query_text(user_text: str, intent: dict, emotion: dict) -> str:
    """
    Combine original input + LLM parsed intent + detected emotion
    into a single rich text for embedding.
    """
    return f"""
User said: {user_text}
Situation: {intent.get('situation', '')}
Emotion: {emotion['primary']}, {emotion.get('secondary', '')}
Tone: {intent.get('tone', '')}
Keywords: {', '.join(intent.get('keywords', []))}
Meme type needed: {intent.get('meme_format', 'reaction')}
""".strip()

# ─── Step D: Vector Search in Qdrant ─────────────────────────────────
def vector_search(
    query_vector: list[float],
    emotion: str,
    format_pref: str = "any",
    nsfw: bool = False,
    top_k: int = 10
) -> list:
    """Qdrant search with filters: ~30-60ms"""
    
    # Build filter conditions
    conditions = [
        FieldCondition(key="nsfw", match=MatchValue(value=nsfw))
    ]
    
    if format_pref == "gif":
        conditions.append(FieldCondition(key="has_gif", match=MatchValue(value=True)))
    elif format_pref == "video":
        conditions.append(FieldCondition(key="has_video", match=MatchValue(value=True)))
    
    search_filter = Filter(must=conditions)
    
    results = qdrant.search(
        collection_name="memes",
        query_vector=("text", query_vector),  # Use text vector space
        query_filter=search_filter,
        limit=top_k,
        with_payload=True,
        score_threshold=0.45  # Min similarity — adjust based on dataset
    )
    
    return results

# ─── Step E: Re-rank Results ─────────────────────────────────────────
def rerank(
    results: list,
    intent: dict,
    emotion: dict,
    format_pref: str = "any"
) -> list:
    """
    Apply business logic re-ranking on top of vector similarity scores.
    Small adjustments that make a big difference in result quality.
    """
    scored = []
    
    for r in results:
        payload = r.payload
        score = r.score  # Cosine similarity (0.0 – 1.0)
        
        # +15% if detected emotion matches meme's emotion tags
        if emotion["primary"] in payload.get("emotions", []):
            score += 0.15
        
        # +8% for secondary emotion match
        if emotion.get("secondary") in payload.get("emotions", []):
            score += 0.08
        
        # +10% popularity boost (weighted by actual usage)
        popularity = payload.get("popularity_score", 0)
        score += popularity * 0.10
        
        # +5% if user prefers GIF and meme has GIF
        if format_pref == "gif" and payload.get("has_gif"):
            score += 0.05
        
        # -10% for very old memes (if we track freshness in Phase 2)
        # score -= staleness_penalty(payload)
        
        scored.append({
            "meme": payload,
            "score": min(score, 1.0),  # Cap at 1.0
            "vector_score": r.score
        })
    
    # Sort by final score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:5]  # Return top 5

# ─── Main Entry Point ─────────────────────────────────────────────────
async def recommend_memes(
    user_text: str,
    format_pref: str = "gif",
    nsfw: bool = False,
    session_id: str = None
) -> list[dict]:
    """
    Full recommendation pipeline.
    Returns top 5 meme recommendations.
    """
    import time
    start = time.time()
    
    # Cache check (hash the query for cache key)
    cache_key = f"search:{hashlib.md5(f'{user_text}:{format_pref}:{nsfw}'.encode()).hexdigest()}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # A: Parse intent (LLM)
    intent = await parse_intent(user_text)         # ~300ms
    
    # B: Detect emotion (local model)
    emotion = detect_emotion(user_text)             # ~100ms
    
    # C: Build rich query text
    query_text = build_query_text(user_text, intent, emotion)
    
    # D: Generate query embedding
    query_vector = text_model.encode(             # ~50ms
        query_text, normalize_embeddings=True
    ).tolist()
    
    # E: Vector search
    results = vector_search(                        # ~50ms
        query_vector, emotion["primary"],
        format_pref, nsfw
    )
    
    # F: Re-rank
    final_results = rerank(results, intent, emotion, format_pref)
    
    # Cache for 1 hour
    cache.setex(cache_key, 3600, json.dumps(final_results))
    
    elapsed = time.time() - start
    print(f"Recommendation completed in {elapsed:.2f}s")
    
    return final_results
```

---

## Step 6: Feedback Loop & Continuous Improvement

### Signal Collection
Every user interaction is tracked (anonymously):

```python
# Signals we collect
SIGNAL_WEIGHTS = {
    "view":      0.1,   # Saw the result
    "click":     0.5,   # Clicked to expand
    "copy":      1.0,   # Copied the image
    "download":  2.0,   # Downloaded the meme
    "share":     3.0,   # Shared via link
    "thumbs_up": 2.0,   # Explicit positive
    "thumbs_down": -1.0, # Explicit negative
    "skip":      -0.3,  # Scrolled past without interaction
}
```

### Weekly Retraining Cycle
Every Sunday at midnight (automated via GitHub Actions):

```
1. Pull last week's feedback from PostgreSQL
2. Calculate new popularity_scores for each meme
3. Update Qdrant payload (fast, no re-indexing)
4. Generate "hard negative" pairs: {query, rejected_meme}
5. Generate "positive" pairs: {query, downloaded_meme}
6. (Phase 2) Fine-tune MiniLM on these pairs using contrastive loss
7. Run evaluation on held-out test set
8. Deploy new model if metrics improve
```

---

## Evaluation Metrics

### Offline Metrics (test dataset)

| Metric | Formula | Target | How to Measure |
|---|---|---|---|
| **Precision@3** | Relevant memes in top-3 ÷ 3 | > 0.70 | Human labelers rate top-3 |
| **Recall@10** | Relevant memes in top-10 ÷ all relevant | > 0.85 | Exhaustive labeling |
| **NDCG@5** | Normalized Discounted Cumulative Gain | > 0.75 | Standard IR metric |
| **MRR** | Mean Reciprocal Rank of first relevant result | > 0.80 | First hit ranking |

### Online Metrics (production)

| Metric | Target | Measurement |
|---|---|---|
| **Click-Through Rate (CTR)** | > 30% | Clicks ÷ Impressions |
| **Download Rate** | > 15% | Downloads ÷ Clicks |
| **Session Success Rate** | > 60% | Sessions with ≥1 interaction |
| **Response Latency P50** | < 1.0s | Server-side timing |
| **Response Latency P95** | < 3.0s | Server-side timing |
| **Cache Hit Ratio** | > 50% | Redis hits ÷ total requests |
| **Thumbs Up Rate** | > 75% | Upvotes ÷ total votes |
| **User Return Rate** | > 40% | D7 retention |

### Evaluation Script
```bash
# Run weekly evaluation
python scripts/evaluate.py \
  --test-file data/eval/test_queries.json \
  --k 3 5 10 \
  --output reports/eval_$(date +%Y%m%d).json
```

---

## Scaling the Dataset Over Time

| Phase | Meme Count | Search Quality | Resources Needed |
|---|---|---|---|
| MVP (Week 1) | 1,000 | Basic — top memes only | Local machine, 30 min |
| Phase 1 | 5,000 | Good — covers 80% of use cases | Local machine, 2 hours |
| Phase 2 | 25,000 | Very good — niche topics covered | Local machine, 8 hours |
| Phase 3 | 100,000 | Excellent | Free tier GPU (Colab) |
| Scale | 500,000+ | Comprehensive | Paid GPU |

### Quick Start: Get to 1,000 Memes in 30 Minutes
```bash
# Step 1: Download top 100 Imgflip templates (5 min)
python scripts/download_datasets.py --source imgflip

# Step 2: Preprocess with LLM tags (15 min, uses Groq free tier)
python scripts/preprocess_memes.py --batch-size 10

# Step 3: Generate embeddings (5 min, CPU)
python scripts/generate_embeddings.py

# Step 4: Index in Qdrant (2 min)
python scripts/index_qdrant.py

# Step 5: Test search
python scripts/verify_index.py
# → Expected: "when code works" → returns "Success Kid" or "This Is Fine" meme
```
