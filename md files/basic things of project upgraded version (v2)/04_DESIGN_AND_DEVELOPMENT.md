# 04 — MemeGPT: System Architecture, Design & Development Guide
> Complete blueprint for solo development — architecture diagrams, API contracts, UI spec, and build order.

---

## Full System Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                        CLIENT LAYER                                 ║
║                                                                     ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐    ║
║  │  Next.js Web App │  │  React Native   │  │  Landing Website │    ║
║  │  (app.memegpt)  │  │  iOS + Android  │  │  (memegpt.com)   │    ║
║  │  Hosted: Vercel │  │  EAS Build      │  │  Hosted: Vercel  │    ║
║  └────────┬────────┘  └───────┬─────────┘  └────────┬─────────┘    ║
╚═══════════╪═══════════════════╪════════════════════════╪════════════╝
            │                  │                         │
            └──────────────────┼─────────────────────────┘
                               │ HTTPS REST API
                               ▼
╔══════════════════════════════════════════════════════════════════════╗
║                      API GATEWAY LAYER                              ║
║                                                                     ║
║              FastAPI (Python 3.11) — Hosted: Railway                ║
║                                                                     ║
║  ┌──────────────────────────────────────────────────────────────┐   ║
║  │  Middleware: CORS │ Rate Limiting │ Auth │ Request Logging   │   ║
║  └──────────────────────────────────────────────────────────────┘   ║
║                                                                     ║
║  POST /api/v1/search    GET /api/v1/memes/{id}    GET /trending     ║
║  POST /api/v1/feedback  GET /api/v1/memes/{id}/download             ║
╚══════════════════════╦═══════════════════════════════════════════════╝
                       ║
          ┌────────────╩────────────┐
          ▼                         ▼
╔═════════════════════╗  ╔══════════════════════════════════╗
║  ML INFERENCE LAYER ║  ║         EXTERNAL APIS            ║
║                     ║  ║                                  ║
║  ┌───────────────┐  ║  ║  Groq API (LLM context parsing) ║
║  │  MiniLM       │  ║  ║  Tenor API  (GIF search)        ║
║  │  (text embed) │  ║  ║  Imgflip API (meme templates)   ║
║  └───────────────┘  ║  ╚══════════════════════════════════╝
║  ┌───────────────┐  ║
║  │  Emotion      │  ║
║  │  Classifier   │  ║
║  └───────────────┘  ║
╚════════════╦════════╝
             ║
             ▼
╔══════════════════════════════════════════════════════════════════════╗
║                       DATA LAYER                                    ║
║                                                                     ║
║  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────────┐  ║
║  │  Qdrant Cloud   │  │  Supabase    │  │  Cloudflare R2 + CDN   │  ║
║  │  (Vector DB)    │  │ (PostgreSQL) │  │  (Meme Files)          │  ║
║  │  1M vectors free│  │  User data   │  │  GIF / PNG / MP4       │  ║
║  └─────────────────┘  │  Feedback    │  │  WebP thumbnails       │  ║
║                       │  Analytics   │  └────────────────────────┘  ║
║  ┌─────────────────┐  └──────────────┘                              ║
║  │  Upstash Redis  │                                                ║
║  │  (Cache layer)  │                                                ║
║  │  TTL: 1hr–24hr  │                                                ║
║  └─────────────────┘                                                ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Complete Project Repository Structure

