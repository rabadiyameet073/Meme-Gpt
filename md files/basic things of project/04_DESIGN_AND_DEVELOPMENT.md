# MemeGPT — Design & Development Guide
> A solo developer's complete reference for building all three platforms from scratch.

---

## 🏗️ Monorepo Structure

Keep everything in one GitHub repository (monorepo). This makes it easy to share types and utilities across platforms.

```
memegpt/
├── apps/
│   ├── web/                   # Next.js web app (app.memegpt.app)
│   ├── landing/               # Next.js landing site (memegpt.app)
│   └── mobile/                # React Native + Expo app
├── packages/
│   ├── api-client/            # Shared API client (used by web + mobile)
│   ├── types/                 # Shared TypeScript types
│   └── ui/                    # Shared UI components (web only)
├── backend/                   # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entrypoint
│   │   ├── routers/           # API route files
│   │   ├── services/          # Business logic
│   │   ├── models/            # Pydantic models
│   │   └── core/              # Config, DB clients
│   ├── scripts/               # Indexing scripts (offline pipeline)
│   │   ├── collect_reddit.py
│   │   ├── collect_giphy.py
│   │   ├── run_ocr.py
│   │   ├── generate_embeddings.py
│   │   └── index_to_qdrant.py
│   ├── requirements.txt
│   └── Dockerfile
├── .github/
│   └── workflows/             # CI/CD GitHub Actions
├── package.json               # Workspace root (Turborepo or pnpm)
└── README.md
```

---

## 🎨 Design System

### Color Palette
```css
/* Primary */
--color-primary: #6C3CE1;        /* Purple — "meme magic" */
--color-primary-light: #8B5CF6;
--color-primary-dark: #4C1D95;

/* Accent */
--color-accent: #F59E0B;         /* Amber — energy, humor */
--color-accent-light: #FCD34D;

/* Neutral (Dark Mode First) */
--color-bg-dark: #0F0F13;        /* Near-black background */
--color-surface-dark: #1C1C24;   /* Card surface */
--color-border-dark: #2D2D3A;    /* Borders */
--color-text-primary: #F1F1F3;   /* Main text */
--color-text-secondary: #9999AA; /* Muted text */

/* Semantic */
--color-success: #10B981;        /* Green */
--color-error: #EF4444;          /* Red */
--color-warning: #F59E0B;        /* Amber */
```

### Typography
```css
/* Font Stack */
--font-display: 'Geist', 'Inter', sans-serif;  /* Headlines */
--font-body: 'Inter', 'SF Pro', sans-serif;     /* Body text */
--font-mono: 'JetBrains Mono', monospace;       /* Code/API docs */

/* Scale */
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 30px;
--text-4xl: 36px;
```

### Spacing & Radius
```css
--spacing-unit: 8px;    /* Base unit — all spacing is multiples of 8 */
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;
--radius-full: 9999px;  /* Pills, avatars */
```

---

## 🌐 Web App — Screen-by-Screen Design

### Screen 1: Search Home (Main Screen)
```
┌──────────────────────────────────────────────┐
│  🎭 MemeGPT                        ⚙️  🌙    │
├──────────────────────────────────────────────┤
│                                              │
│   ┌────────────────────────────────────┐     │
│   │  💬 Say anything. Get the meme.   │     │
│   │                                    │     │
│   │  Type a sentence, paste a chat,   │     │
│   │  or describe your mood...          │     │
│   │                                    │     │
│   │  [___________________________________]   │
│   │  Large text area (3-4 rows tall)        │
│   │                                    │     │
│   │  [Single line] [Conversation] [Script]  │
│   └────────────────────────────────────┘     │
│                                              │
│       [ 🔍 Find My Meme ]  ← Primary CTA    │
│                                              │
│  Filters: [All] [GIF] [Image] [Video]       │
│  Mood: [😂 Funny] [😤 Angry] [🥺 Sad]       │
│                                              │
│  ── Trending Searches ──                    │
│  · Monday morning · Code review · FOMO      │
└──────────────────────────────────────────────┘
```

### Screen 2: Search Results
```
┌──────────────────────────────────────────────┐
│  ← "when your code works first try"    🔄   │
├──────────────────────────────────────────────┤
│  10 memes found  •  Sorted by relevance      │
│                                              │
│  ┌───────────┐  ┌───────────┐               │
│  │  [GIF]    │  │  [GIF]    │               │
│  │  ★ 98%    │  │  ★ 94%    │               │
│  │  📋  ⬇️  🔗│  │  📋  ⬇️  🔗│               │
│  └───────────┘  └───────────┘               │
│                                              │
│  ┌───────────┐  ┌───────────┐               │
│  │  [Image]  │  │  [GIF]    │               │
│  │  ★ 91%    │  │  ★ 89%    │               │
│  │  📋  ⬇️  🔗│  │  📋  ⬇️  🔗│               │
│  └───────────┘  └───────────┘               │
│                                              │
│  [Load 10 more]                             │
└──────────────────────────────────────────────┘
```

