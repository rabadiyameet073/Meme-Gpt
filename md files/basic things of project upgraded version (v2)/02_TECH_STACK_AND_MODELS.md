# 02 — MemeGPT: Technology Stack & AI Models
> Everything 100% free-tier first. No costs until you scale past thousands of users.

---

## Guiding Principles

1. **Free first** — Every choice works on free tiers or is open-source
2. **CPU-friendly** — No GPU required for real-time inference
3. **Small footprint** — Models that fit in low-RAM free hosting (< 1GB)
4. **Fast inference** — Results in under 3 seconds on free hosting
5. **Proven tools** — Battle-tested libraries, not experimental ones

---

## AI / ML Models (All Free — HuggingFace)

### Model 1: Text Embedding — Core of the Search Engine
**`sentence-transformers/all-MiniLM-L6-v2`**

| Property | Value |
|---|---|
| Model Size | 80 MB |
| Output Dimensions | 384 |
| Inference Speed | ~14,000 sentences/sec (CPU) |
| License | Apache 2.0 (fully free, commercial OK) |
| HuggingFace URL | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |

**What it does:** Converts user input text into a 384-dimensional vector. This vector is then searched against all meme vectors in Qdrant to find the most semantically similar memes.

**Install + Use:**
```python
pip install sentence-transformers

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

query = "when the code works on first try and you don't know why"
embedding = model.encode(query, normalize_embeddings=True)
# Returns: numpy array of shape (384,)
```

**Why this model over others:**
- 5x faster than BERT-base with only ~2% accuracy loss
- 80MB fits easily in free Railway/Render hosting (512MB RAM)
- Excellent at semantic similarity — exactly what meme matching needs
- No API key needed — runs 100% locally

**Alternative (if better accuracy needed):**
`sentence-transformers/all-mpnet-base-v2` — 420MB, 768-dim, ~5% better accuracy

---

### Model 2: Image-Text Matching (Multimodal)
**`openai/clip-vit-base-patch32`**

| Property | Value |
|---|---|
| Model Size | 400 MB |
| Output Dimensions | 512 (image) / 512 (text) |
| License | MIT (free, commercial OK) |
| HuggingFace URL | https://huggingface.co/openai/clip-vit-base-patch32 |
| Usage Phase | **Indexing only** (not real-time inference) |

**What it does:** Given a meme image, generates a 512-dim embedding that captures visual content. Also aligns text and image in the same embedding space — so "cat shocked at vegetables" text is near the "Woman Yelling at Cat" meme image.

**When it runs:** Only during the **data ingestion pipeline** (one-time or nightly batch), NOT during user queries. This means you don't pay latency cost at runtime.

**Install + Use:**
```python
pip install transformers Pillow torch

from transformers import CLIPProcessor, CLIPModel
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Generate image embedding for a meme
image = Image.open("drake_pointing.jpg").convert("RGB")
inputs = processor(images=image, return_tensors="pt")
with torch.no_grad():
    image_features = model.get_image_features(**inputs)
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
# Returns: torch tensor of shape (1, 512)
```

---

### Model 3: Meme Caption Generation (Indexing Only)
**`Salesforce/blip-image-captioning-base`**

| Property | Value |
|---|---|
| Model Size | 446 MB |
| License | BSD-3 (free, commercial OK) |
| HuggingFace URL | https://huggingface.co/Salesforce/blip-image-captioning-base |
| Usage Phase | **Indexing only** |

**What it does:** Auto-generates a natural language caption for any meme image. "A man in a suit pointing at a TV screen" — this gets added to the meme's text metadata, which improves search quality enormously.

```python
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def caption_meme(image_path):
    img = Image.open(image_path).convert('RGB')
    inputs = processor(img, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=50)
    return processor.decode(out[0], skip_special_tokens=True)

# Example output: "a man in a business suit pointing at a television"
```

---

### Model 4: Emotion Detection
**`j-hartmann/emotion-english-distilroberta-base`**

| Property | Value |
|---|---|
| Model Size | 250 MB |
| Emotions | anger, disgust, fear, joy, neutral, sadness, surprise |
| License | MIT (free) |
| HuggingFace URL | https://huggingface.co/j-hartmann/emotion-english-distilroberta-base |
| Usage Phase | **Real-time inference** (fast — 100ms on CPU) |

**What it does:** Classifies the primary emotion in the user's input text. This emotion label is used to filter and boost memes that match the detected emotion.

```python
from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

result = emotion_classifier("I just got rejected after 5 rounds of interviews")
# Returns: [{'label': 'sadness', 'score': 0.72}, {'label': 'anger', 'score': 0.18}, ...]
```

---

### Model 5: LLM Context Parser (Free API — No GPU Needed)
**Groq API — `llama-3.1-8b-instant`**

