# MemeGPT — Folder Structure (Complete Repository)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete monorepo directory structure with annotations for every file and directory. This is the definitive map of the MemeGPT codebase.

---

## Full Repository Tree

```
memegpt/
├── apps/
│   ├── web/                           # Next.js 14 web app + landing site
│   │   ├── app/
│   │   │   ├── (marketing)/           # Public landing pages (no auth)
│   │   │   │   ├── layout.tsx         # Marketing layout (header + footer)
│   │   │   │   ├── page.tsx           # Homepage — memegpt.com
│   │   │   │   ├── download/
│   │   │   │   │   └── page.tsx       # /download — App Store links
│   │   │   │   ├── features/
│   │   │   │   │   └── page.tsx       # /features — Feature showcase
│   │   │   │   └── blog/
│   │   │   │       ├── page.tsx       # /blog — Blog index
│   │   │   │       └── [slug]/
│   │   │   │           └── page.tsx   # /blog/monday-memes — Blog post
│   │   │   ├── (app)/                 # Authenticated web app
│   │   │   │   ├── layout.tsx         # App shell with sidebar
│   │   │   │   ├── page.tsx           # /app — Chat / search interface
│   │   │   │   ├── trending/
│   │   │   │   │   └── page.tsx       # /app/trending — Trending page
│   │   │   │   └── library/
│   │   │   │       └── page.tsx       # /app/library — Saved memes
│   │   │   ├── meme/
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx       # /meme/drake-pointing — SEO pages
│   │   │   ├── api/
│   │   │   │   └── auth/
│   │   │   │       └── [...nextauth]/
│   │   │   │           └── route.ts   # NextAuth OAuth routes
│   │   │   ├── layout.tsx             # Root layout (metadata, fonts)
│   │   │   ├── sitemap.ts             # Auto-generated sitemap (10K+ pages)
│   │   │   └── robots.ts             # Robots.txt configuration
│   │   ├── components/
│   │   │   ├── meme/
│   │   │   │   ├── MemeCard.tsx       # Individual meme result card
│   │   │   │   ├── MemeGrid.tsx       # Responsive results grid
│   │   │   │   ├── MemeModal.tsx      # Full-screen meme preview
│   │   │   │   ├── FormatSelector.tsx # GIF / PNG / MP4 toggle
│   │   │   │   ├── DownloadButton.tsx # Download with format selection
│   │   │   │   └── ShareButton.tsx    # Native share + link copy
│   │   │   ├── search/
│   │   │   │   ├── SearchInput.tsx    # Main text input (⌘+Enter)
│   │   │   │   ├── SearchResults.tsx  # Results container + loading
│   │   │   │   └── SuggestionChips.tsx# "Monday vibe", "Frustration" chips
│   │   │   ├── ui/                    # Reusable primitives
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Skeleton.tsx       # Loading shimmer placeholder
│   │   │   │   └── Toast.tsx          # "✓ Copied!" notification
│   │   │   └── layout/
│   │   │       ├── Header.tsx         # Logo + navigation
│   │   │       ├── Sidebar.tsx        # Search history + collections
│   │   │       └── Footer.tsx         # Links, legal, social
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client (fetch + error handling)
│   │   │   ├── utils.ts              # Shared utilities
│   │   │   └── hooks/
│   │   │       ├── useMemeSearch.ts   # Search state + API integration
│   │   │       └── useDownload.ts    # Download + clipboard logic
│   │   ├── public/
│   │   │   ├── og-image.jpg           # OpenGraph social card (1200×630)
│   │   │   ├── apple-touch-icon.png   # iOS home screen icon
│   │   │   └── icons/                # Favicon set
│   │   ├── next.config.ts            # Next.js configuration
│   │   ├── tailwind.config.ts        # Tailwind CSS configuration
│   │   └── package.json
│   │
│   └── mobile/                        # React Native Expo app
│       ├── app/
│       │   ├── (tabs)/
│       │   │   ├── index.tsx          # Home / Search tab
│       │   │   ├── trending.tsx       # Trending tab
│       │   │   └── library.tsx        # Saved memes tab
│       │   ├── meme/
│       │   │   └── [id].tsx           # Meme detail screen
│       │   └── _layout.tsx            # Root layout with tab bar
│       ├── components/
│       │   ├── MemeCard.tsx           # Native meme card
│       │   ├── SearchBar.tsx          # Native search input
│       │   ├── FormatPicker.tsx       # Bottom sheet format picker
│       │   └── BottomSheet.tsx        # Reusable bottom sheet
│       ├── hooks/
│       │   ├── useMemeSearch.ts       # Shared search hook
│       │   └── useShare.ts           # Native share sheet
│       ├── lib/
│       │   └── api.ts                # API client (shared types)
│       ├── assets/                   # App icons, splash screen
│       ├── app.json                  # Expo configuration
│       └── package.json
│
├── services/
│   └── api/                           # FastAPI backend service
│       ├── app/
│       │   ├── main.py                # App factory + lifespan (model loading)
│       │   ├── api/v1/
│       │   │   ├── search.py          # POST /api/v1/search
│       │   │   ├── memes.py           # GET /api/v1/memes/{slug}
│       │   │   ├── trending.py        # GET /api/v1/trending
│       │   │   ├── feedback.py        # POST /api/v1/feedback
│       │   │   └── health.py          # GET /health
│       │   ├── services/
│       │   │   ├── recommendation.py  # Core engine — pipeline orchestrator
│       │   │   ├── embedding.py       # MiniLM text embedding + emotion
│       │   │   ├── llm.py             # Groq API integration
│       │   │   ├── search_service.py  # Qdrant vector search
│       │   │   ├── rerank_service.py  # Business logic re-ranking
│       │   │   └── cdn_service.py     # Cloudflare R2 URL builder
│       │   ├── models/
│       │   │   ├── meme.py            # Meme Pydantic schema
│       │   │   ├── search.py          # SearchRequest / SearchResponse
│       │   │   └── feedback.py        # FeedbackRequest schema
│       │   └── core/
│       │       ├── config.py          # pydantic-settings (.env loading)
│       │       ├── cache.py           # Redis caching layer
│       │       └── rate_limit.py      # Token bucket rate limiter
│       ├── scripts/                    # Offline data pipeline
│       │   ├── download_datasets.py   # Fetch from Imgflip, Reddit, Tenor
│       │   ├── preprocess_memes.py    # OCR + BLIP + LLM tagging
│       │   ├── generate_embeddings.py # MiniLM + CLIP embedding generation
│       │   ├── index_qdrant.py        # Upsert vectors to Qdrant
│       │   └── verify_index.py        # Test search quality
│       ├── tests/
│       │   ├── test_search.py         # Search endpoint integration tests
│       │   ├── test_recommendations.py# Pipeline unit tests
│       │   └── test_api.py            # API contract tests
│       ├── Dockerfile                 # Production Docker image
│       └── requirements.txt           # Python dependencies
│
├── data/                              # Local data directory (gitignored)
│   ├── raw/                           # Downloaded meme images
│   ├── processed/                     # Preprocessed JSON with tags
│   └── embeddings/                    # Generated vectors
│
├── docs/                              # Source markdown documentation
│   ├── 01_FEATURES_AND_PRODUCT.md
│   ├── 02_TECH_STACK_AND_MODELS.md
│   ├── 03_ML_PIPELINE_AND_TRAINING.md
│   ├── 04_DESIGN_AND_DEVELOPMENT.md
│   └── 05_SEO_DEPLOYMENT_AND_LAUNCH.md
│
├── .github/
│   └── workflows/
│       ├── deploy.yml                 # Production deploy (push to main)
│       ├── test.yml                   # PR checks (lint + build + test)
│       └── index.yml                 # Weekly meme re-indexing (cron)
│
├── prisma/
│   ├── schema.prisma                  # Database schema definition
│   └── dev.db                         # SQLite dev database (gitignored)
│
├── docker-compose.yml                 # Local development (API + Redis)
├── .env.example                       # Environment variable template
├── .gitignore
└── README.md                          # Project overview + quick start
```