```
memegpt/
├── apps/
│   ├── web/                           # Next.js web app + landing
│   │   ├── app/
│   │   │   ├── (marketing)/           # Public landing pages
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx           # Homepage — memegpt.com
│   │   │   │   ├── download/
│   │   │   │   │   └── page.tsx       # App download page
│   │   │   │   ├── features/
│   │   │   │   │   └── page.tsx       # Features page
│   │   │   │   └── blog/
│   │   │   │       ├── page.tsx       # Blog index
│   │   │   │       └── [slug]/
│   │   │   │           └── page.tsx   # Individual blog post
│   │   │   ├── (app)/                 # Authenticated web app
│   │   │   │   ├── layout.tsx         # App shell with sidebar
│   │   │   │   ├── page.tsx           # Chat / search interface
│   │   │   │   ├── trending/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── library/
│   │   │   │       └── page.tsx
│   │   │   ├── meme/
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx       # SEO meme pages
│   │   │   ├── api/
│   │   │   │   └── auth/
│   │   │   │       └── [...nextauth]/
│   │   │   │           └── route.ts
│   │   │   ├── layout.tsx
│   │   │   ├── sitemap.ts
│   │   │   └── robots.ts
│   │   ├── components/
│   │   │   ├── meme/
│   │   │   │   ├── MemeCard.tsx
│   │   │   │   ├── MemeGrid.tsx
│   │   │   │   ├── MemeModal.tsx
│   │   │   │   ├── FormatSelector.tsx
│   │   │   │   ├── DownloadButton.tsx
│   │   │   │   └── ShareButton.tsx
│   │   │   ├── search/
│   │   │   │   ├── SearchInput.tsx
│   │   │   │   ├── SearchResults.tsx
│   │   │   │   └── SuggestionChips.tsx
│   │   │   ├── ui/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Skeleton.tsx
│   │   │   │   └── Toast.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client
│   │   │   ├── utils.ts
│   │   │   └── hooks/
│   │   │       ├── useMemeSearch.ts
│   │   │       └── useDownload.ts
│   │   ├── public/
│   │   │   ├── og-image.jpg
│   │   │   ├── apple-touch-icon.png
│   │   │   └── icons/
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   └── package.json
│   │
│   └── mobile/                        # React Native Expo app
│       ├── app/
│       │   ├── (tabs)/
│       │   │   ├── index.tsx          # Search tab
│       │   │   ├── trending.tsx       # Trending tab
│       │   │   └── library.tsx        # Library tab
│       │   ├── meme/
│       │   │   └── [id].tsx           # Meme detail
│       │   └── _layout.tsx
│       ├── components/
│       │   ├── MemeCard.tsx
│       │   ├── SearchBar.tsx
│       │   ├── FormatPicker.tsx
│       │   └── BottomSheet.tsx
│       ├── hooks/
│       │   ├── useMemeSearch.ts
│       │   └── useShare.ts
│       ├── lib/
│       │   └── api.ts
│       ├── assets/
│       ├── app.json
│       └── package.json
│
├── services/
│   └── api/                           # FastAPI backend
│       ├── app/
│       │   ├── main.py                # App factory + startup
│       │   ├── api/v1/
│       │   │   ├── search.py
│       │   │   ├── memes.py
│       │   │   ├── trending.py
│       │   │   ├── feedback.py
│       │   │   └── health.py
│       │   ├── services/
│       │   │   ├── recommendation.py  # Core engine
│       │   │   ├── embedding.py
│       │   │   ├── llm.py
│       │   │   └── storage.py
│       │   ├── models/
│       │   │   ├── meme.py
│       │   │   ├── search.py
│       │   │   └── feedback.py
│       │   └── core/
│       │       ├── config.py
│       │       ├── cache.py
│       │       └── rate_limit.py
│       ├── scripts/                   # Data pipeline scripts
│       │   ├── download_datasets.py
│       │   ├── preprocess_memes.py
│       │   ├── generate_embeddings.py
│       │   ├── index_qdrant.py
│       │   └── verify_index.py
│       ├── tests/
│       │   ├── test_search.py
│       │   ├── test_recommendations.py
│       │   └── test_api.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── data/                              # Local data (gitignored)
│   ├── raw/
│   ├── processed/
│   └── embeddings/
│
├── docs/                              # These 5 MD files
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── test.yml
├── docker-compose.yml                 # Local development
└── README.md
```

---

## API Specification (Complete)

### POST `/api/v1/search`
The core endpoint — takes user text, returns meme recommendations.

