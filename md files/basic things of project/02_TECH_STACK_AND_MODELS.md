# MemeGPT — Technology Stack & AI Models
> All tools and models used here are **100% free** unless noted with 💰 (optional paid upgrade).

---

## 🏗️ Full System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│   │  Mobile App     │  │   Web App         │  │  Landing Site   │   │
│   │  React Native   │  │   Next.js 14      │  │   Next.js 14    │   │
│   │  Expo SDK 51    │  │   app.memegpt.app │  │   memegpt.app   │   │
│   │  iOS + Android  │  │   PWA enabled     │  │   Vercel CDN    │   │
│   └────────┬────────┘  └────────┬──────────┘  └────────┬────────┘   │
└────────────┼──────────────────────────────────────────────────────────┘
             │                    │                         │
             └────────────────────┼─────────────────────────┘
                                  │ HTTPS / REST API
┌─────────────────────────────────▼────────────────────────────────────┐
│                         API LAYER                                    │
│            FastAPI (Python 3.11) — hosted on Render.com              │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │  /api/v1/search  →  /api/v1/meme/{id}  →  /api/v1/health  │    │
│   └─────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┬─┘
                                                                     │
┌────────────────────────────────────────────────────────────────────▼─┐
│                        ML / AI LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Text Embedder   │  │  Context Parser  │  │  Image Ranker   │   │
│  │  MiniLM-L6-v2   │  │  Llama 3.1-8B   │  │  CLIP ViT-B/32  │   │
│  │  (HuggingFace)   │  │  (Groq Free API) │  │  (HuggingFace)  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└────────────────────────────────────────────────────────────────────┬─┘
                                                                     │
┌────────────────────────────────────────────────────────────────────▼─┐
│                        DATA LAYER                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Qdrant Cloud    │  │  Supabase        │  │  Upstash Redis  │   │
│  │  Vector DB       │  │  PostgreSQL      │  │  Cache Layer    │   │
│  │  1GB free        │  │  Metadata store  │  │  10K ops/day    │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└────────────────────────────────────────────────────────────────────┬─┘
                                                                     │
┌────────────────────────────────────────────────────────────────────▼─┐
│                       MEDIA / CDN LAYER                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Cloudflare R2   │  │  Giphy API       │  │  Reddit API     │   │
│  │  10GB free       │  │  100 req/hr free │  │  60 req/min     │   │
│  │  GIF/Image/MP4   │  │  GIF source      │  │  Meme source    │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI / ML Models (All Free via HuggingFace)

### Model 1 — Text Embedding: `sentence-transformers/all-MiniLM-L6-v2`
| Property | Value |
|---|---|
| **Purpose** | Convert user query text → 384-dim vector |
| **Model Size** | 22 MB (tiny!) |
| **Speed** | ~10ms per query on CPU |
| **License** | Apache 2.0 — commercial use allowed |
| **HuggingFace URL** | `https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2` |
| **How Used** | Embed every incoming user query + embed meme captions during indexing |

```python
# Installation
pip install sentence-transformers

# Usage
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query_vector = model.encode("When your code works on first try")
# Output: numpy array of shape (384,)
```

**Why this model:** Fastest text embedding model at high quality. Only 22MB. 
Runs entirely on CPU — no GPU needed on server.

---

### Model 2 — Image-Text Alignment: `openai/clip-vit-base-patch32`
| Property | Value |
|---|---|
| **Purpose** | Score how well a meme image matches a text description |
| **Model Size** | 350 MB |
| **License** | MIT — commercial use allowed |
| **HuggingFace URL** | `https://huggingface.co/openai/clip-vit-base-patch32` |
| **How Used** | Re-ranking step: after vector search returns top 50, CLIP re-ranks them by image-text alignment |

```python
# Installation
pip install transformers Pillow torch torchvision

# Usage
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Score a meme image vs query text
inputs = processor(
    text=["when your code works on first try"],
    images=meme_image,
    return_tensors="pt",
    padding=True
)
outputs = model(**inputs)
clip_score = outputs.logits_per_image.item()
```

**Usage in pipeline:** Run ONLY for re-ranking top 50 candidates (not all memes). 
Loaded once in memory and cached — runs in ~50ms per batch.

---

### Model 3 — Context Understanding: `Llama-3.1-8B` via Groq API
| Property | Value |
|---|---|
| **Purpose** | Understand context, emotion, intent from user input |
| **Cost** | Free (Groq free tier: 30 req/min, 14,400 req/day) |
| **Groq URL** | `https://console.groq.com` |
| **How Used** | Optional enrichment — extract emotion, topic, humor type from query |