---

## Key Conventions

| Convention | Pattern | Example |
|---|---|---|
| Route groups | `(name)/` | `(marketing)/`, `(app)/` |
| Dynamic routes | `[param]/` | `[slug]/page.tsx` |
| Catch-all routes | `[...param]/` | `[...nextauth]/route.ts` |
| API routes | `api/v1/` | Versioned REST endpoints |
| Components | PascalCase | `MemeCard.tsx` |
| Hooks | `use` prefix | `useMemeSearch.ts` |
| Config files | lowercase | `tailwind.config.ts` |
| Test files | `test_` prefix | `test_search.py` |

---

## What Goes Where

| Content Type | Location | Gitignored? |
|---|---|---|
| Frontend code | `apps/web/` | No |
| Mobile code | `apps/mobile/` | No |
| Backend code | `services/api/` | No |
| ML scripts | `services/api/scripts/` | No |
| Raw meme data | `data/raw/` | **Yes** |
| Processed data | `data/processed/` | **Yes** |
| Embeddings | `data/embeddings/` | **Yes** |
| SQLite dev DB | `prisma/dev.db` | **Yes** |
| Environment vars | `.env` | **Yes** |
| Documentation | `docs/` | No |
| CI/CD workflows | `.github/workflows/` | No |

---

## App Size Budget (Mobile)

```
React Native runtime (Hermes):   15 MB
JavaScript bundle (minified):     4 MB
Expo modules:                     8 MB
App assets (icons, fonts):        2 MB
────────────────────────────────────
Total APK/IPA:                  ~29 MB   ✅ Under 40 MB goal
```

---

> **Related Documents:**
> - [02_Project_Architecture/High_Level_Architecture.md](../02_Project_Architecture/High_Level_Architecture.md) — System overview
> - [03_Backend/API_Architecture.md](../03_Backend/API_Architecture.md) — Backend structure detail
> - [04_Frontend/Frontend_Overview.md](../04_Frontend/Frontend_Overview.md) — Frontend architecture