| Property | Value |
|---|---|
| Cost | **FREE** (30 req/min, 6,000 req/day on free tier) |
| Speed | 500+ tokens/second (fastest free LLM available) |
| Signup | https://console.groq.com |
| License | Meta Llama 3.1 Community License (free for <700M MAU) |

**What it does:** Takes the raw user input and extracts structured context — emotion, situation, tone, keywords, and what format of meme they probably want. This structured output is then used to build a better search query.

```python
pip install groq

from groq import Groq
import json

client = Groq(api_key="YOUR_FREE_GROQ_KEY")

def parse_meme_intent(user_input: str) -> dict:
    prompt = f"""
You are a meme expert AI. Analyze this input and return ONLY a JSON object.

User input: "{user_input}"

Return ONLY this JSON (no explanation, no markdown):
{{
  "primary_emotion": "joy|sadness|anger|surprise|fear|disgust|neutral",
  "situation": "one short sentence describing the situation",
  "tone": "sarcastic|sincere|humorous|frustrated|excited|proud|anxious",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "meme_format_hint": "reaction|comparison|advice|relatable|wholesome|achievement|failure",
  "intensity": 0.0,
  "cultural_refs": ["any TV show, movie, game references if present"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=200
    )
    return json.loads(response.choices[0].message.content)
```

**Free Tier Alternatives (in priority order):**

| Service | Model | Free Limit | Speed |
|---|---|---|---|
| **Groq** (primary) | llama-3.1-8b-instant | 6K req/day | Ultra fast |
| Google Gemini AI | gemini-1.5-flash | 1M tokens/day | Fast |
| Cohere | command-r | 1K req/month | Medium |
| Together AI | meta-llama/Llama-3-8b | $25 free credits | Fast |
| Ollama (offline) | llama3.2:3b | Unlimited (local) | CPU speed |

**Offline fallback with Ollama (zero cost, zero API limit):**
```bash
# Install Ollama (free, open-source)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a small model
ollama pull llama3.2:3b  # 2GB download, runs on CPU

# Use in Python
import ollama
response = ollama.chat(model='llama3.2:3b', messages=[...])
```

---

### Model 6: OCR — Extract Text From Meme Images
**Tesseract OCR via `pytesseract`**

| Property | Value |
|---|---|
| Cost | Free (open-source) |
| License | Apache 2.0 |
| Usage Phase | Indexing only |

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Python
pip install pytesseract Pillow
```

```python
import pytesseract
from PIL import Image, ImageFilter

def extract_meme_text(image_path: str) -> str:
    img = Image.open(image_path)
    # Preprocess for better OCR accuracy
    img = img.convert('L')              # Grayscale
    img = img.filter(ImageFilter.SHARPEN)
    text = pytesseract.image_to_string(img, config='--psm 6')
    return text.strip()

# Example: extract "ONE DOES NOT SIMPLY / WALK INTO MORDOR"
```

---

## Complete Model Summary

| Model | Purpose | Size | Runtime | Cost |
|---|---|---|---|---|
| MiniLM-L6-v2 | Text embedding | 80 MB | Real-time | Free |
| CLIP ViT-B/32 | Image embedding | 400 MB | Indexing only | Free |
| BLIP Base | Caption generation | 446 MB | Indexing only | Free |
| Emotion DistilRoBERTa | Emotion detection | 250 MB | Real-time | Free |
| Groq Llama 3.1 8B | Intent parsing | Cloud API | Real-time | Free |
| Tesseract OCR | Text extraction | 20 MB | Indexing only | Free |

**Real-time inference RAM needed:** ~700 MB (MiniLM + Emotion model + overhead)
**Indexing RAM needed:** ~4 GB (all models loaded, run on your local machine once)

---

## Backend Stack

### Framework: FastAPI (Python 3.11)
```
Why FastAPI:
✓ Async I/O — handles concurrent requests efficiently
✓ Auto-generates OpenAPI docs at /docs
✓ Native Pydantic validation
✓ 3x faster than Flask under load
✓ Free, open-source
```

**Project dependencies:**
```txt
# requirements.txt
fastapi==0.111.0
uvicorn[standard]==0.30.0
pydantic==2.7.0
sentence-transformers==3.0.0
transformers==4.41.0
torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
Pillow==10.3.0
pytesseract==0.3.10
groq==0.9.0
qdrant-client==1.9.1
supabase==2.4.0
redis==5.0.4
python-dotenv==1.0.1
httpx==0.27.0
celery==5.4.0
boto3==1.34.0  # For Cloudflare R2
pytest==8.2.0
```

**Key backend folder structure:**
```
services/api/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       ├── search.py          # POST /search
│   │       ├── memes.py           # GET /memes/{id}
│   │       ├── trending.py        # GET /trending
│   │       ├── feedback.py        # POST /feedback
│   │       └── health.py          # GET /health
│   ├── services/
│   │   ├── embedding_service.py   # MiniLM + Emotion models
│   │   ├── llm_service.py         # Groq API calls
│   │   ├── search_service.py      # Qdrant vector search
│   │   ├── rerank_service.py      # Re-ranking logic
│   │   └── cdn_service.py         # Cloudflare R2 URLs
│   ├── models/
│   │   ├── meme.py                # Meme Pydantic schema
│   │   ├── search.py              # Search request/response
│   │   └── feedback.py            # Feedback schema
│   └── core/
│       ├── config.py              # Settings from .env
│       ├── cache.py               # Redis caching
│       └── rate_limit.py          # Rate limiting middleware
├── scripts/
│   ├── download_datasets.py
│   ├── preprocess_memes.py
│   ├── generate_embeddings.py
│   └── index_qdrant.py
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Frontend — Web App