**Request:**
```json
{
  "query": "my boss scheduled a meeting that could have been an email",
  "format_preference": "gif",
  "nsfw": false,
  "limit": 5,
  "session_id": "sess_abc123",
  "filters": {
    "categories": [],
    "exclude_ids": []
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "query_id": "q_xyz789",
  "results": [
    {
      "id": "meme_042",
      "name": "This Is Fine",
      "slug": "this-is-fine",
      "relevance_score": 0.94,
      "emotion_match": ["frustration", "acceptance"],
      "preview_url": "https://cdn.memegpt.com/thumbs/this-is-fine.webp",
      "formats": {
        "gif": "https://cdn.memegpt.com/gifs/this-is-fine.gif",
        "image": "https://cdn.memegpt.com/images/this-is-fine.jpg",
        "video": null,
        "webp": "https://cdn.memegpt.com/webp/this-is-fine.webp"
      },
      "share_url": "https://memegpt.com/meme/this-is-fine?ref=q_xyz789",
      "meme_type": "reaction",
      "categories": ["work", "stress", "relatable"]
    }
  ],
  "intent_parsed": {
    "emotion": "frustration",
    "situation": "unnecessary meeting at work",
    "tone": "sarcastic"
  },
  "response_time_ms": 847,
  "cached": false
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "60 requests per minute allowed. Retry after 23 seconds.",
  "retry_after": 23
}
```

---

### GET `/api/v1/memes/{slug}`
Get full meme details by slug.

```json
{
  "id": "meme_042",
  "name": "This Is Fine",
  "slug": "this-is-fine",
  "description": "A dog sitting in a burning room saying 'this is fine'",
  "origin": "KC Green's Gunshow webcomic (2013)",
  "categories": ["work", "stress", "acceptance", "chaos"],
  "emotions": ["frustration", "denial", "resignation"],
  "formats": { ... },
  "related_memes": ["disaster-girl", "everything-is-fine-dog"],
  "usage_count": 15823,
  "download_count": 4291,
  "created_at": "2024-01-15T00:00:00Z"
}
```

---

### GET `/api/v1/memes/{slug}/download?format=gif`
Streams or redirects to the CDN file.

```
301 Redirect → https://cdn.memegpt.com/gifs/this-is-fine.gif
```

---

### POST `/api/v1/feedback`
Record user interaction for model improvement.

```json
// Request
{
  "query_id": "q_xyz789",
  "meme_id": "meme_042",
  "action": "download",
  "session_id": "sess_abc123"
}

// Response
{ "recorded": true }
```

---

### GET `/api/v1/trending?category=work&limit=20`
Returns trending memes updated hourly.

---

## UI Design Specification

### Design Philosophy
- **Dark-first** — memes live on dark Discord/Reddit backgrounds; match that energy
- **Minimal chrome** — the meme is the hero; UI steps back
- **Instant feedback** — loading skeletons, not spinners; optimistic UI
- **Mobile-native feel** — even on desktop, interactions feel touch-friendly

---

### Color System

```css
:root {
  /* Brand */
  --brand-purple:       #7C3AED;   /* Primary — playful but premium */
  --brand-purple-light: #A78BFA;   /* Hover states */
  --brand-amber:        #F59E0B;   /* Accent — meme energy */
  --brand-amber-light:  #FCD34D;

  /* Backgrounds */
  --bg-base:            #0A0A0A;   /* Page background */
  --bg-surface:         #141414;   /* Card backgrounds */
  --bg-elevated:        #1E1E1E;   /* Modals, dropdowns */
  --bg-hover:           #252525;   /* Hover states */

  /* Text */
  --text-primary:       #F5F5F5;   /* Main text */
  --text-secondary:     #A3A3A3;   /* Subtitles, labels */
  --text-muted:         #525252;   /* Placeholder, disabled */

  /* Borders */
  --border-subtle:      #2A2A2A;   /* Card borders */
  --border-default:     #3F3F3F;   /* Input borders */
  --border-strong:      #525252;   /* Focus rings */

  /* Status */
  --success:            #22C55E;
  --error:              #EF4444;
  --warning:            #F59E0B;
}
```