### Screen 3: Meme Preview (Lightbox)
```
┌──────────────────────────────────────────────┐
│  ✕                              ← → (nav)   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │                                      │   │
│  │           [MEME IMAGE/GIF]           │   │
│  │            Full screen               │   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  "When your code works on first try"        │
│  📍 r/ProgrammerHumor  •  45K upvotes       │
│                                              │
│  ┌────────┐  ┌────────┐  ┌────────────┐    │
│  │📋 Copy │  │⬇️ Save  │  │🔗 Share    │    │
│  └────────┘  └────────┘  └────────────┘    │
│                                              │
│  Format:  [GIF ✓]  [MP4]  [PNG]           │
│                                             │
│  Tags: #programming #coding #surprised      │
└──────────────────────────────────────────────┘
```

---

## 📱 Mobile App — Screen Breakdown

### Navigation Structure (Expo Router)
```
app/
├── (tabs)/
│   ├── index.tsx          # Search tab (home)
│   ├── favorites.tsx      # Saved memes
│   ├── history.tsx        # Recent searches
│   └── settings.tsx       # App settings
├── meme/[id].tsx          # Meme detail/preview screen
├── results.tsx            # Search results screen
└── _layout.tsx            # Root layout + bottom tab bar
```

### Mobile-Specific UX Patterns
- **Pull to refresh** on results page
- **Haptic feedback** on copy/download
- **Swipe gestures** on meme preview (left/right to navigate results)
- **Bottom sheet** for format picker (instead of modal)
- **Skeleton loading** placeholders while memes load
- **Toast notifications** for copy/download success (auto-dismiss 2s)
- **Offline indicator** when no internet

---

## 🔌 Complete REST API Design

### Base URL: `https://api.memegpt.app`

### Endpoints

#### `POST /api/v1/search`
**Purpose:** Main meme search  
**Request:**
```json
{
  "query": "when your code works on first try",
  "format": "gif",          // optional: "gif" | "image" | "video" | null
  "emotion": "surprised",   // optional
  "limit": 10,              // 1-50, default 10
  "safe_mode": true,        // default true
  "offset": 0               // for pagination
}
```
**Response:**
```json
{
  "results": [
    {
      "id": "meme_abc123",
      "title": "When your code works on first try",
      "media_url": "https://cdn.memegpt.app/memes/abc123.gif",
      "thumb_url": "https://cdn.memegpt.app/thumbs/abc123.jpg",
      "format": "gif",
      "width": 480,
      "height": 270,
      "source": "reddit",
      "subreddit": "ProgrammerHumor",
      "upvotes": 45234,
      "tags": ["programming", "coding"],
      "emotion": "surprised",
      "relevance_score": 0.94,
      "share_url": "https://mgpt.link/abc123",
      "download_formats": {
        "gif": "https://cdn.memegpt.app/memes/abc123.gif",
        "mp4": "https://cdn.memegpt.app/memes/abc123.mp4",
        "jpg": "https://cdn.memegpt.app/memes/abc123.jpg"
      }
    }
  ],
  "total": 10,
  "query_understood_as": "surprised reaction, programming context",
  "search_time_ms": 340,
  "from_cache": false
}
```

#### `GET /api/v1/meme/{id}`
**Purpose:** Get a single meme by ID  
**Response:** Same as single item in search results array

#### `GET /api/v1/trending`
**Purpose:** Get currently trending memes  
**Query Params:** `?limit=20&format=gif`

#### `GET /api/v1/categories`
**Purpose:** List all meme categories  

#### `POST /api/v1/feedback`
**Purpose:** Record user interaction (for quality improvement)  
```json
{
  "query_hash": "md5_of_query",
  "meme_id": "meme_abc123",
  "action": "copy",          // "copy" | "download" | "share" | "skip"
  "result_position": 1
}
```

#### `GET /api/v1/health`
**Purpose:** Health check (for monitoring + keeping Render warm)  
**Response:** `{"status": "ok", "version": "1.0.0"}`

---

## 🗄️ Supabase Database Schema