### Framework: Next.js 14 (App Router)

| Component | Technology | Why |
|---|---|---|
| Framework | Next.js 14 | SSR + SSG = great SEO, fast, free on Vercel |
| Styling | Tailwind CSS | Utility-first, tiny CSS bundle |
| Animations | Framer Motion | Smooth meme card animations |
| Icons | Lucide React | Free icon library |
| Data Fetching | TanStack Query v5 | Caching, background refetch, optimistic UI |
| Global State | Zustand | Lightweight (< 1KB), no boilerplate |
| Auth | NextAuth.js | Free, OAuth (Google, GitHub) |
| Forms | React Hook Form | No re-renders, fast |
| Analytics | Umami (self-hosted) | Free, privacy-friendly |
| Error Tracking | Sentry (free tier) | 5K errors/month free |

**Next.js folder structure:**
```
apps/web/
├── app/
│   ├── (marketing)/          # Landing site routes
│   │   ├── page.tsx           # Homepage (/)
│   │   ├── layout.tsx
│   │   ├── download/
│   │   │   └── page.tsx       # /download
│   │   ├── features/
│   │   │   └── page.tsx       # /features
│   │   └── blog/
│   │       ├── page.tsx       # /blog (meme list)
│   │       └── [slug]/
│   │           └── page.tsx   # /blog/monday-memes
│   ├── (app)/                # Web app routes (authenticated)
│   │   ├── layout.tsx
│   │   ├── page.tsx           # /app — chat interface
│   │   ├── library/
│   │   │   └── page.tsx       # /app/library
│   │   └── trending/
│   │       └── page.tsx       # /app/trending
│   ├── meme/
│   │   └── [slug]/
│   │       └── page.tsx       # /meme/drake-pointing (SEO pages)
│   ├── layout.tsx             # Root layout with metadata
│   └── sitemap.ts             # Auto-generated sitemap
├── components/
│   ├── ui/                    # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   ├── meme/
│   │   ├── MemeCard.tsx       # Individual meme result card
│   │   ├── MemeGrid.tsx       # Grid of meme results
│   │   ├── FormatBadges.tsx   # GIF / PNG / MP4 format buttons
│   │   ├── DownloadButton.tsx
│   │   └── ShareModal.tsx
│   ├── search/
│   │   ├── SearchInput.tsx    # Main text input
│   │   ├── SearchHistory.tsx
│   │   └── FormatSelector.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Sidebar.tsx
├── lib/
│   ├── api.ts                 # API client functions
│   └── utils.ts
├── public/
│   ├── og-image.jpg           # OG meta image
│   └── icons/
├── tailwind.config.ts
├── next.config.ts
└── package.json
```

---

## Mobile App Stack

### Framework: React Native 0.74 (with Expo SDK 51)

| Component | Technology | Notes |
|---|---|---|
| Framework | React Native + Expo | Cross-platform, one codebase |
| Navigation | Expo Router (file-based) | Same pattern as Next.js |
| UI Components | React Native Paper | Material Design, free |
| Animations | React Native Reanimated v3 | Silky 60fps |
| Images | Expo Image | Optimized caching |
| Storage | MMKV | 10x faster than AsyncStorage |
| HTTP | Axios | Simple, reliable |
| Share | Expo Sharing | Native share sheet (WhatsApp etc.) |
| Downloads | Expo FileSystem | Save GIF/PNG to camera roll |
| Build | EAS Build (Expo) | Free tier: 30 builds/month |
| OTA Updates | Expo Updates | Push JS updates without app store |

**App size breakdown:**
```
React Native runtime (Hermes):   15 MB
JavaScript bundle (minified):     4 MB
Expo modules:                     8 MB
App assets (icons, fonts):        2 MB
────────────────────────────────────
Total APK/IPA:                  ~29 MB   ✅ Under 40 MB goal
```