---

### Typography

```css
/* Fonts — load via next/font (zero CLS) */
--font-sans: 'Inter', system-ui;         /* Body text */
--font-display: 'Space Grotesk', sans;  /* Headings */
--font-mono: 'JetBrains Mono', monospace; /* Code */

/* Scale */
--text-xs:   0.75rem;   /* 12px — badges, captions */
--text-sm:   0.875rem;  /* 14px — secondary text */
--text-base: 1rem;      /* 16px — body text */
--text-lg:   1.125rem;  /* 18px — card titles */
--text-xl:   1.25rem;   /* 20px */
--text-2xl:  1.5rem;    /* 24px — section headers */
--text-4xl:  2.25rem;   /* 36px — hero headline */
--text-6xl:  3.75rem;   /* 60px — mega headline */
```

---

### Component Specifications

#### SearchInput Component
```
┌──────────────────────────────────────────────────┐
│  🤔 What's happening? Type anything...            │
│                                                  │
│  [paste your WhatsApp chat, describe a feeling,  │
│   quote a movie, explain a situation...]         │
│                                                  │
│                          [⌘+Enter to Search →]  │
└──────────────────────────────────────────────────┘

States:
- Empty: Placeholder text with examples
- Typing: Character count (max 2000) in bottom-right
- Loading: Animated gradient border + "Finding your meme..." text
- Error: Red border + error message

Props:
- onSearch(query: string) => void
- loading: boolean
- maxLength: 2000
```

#### MemeCard Component
```
┌──────────────────────────┐
│                          │
│   [MEME IMAGE / GIF]     │  ← lazy-loaded, progressive
│   (aspect-ratio: auto)   │
│                          │
├──────────────────────────┤
│ 🎯 94% match             │
│ "This Is Fine"           │
│ 😤 Frustration · 😮 Denial │
├──────────────────────────┤
│ [GIF] [PNG] [MP4]        │
│ [📋 Copy] [⬇ Download]  │
└──────────────────────────┘

Hover state:
- Card lifts (translateY -4px)
- Shadow deepens
- Download button pulses

Format buttons:
- Active format: filled purple
- Unavailable format: greyed out, tooltip "Not available for this meme"

On download click:
- Button shows spinner + "Downloading..."
- Shows ✓ checkmark for 2 seconds
- Triggers file download
```

#### Format Selector (Global)
```
Prefer:  [GIF ✓] [Image] [Video]

- Sticks to top when scrolling
- Selection persists in localStorage
- GIF selected by default
```

---

### Web App — Chat Interface Layout

```
╔════════════════════════════════════════════════════╗
║ HEADER: MemeGPT logo | Search | Trending | Library ║
╠════════════════╦═══════════════════════════════════╣
║                ║                                   ║
║  SIDEBAR       ║  MAIN AREA                        ║
║  (hidden on    ║                                   ║
║   mobile)      ║  [Search Input — full width]      ║
║                ║                                   ║
║  Recent:       ║  [Format Selector: GIF PNG MP4]  ║
║  • "when bug   ║                                   ║
║    finally..." ║  ─── Results ───                  ║
║  • "monday     ║                                   ║
║    morning"    ║  [MemeCard] [MemeCard] [MemeCard]  ║
║                ║  [MemeCard] [MemeCard]            ║
║  Saved:        ║                                   ║
║  • My Favorites║  [More results ↓]                 ║
║  • Work Memes  ║                                   ║
║                ║                                   ║
╚════════════════╩═══════════════════════════════════╝
```

---

### Mobile App — Screen Specs