```sql
-- Meme metadata (supplements Qdrant)
CREATE TABLE memes (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  media_url TEXT NOT NULL,
  thumb_url TEXT,
  format TEXT NOT NULL,  -- 'gif', 'image', 'video'
  width INTEGER,
  height INTEGER,
  file_size_kb INTEGER,
  source TEXT,           -- 'reddit', 'giphy', 'tenor', 'imgflip'
  source_url TEXT,
  subreddit TEXT,
  upvotes INTEGER DEFAULT 0,
  tags TEXT[],
  emotion TEXT,
  humor_type TEXT,
  is_nsfw BOOLEAN DEFAULT FALSE,
  ocr_text TEXT,
  created_at TIMESTAMPTZ,
  indexed_at TIMESTAMPTZ DEFAULT NOW()
);

-- User collections (local-first, synced if logged in)
CREATE TABLE collections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,           -- anonymous device ID
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE collection_memes (
  collection_id UUID REFERENCES collections(id),
  meme_id TEXT NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (collection_id, meme_id)
);

-- Search analytics (aggregated, not per-user)
CREATE TABLE search_analytics (
  id BIGSERIAL PRIMARY KEY,
  query_hash TEXT NOT NULL,    -- MD5 of query (privacy-safe)
  result_count INTEGER,
  avg_relevance_score FLOAT,
  cache_hit BOOLEAN,
  response_time_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Meme performance tracking
CREATE TABLE meme_events (
  id BIGSERIAL PRIMARY KEY,
  meme_id TEXT NOT NULL,
  action TEXT NOT NULL,        -- 'view', 'copy', 'download', 'share'
  result_position INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_memes_format ON memes(format);
CREATE INDEX idx_memes_emotion ON memes(emotion);
CREATE INDEX idx_meme_events_meme_id ON meme_events(meme_id);
CREATE INDEX idx_search_analytics_hash ON search_analytics(query_hash);
```

---

## 🧱 Backend Code Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app + startup
│   ├── routers/
│   │   ├── search.py            # POST /api/v1/search
│   │   ├── memes.py             # GET /api/v1/meme/{id}
│   │   ├── trending.py          # GET /api/v1/trending
│   │   ├── feedback.py          # POST /api/v1/feedback
│   │   └── health.py            # GET /api/v1/health
│   ├── services/
│   │   ├── embedding_service.py # Wraps MiniLM model
│   │   ├── search_service.py    # Qdrant search logic
│   │   ├── rerank_service.py    # CLIP re-ranking logic
│   │   ├── context_service.py   # Groq context extraction
│   │   └── cache_service.py     # Redis operations
│   ├── models/
│   │   ├── search.py            # SearchRequest, SearchResult Pydantic models
│   │   └── meme.py              # Meme Pydantic model
│   └── core/
│       ├── config.py            # Environment variables (Pydantic Settings)
│       ├── qdrant.py            # Qdrant client singleton
│       ├── supabase.py          # Supabase client singleton
│       └── redis.py             # Redis client singleton
└── scripts/
    ├── 01_collect_reddit.py
    ├── 02_collect_giphy.py
    ├── 03_clean_and_deduplicate.py
    ├── 04_run_ocr.py
    ├── 05_generate_embeddings.py
    └── 06_index_to_qdrant.py
```

### `main.py` — FastAPI App Entry
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search, memes, trending, feedback, health
from app.services.embedding_service import EmbeddingService
from app.services.rerank_service import RerankService

app = FastAPI(title="MemeGPT API", version="1.0.0")

# CORS — allow web app + mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.memegpt.app", "https://memegpt.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models at startup (once, stays in memory)
@app.on_event("startup")
async def startup():
    app.state.embedding_service = EmbeddingService()  # Loads MiniLM
    app.state.rerank_service = RerankService()         # Loads CLIP
    print("✅ Models loaded successfully")

# Include routers
app.include_router(search.router, prefix="/api/v1")
app.include_router(memes.router, prefix="/api/v1")
app.include_router(trending.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
```

---

## 🌐 Web App Code Structure

```
apps/web/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout (fonts, metadata, providers)
│   ├── page.tsx                  # Home / Search page
│   ├── results/
│   │   └── page.tsx              # Results page
│   ├── meme/
│   │   └── [id]/
│   │       └── page.tsx          # Single meme page (for sharing links)
│   ├── favorites/
│   │   └── page.tsx              # Saved memes
│   └── api/                      # Next.js API routes (proxy to backend)
│       └── search/
│           └── route.ts
├── components/
│   ├── SearchBar.tsx             # Main search input component
│   ├── MemeGrid.tsx              # Responsive meme grid
│   ├── MemeCard.tsx              # Individual meme card (thumbnail + actions)
│   ├── MemeLightbox.tsx          # Full-screen meme preview
│   ├── FormatBadge.tsx           # GIF / Image / Video badge
│   ├── FilterBar.tsx             # Format + mood filters
│   ├── DownloadModal.tsx         # Format picker for download
│   ├── CopyButton.tsx            # Copy to clipboard button
│   └── ShareButton.tsx           # Native share / copy URL
├── hooks/
│   ├── useMemeSearch.ts          # Search state + API calls
│   ├── useClipboard.ts           # Copy to clipboard logic
│   ├── useDownload.ts            # Download file logic
│   └── useFavorites.ts           # Local favorites (localStorage)
├── lib/
│   ├── api.ts                    # API client
│   └── utils.ts                  # Utility functions
├── public/
│   ├── icons/                    # App icons
│   └── og-image.png              # Default OG image for SEO
└── next.config.js
```