```python
# Groq API call
from groq import Groq

client = Groq(api_key="your_groq_api_key")

def extract_meme_context(user_query: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "system",
            "content": """Extract meme search context from the input.
            Return ONLY valid JSON with keys:
            - emotion: (string) e.g. "frustrated", "happy", "sarcastic"
            - topic: (string) e.g. "programming", "relationships", "work"
            - humor_type: (string) e.g. "relatable", "dark", "wholesome"
            - enriched_query: (string) enhanced search query"""
        }, {
            "role": "user",
            "content": user_query
        }],
        max_tokens=150,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

**Strategy:** Call this only when MiniLM search score < 0.6 (meaning the query is ambiguous). 
Cache results for identical queries in Redis. This saves API calls.

---

### Model 4 — OCR for Meme Indexing: `Tesseract OCR` (open source)
| Property | Value |
|---|---|
| **Purpose** | Extract text from meme images during indexing (offline pipeline) |
| **Cost** | Free, open source |
| **License** | Apache 2.0 |
| **How Used** | Extract caption text from every meme image in the database |

```python
# Installation
apt install tesseract-ocr
pip install pytesseract Pillow

# Usage
import pytesseract
from PIL import Image

def extract_meme_text(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config='--psm 6')
    return text.strip()
```

---

### Model 5 — Alternative Embedding: `BAAI/bge-small-en-v1.5` (Backup)
| Property | Value |
|---|---|
| **Purpose** | Backup text embedding model, slightly better quality than MiniLM |
| **Model Size** | 33 MB |
| **License** | MIT |
| **HuggingFace URL** | `https://huggingface.co/BAAI/bge-small-en-v1.5` |

Use this if MiniLM results feel less accurate in testing. Same API as sentence-transformers.

---

## 🛠️ Full Technology Stack

### Frontend — Web App & Landing Site
| Technology | Version | Purpose | Cost |
|---|---|---|---|
| **Next.js** | 14 (App Router) | Web framework (SSR + SSG) | Free |
| **React** | 18 | UI library | Free |
| **TypeScript** | 5.x | Type safety | Free |
| **Tailwind CSS** | 3.x | Styling | Free |
| **Framer Motion** | 11.x | Animations | Free |
| **React Query (TanStack)** | 5.x | Server state management | Free |
| **Zustand** | 4.x | Client state (filters, history) | Free |
| **next-seo** | 6.x | SEO meta tags management | Free |
| **next-pwa** | latest | PWA support | Free |
| **SWR** | 2.x | Data fetching / cache | Free |
| **Vercel** | — | Hosting (100GB bandwidth/month free) | Free |

### Frontend — Mobile App
| Technology | Version | Purpose | Cost |
|---|---|---|---|
| **React Native** | 0.74 | Cross-platform mobile framework | Free |
| **Expo SDK** | 51 | Build tools + native modules | Free |
| **Expo Router** | 3.x | Navigation (file-based) | Free |
| **NativeWind** | 4.x | Tailwind for React Native | Free |
| **React Native Reanimated** | 3.x | Smooth animations | Free |
| **Expo Image** | latest | Fast image loading + caching | Free |
| **Expo AV** | latest | Video/GIF playback | Free |
| **Expo Sharing** | latest | Native share sheet | Free |
| **Expo Clipboard** | latest | Copy to clipboard | Free |
| **Expo File System** | latest | Download files to device | Free |
| **EAS Build** | — | Build iOS/Android app | Free (limited) |

### Backend — API Server
| Technology | Version | Purpose | Cost |
|---|---|---|---|
| **Python** | 3.11 | Language | Free |
| **FastAPI** | 0.111 | API framework | Free |
| **Uvicorn** | 0.29 | ASGI server | Free |
| **Pydantic** | 2.x | Request/response validation | Free |
| **sentence-transformers** | 3.x | Text embeddings | Free |
| **transformers** | 4.x | CLIP model | Free |
| **torch** | 2.x (CPU only) | ML runtime | Free |
| **qdrant-client** | 1.9 | Vector DB client | Free |
| **supabase** | 2.x | Database client | Free |
| **redis** | 5.x | Cache client | Free |
| **httpx** | 0.27 | Async HTTP client for external APIs | Free |
| **Render.com** | — | Hosting (750 hrs/month free) | Free |

### Databases & Storage
| Service | Free Tier | Purpose |
|---|---|---|
| **Qdrant Cloud** | 1GB storage, 1 cluster | Vector search for memes |
| **Supabase** | 500MB DB, 1GB storage | Meme metadata, user collections |
| **Upstash Redis** | 10K commands/day, 256MB | Query result caching |
| **Cloudflare R2** | 10GB storage, 1M operations/month | Meme media files (GIF/MP4/PNG) |

### External APIs (All Free Tier)
| API | Free Limit | Used For |
|---|---|---|
| **Giphy API** | 100 req/hr | GIF meme source |
| **Tenor API** | 300 req/min | GIF meme source |
| **Reddit API** | 60 req/min | Meme scraping from r/memes etc. |
| **Imgflip API** | Unlimited (public memes) | Meme templates + top memes |
| **Groq API** | 14,400 req/day | Llama 3.1 for context parsing |