**Screen 1: Home / Search (Tab 1)**
```
─────────────────────────
[MemeGPT logo]   [☰ Menu]
─────────────────────────
┌───────────────────────┐
│ What's happening? 🤔  │
│ ____________________  │
│                       │
│             [Search]  │
└───────────────────────┘

[Suggestion chips]
[ 🤦 Monday vibe ] [ 😤 Frustration ] [ 🎉 Win ]

─ Recent Searches ─
• "my code worked first try"
• "boss called at midnight"
```

**Screen 2: Results (after search)**
```
← Back   "my code worked..."   [⚙]

[Format: GIF ✓ | PNG | MP4]

┌───────────────────┐
│                   │
│  [Meme Image/GIF] │
│                   │
│  94% | This Is Fine│
│  😤 😮             │
│  [Copy] [Download] [Share]│
└───────────────────┘

┌───────────────────┐
│  [Meme 2]         │
└───────────────────┘
```

**Screen 3: Trending (Tab 2)**
```
─ Trending Today ─────────
[ All ] [ Work ] [ Gaming ] [ ❤️ ] [ Tech ]

[Meme] [Meme] [Meme]
[Meme] [Meme] [Meme]

─ Trending Keywords ──────
#Monday  #ProgrammerHumor  #Exam
```

---

## Database Schema (Supabase PostgreSQL)

```sql
-- Users table
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT UNIQUE NOT NULL,
  name        TEXT,
  avatar_url  TEXT,
  plan        TEXT DEFAULT 'free',  -- 'free' | 'pro'
  preferences JSONB DEFAULT '{}',   -- {format_pref, nsfw, categories}
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Memes metadata table
CREATE TABLE memes (
  id           TEXT PRIMARY KEY,    -- matches Qdrant payload meme_id
  name         TEXT NOT NULL,
  slug         TEXT UNIQUE NOT NULL,
  categories   TEXT[] DEFAULT '{}',
  emotions     TEXT[] DEFAULT '{}',
  image_url    TEXT,
  gif_url      TEXT,
  mp4_url      TEXT,
  thumb_url    TEXT,
  source       TEXT,
  nsfw         BOOLEAN DEFAULT FALSE,
  view_count   INTEGER DEFAULT 0,
  download_count INTEGER DEFAULT 0,
  popularity_score FLOAT DEFAULT 0.0,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  indexed_at   TIMESTAMPTZ DEFAULT NOW()
);

-- User feedback / interaction signals
CREATE TABLE feedback (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id  TEXT,
  user_id     UUID REFERENCES users(id),
  meme_id     TEXT REFERENCES memes(id),
  query_text  TEXT,
  query_id    TEXT,
  action      TEXT NOT NULL,  -- 'view'|'click'|'copy'|'download'|'share'|'thumbs_up'|'thumbs_down'|'skip'
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- User saved memes
CREATE TABLE saved_memes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) NOT NULL,
  meme_id         TEXT REFERENCES memes(id) NOT NULL,
  collection_name TEXT DEFAULT 'Favorites',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, meme_id)
);

-- Search analytics (aggregated, no PII)
CREATE TABLE search_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_hash      TEXT,          -- MD5 of query (anonymous)
  result_count    INTEGER,
  top_meme_id     TEXT,
  latency_ms      INTEGER,
  cache_hit       BOOLEAN,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_memes_categories ON memes USING GIN(categories);
CREATE INDEX idx_memes_emotions ON memes USING GIN(emotions);
CREATE INDEX idx_feedback_meme_id ON feedback(meme_id);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);
CREATE INDEX idx_saved_memes_user_id ON saved_memes(user_id);
```

---

## Development Phases — Solo Developer Roadmap

### Week 1 — Backend Foundation
**Goal:** Working API with 100 memes and basic search