**React Native folder structure:**
```
apps/mobile/
├── app/
│   ├── (tabs)/
│   │   ├── index.tsx          # Home / Search tab
│   │   ├── trending.tsx       # Trending tab
│   │   └── library.tsx        # Saved memes tab
│   ├── meme/
│   │   └── [id].tsx           # Meme detail screen
│   └── _layout.tsx
├── components/
│   ├── MemeCard.tsx
│   ├── SearchBar.tsx
│   └── FormatPicker.tsx
├── hooks/
│   ├── useMemeSearch.ts
│   └── useDownload.ts
├── lib/
│   └── api.ts
├── assets/
├── app.json                   # Expo config
└── package.json
```

---

## Data Storage Architecture

### 1. Vector Database — Qdrant
**For:** Storing meme embeddings + semantic search

```
Free tier: 1GB storage, 1,000,000 vectors
Signup: https://cloud.qdrant.io

Collections:
- "memes" collection:
  - "text" vector: 384-dim (MiniLM)
  - "image" vector: 512-dim (CLIP)
  - Payload: name, image_url, gif_url, emotions, categories, nsfw, popularity
```

### 2. SQL Database — Supabase (PostgreSQL)
**For:** User accounts, feedback, meme metadata, analytics

```
Free tier: 500MB storage, 2GB bandwidth
Signup: https://supabase.com

Tables:
- users (id, email, created_at, preferences)
- memes (id, name, slug, categories, created_at, view_count)
- feedback (id, user_id, meme_id, query_text, action, created_at)
- saved_memes (id, user_id, meme_id, collection_name, created_at)
- search_logs (id, query, results, latency_ms, created_at)
```

### 3. Object Storage — Cloudflare R2
**For:** Meme files (GIF, PNG, MP4, WebP)

```
Free tier: 10GB storage, 10GB egress/month
Signup: https://dash.cloudflare.com → R2

Bucket structure:
memegpt-memes/
├── images/
│   ├── drake-pointing.jpg
│   └── ...
├── gifs/
│   ├── drake-pointing.gif
│   └── ...
├── videos/
│   └── ...
└── thumbs/    (WebP thumbnails, 200x200px)
    └── ...
```

### 4. Cache — Upstash Redis
**For:** Caching frequent search results, rate limiting

```
Free tier: 10,000 commands/day
Signup: https://upstash.com

Cache keys:
- search:{hash_of_query} → TTL 1 hour
- trending:{category} → TTL 30 minutes
- meme:{id} → TTL 24 hours
- ratelimit:{ip} → TTL 1 minute
```

---

## Free APIs and Data Sources

| Source | Data | Free Limit | URL |
|---|---|---|---|
| Imgflip API | Top 100 meme templates + generation | Unlimited GET | https://api.imgflip.com/get_memes |
| Tenor (Google) | Animated GIFs | 300 req/min | https://developers.google.com/tenor |
| Giphy API | GIFs | 42 req/hour | https://developers.giphy.com |
| Reddit JSON API | r/memes posts | No key needed | reddit.com/r/memes.json |
| HuggingFace Datasets | reddit-meme-dataset | Free download | huggingface.co/datasets |
| Know Your Meme | Meme metadata | Scraping | knowyourmeme.com |

---

## Infrastructure & Hosting (All Free Tier)

| Service | Free Allowance | Use In Project |
|---|---|---|
| **Vercel** | 100GB bandwidth, unlimited deploys | Web app + landing site |
| **Railway** | $5/month credit (≈ 500 hours) | FastAPI backend |
| **Supabase** | 500MB DB, 2GB bandwidth | PostgreSQL database |
| **Qdrant Cloud** | 1GB, 1M vectors | Vector search |
| **Cloudflare R2** | 10GB storage, 10GB egress | Meme file storage |
| **Upstash** | 10K Redis commands/day | Caching |
| **Groq** | 6K LLM requests/day | LLM inference |
| **Expo EAS** | 30 builds/month | Mobile app builds |
| **GitHub Actions** | 2,000 minutes/month | CI/CD pipeline |
| **Sentry** | 5K errors/month | Error monitoring |
| **Resend** | 3K emails/month | Transactional email |
| **Total Cost** | **$0/month** | At MVP scale |

---

## Development Environment Setup

```bash
# Prerequisites
node >= 20.0.0
python >= 3.11
git

# Clone repo
git clone https://github.com/yourusername/memegpt
cd memegpt

# Backend setup
cd services/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your free API keys
uvicorn app.main:app --reload --port 8000

# Web app setup
cd apps/web
npm install
cp .env.local.example .env.local
npm run dev  # Runs at localhost:3000

# Mobile app setup
cd apps/mobile
npm install
npx expo start  # Scan QR with Expo Go app

# Run all tests
cd services/api && pytest
cd apps/web && npm test
```