### DevOps & CI/CD
| Tool | Purpose | Cost |
|---|---|---|
| **GitHub** | Code hosting, CI/CD | Free |
| **GitHub Actions** | Automated tests + deploy | Free (2000 min/month) |
| **Vercel** | Frontend deploy + preview URLs | Free |
| **Render.com** | Backend deploy | Free |
| **Sentry** | Error tracking | Free (5K errors/month) |
| **PostHog** | Product analytics | Free (1M events/month) |

---

## 📦 App Size Management (Target: 40–100 MB)

### What Makes Apps Big (and How to Avoid It)
```
PROBLEM                    SOLUTION                          SIZE SAVED
─────────────────────────────────────────────────────────────────────────
ML models on device    →   All ML runs on server            -200 to -500MB
Bundled meme database  →   All memes fetched from CDN       -1GB+
Unused libraries       →   Tree shaking + selective import  -10 to -30MB
Unoptimized images     →   WebP + lazy load                 -5 to -20MB
Debug builds           →   Release build + Hermes engine    -15 to -30MB
```

### App Size Breakdown (Estimated)
```
React Native base runtime         ~10 MB
Expo SDK modules (selected)        ~8 MB
NativeWind + Tailwind              ~2 MB
React Native Reanimated            ~3 MB
Expo Image (caching library)       ~2 MB
Navigation (Expo Router)           ~2 MB
HTTP client + state libs           ~3 MB
Other deps (clipboard, share)      ~3 MB
App JS bundle (your code)          ~5 MB
App assets (icons, splash)         ~2 MB
────────────────────────────────────────
TOTAL ESTIMATE                   ~40 MB  ✅
```

### Expo Build Optimizations
```json
// app.json
{
  "expo": {
    "jsEngine": "hermes",
    "android": {
      "enableProguardInReleaseBuilds": true,
      "enableShrinkResourcesInReleaseBuilds": true
    },
    "ios": {
      "bitcode": false
    }
  }
}
```

---

## 🗄️ Meme Vector Schema (Qdrant Point)

Each meme stored in Qdrant looks like this:

```json
{
  "id": "meme_abc123xyz",
  "vector": [0.12, -0.34, 0.78, ...],  // 384 dimensions (MiniLM output)
  "payload": {
    "title": "When your code works on first try",
    "caption_text": "Nobody: Me when I accidentally hit undo too many times",
    "format": "gif",
    "width": 480,
    "height": 270,
    "file_size_kb": 1240,
    "media_url": "https://cdn.memegpt.app/memes/abc123.gif",
    "thumb_url": "https://cdn.memegpt.app/thumbs/abc123.jpg",
    "source": "reddit",
    "source_url": "https://reddit.com/r/ProgrammerHumor/comments/...",
    "subreddit": "ProgrammerHumor",
    "upvotes": 45234,
    "tags": ["programming", "coding", "relatable", "developer"],
    "emotion": "surprised",
    "humor_type": "relatable",
    "category": "programming",
    "clip_tags": ["person at computer", "shocked expression", "office"],
    "ocr_text": "When the code works but you don't know why",
    "language": "en",
    "is_nsfw": false,
    "created_at": "2024-01-15T10:30:00Z",
    "indexed_at": "2024-06-01T00:00:00Z",
    "view_count": 0,
    "download_count": 0
  }
}
```

**Total storage per meme:** ~2KB in Qdrant (just the vector + payload)
**100K memes:** ~200MB → well within 1GB free tier
**500K memes:** ~1GB → upgrade needed or use Pinecone free tier as overflow

---

## 💰 Complete Cost Breakdown (Monthly)

| Service | Free Tier Limit | Estimated Usage | Cost |
|---|---|---|---|
| Vercel | 100GB bandwidth | ~20GB | $0 |
| Render.com | 750 hrs/month | ~720 hrs | $0 |
| Qdrant Cloud | 1GB storage | ~200MB | $0 |
| Supabase | 500MB DB | ~100MB | $0 |
| Upstash Redis | 10K ops/day | ~8K ops/day | $0 |
| Cloudflare R2 | 10GB storage | ~5GB | $0 |
| GitHub Actions | 2000 min/month | ~500 min | $0 |
| Groq API | 14,400 req/day | ~2K req/day | $0 |
| Giphy API | 100 req/hr | ~50 req/hr | $0 |
| Reddit API | 60 req/min | ~10 req/min | $0 |
| Sentry | 5K errors/month | <100/month | $0 |
| PostHog | 1M events/month | ~100K/month | $0 |
| **TOTAL** | | | **$0/month** ✅ |

---

## 🔐 Environment Variables

```env
# Backend (.env)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_key_here
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
REDIS_URL=redis://your-upstash-url
GROQ_API_KEY=your_groq_key
GIPHY_API_KEY=your_giphy_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
CLOUDFLARE_R2_ACCESS_KEY=your_key
CLOUDFLARE_R2_SECRET_KEY=your_secret
CLOUDFLARE_R2_BUCKET=memegpt-media

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.memegpt.app
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key
```

---

*Document Version: 1.0 | Last Updated: 2026 | Owner: Founder*