```bash
# Day 1: Project setup
git init memegpt
cd memegpt
mkdir -p apps/web apps/mobile services/api data docs

# Day 2: FastAPI skeleton
cd services/api
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sentence-transformers qdrant-client groq
# Write main.py, basic routes, health check

# Day 3: Data pipeline
python scripts/download_datasets.py --source imgflip  # 100 memes
python scripts/preprocess_memes.py
python scripts/generate_embeddings.py

# Day 4: Qdrant indexing + search endpoint
python scripts/index_qdrant.py
# Implement /api/v1/search with MiniLM + Qdrant

# Day 5: Test + polish
pytest tests/
# Verify: "Monday morning meme" returns relevant results
```

### Week 2 — Web App
**Goal:** Working UI connected to backend

```bash
# Day 6-7: Next.js setup
cd apps/web
npx create-next-app@latest . --typescript --tailwind --app
npm install framer-motion @tanstack/react-query zustand

# Day 8: SearchInput + API integration
# Day 9: MemeCard + MemeGrid components
# Day 10: Download + Copy functionality
```

### Week 3 — Deploy + Polish
**Goal:** Live on the internet, shareable

```bash
# Day 11: Deploy backend to Railway
railway login
railway init
railway up

# Day 12: Deploy frontend to Vercel
vercel --prod

# Day 13: Landing page (homepage with hero + CTA)
# Day 14: Basic SEO (metadata, OG image, sitemap)
# Day 15: Bug fixes, performance tuning
```

### Week 4 — Mobile App
**Goal:** App store ready

```bash
# Day 16-17: Expo setup + core screens
cd apps/mobile
npx create-expo-app . --template blank-typescript
npm install @react-navigation/native expo-image expo-sharing

# Day 18-19: Search, Results, Library screens
# Day 20: Native share + download to camera roll
# Day 21: TestFlight (iOS) + Play Store Beta (Android)
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_recommendation.py
import pytest
from app.services.recommendation import recommend_memes

# Test cases with expected emotion/situation
TEST_CASES = [
    ("I just got promoted", "joy", ["achievement", "success"]),
    ("My flight got cancelled", "frustration", ["travel", "disappointment"]),
    ("It's finally Friday", "joy", ["weekend", "relief"]),
    ("My code worked on first try", "surprise", ["programming", "success"]),
    ("Mondays be like", "frustration", ["monday", "work"]),
]

@pytest.mark.asyncio
async def test_recommendation_returns_results():
    for query, expected_emotion, expected_tags in TEST_CASES:
        results = await recommend_memes(query, format_pref="any")
        assert len(results) >= 1, f"No results for: {query}"
        top_score = results[0]["score"]
        assert top_score > 0.5, f"Low confidence for: {query} (score: {top_score})"

@pytest.mark.asyncio
async def test_nsfw_filter():
    results = await recommend_memes("anything", nsfw=False)
    for r in results:
        assert r["meme"]["nsfw"] == False

@pytest.mark.asyncio
async def test_gif_format_filter():
    results = await recommend_memes("happy", format_pref="gif")
    for r in results:
        assert r["meme"]["has_gif"] == True
```

### Performance Test
```python
# tests/test_performance.py
import time, asyncio

async def test_latency_under_3_seconds():
    start = time.time()
    await recommend_memes("test query for performance")
    elapsed = time.time() - start
    assert elapsed < 3.0, f"Too slow: {elapsed:.2f}s"

async def test_cache_hit_is_fast():
    query = "cached query test"
    await recommend_memes(query)  # First call (no cache)
    
    start = time.time()
    await recommend_memes(query)  # Second call (cache hit)
    elapsed = time.time() - start
    assert elapsed < 0.2, f"Cache miss: {elapsed:.2f}s"
```

### Load Test (Locust)
```python
# locustfile.py
from locust import HttpUser, task, between

class MemeGPTUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(10)
    def search_meme(self):
        self.client.post("/api/v1/search", json={
            "query": "Monday morning feeling",
            "format_preference": "gif"
        })
    
    @task(3)
    def get_trending(self):
        self.client.get("/api/v1/trending")

# Run: locust -f locustfile.py --host https://api.memegpt.com
# Target: 100 concurrent users, < 3s P95
```