### Key Component: `MemeCard.tsx`
```tsx
interface MemeCardProps {
  meme: MemeResult;
  onSelect: (meme: MemeResult) => void;
}

export function MemeCard({ meme, onSelect }: MemeCardProps) {
  const { copy, isCopied } = useClipboard();
  const { download } = useDownload();
  
  return (
    <div className="group relative rounded-xl overflow-hidden bg-surface 
                    cursor-pointer hover:ring-2 hover:ring-primary transition-all">
      
      {/* Meme Media */}
      <div onClick={() => onSelect(meme)} className="relative aspect-video">
        <img
          src={meme.thumb_url}
          alt={meme.title}
          loading="lazy"
          className="w-full h-full object-cover"
        />
        {/* GIF badge */}
        {meme.format === 'gif' && (
          <span className="absolute top-2 left-2 bg-black/70 text-white 
                           text-xs px-2 py-0.5 rounded-md font-mono">
            GIF
          </span>
        )}
        {/* Relevance score */}
        <span className="absolute top-2 right-2 bg-primary/80 text-white 
                         text-xs px-2 py-0.5 rounded-md">
          ★ {Math.round(meme.relevance_score * 100)}%
        </span>
      </div>
      
      {/* Action buttons — visible on hover */}
      <div className="absolute bottom-0 left-0 right-0 
                      bg-gradient-to-t from-black/80 to-transparent
                      opacity-0 group-hover:opacity-100 transition-opacity
                      flex gap-2 p-3">
        <button
          onClick={(e) => { e.stopPropagation(); copy(meme.media_url); }}
          className="flex-1 bg-white/20 hover:bg-white/30 text-white 
                     text-sm rounded-lg py-1.5 backdrop-blur-sm"
        >
          {isCopied ? '✓ Copied' : '📋 Copy'}
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); download(meme); }}
          className="flex-1 bg-white/20 hover:bg-white/30 text-white 
                     text-sm rounded-lg py-1.5 backdrop-blur-sm"
        >
          ⬇️ Save
        </button>
      </div>
    </div>
  );
}
```

---

## 🛠️ Development Environment Setup

### Prerequisites
```bash
# Required installations
node --version     # 20.x or higher
python --version   # 3.11 or higher
git --version

# Install pnpm (faster than npm)
npm install -g pnpm

# Install Expo CLI
npm install -g @expo/cli

# Install Tesseract (for OCR scripts)
# macOS:
brew install tesseract
# Ubuntu:
sudo apt install tesseract-ocr
```

### Setup Steps
```bash
# 1. Clone repo
git clone https://github.com/yourname/memegpt
cd memegpt

# 2. Install JS dependencies (all packages)
pnpm install

# 3. Set up Python backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Copy environment files
cp .env.example .env
# Fill in your API keys in .env

# 5. Start everything in dev mode
# Terminal 1 — Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — Web App
cd apps/web && pnpm dev

# Terminal 3 — Landing Site
cd apps/landing && pnpm dev

# Terminal 4 — Mobile App
cd apps/mobile && npx expo start
```

### `requirements.txt` (Backend)
```txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.0
pydantic-settings==2.2.1
sentence-transformers==3.0.0
transformers==4.40.0
torch==2.3.0
Pillow==10.3.0
pytesseract==0.3.10
qdrant-client==1.9.0
supabase==2.4.0
redis==5.0.4
httpx==0.27.0
praw==7.7.1
groq==0.9.0
python-multipart==0.0.9
```

---

## 🧪 Testing Strategy

### Backend Tests (pytest)
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

Key test files:
- `tests/test_search.py` — Test search endpoint with known queries
- `tests/test_embedding.py` — Test embedding consistency
- `tests/test_reranking.py` — Test CLIP reranking logic

### Frontend Tests (Vitest + Playwright)
```bash
# Unit tests
pnpm test

# E2E tests (Playwright)
pnpm e2e
```

Key E2E tests:
- User can type query and see results
- User can copy a meme
- User can download a meme in different formats
- Search results update when filters change

---

*Document Version: 1.0 | Last Updated: 2026 | Owner: Founder*
