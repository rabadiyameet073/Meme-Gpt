"""Comprehensive Technology Stack Reference and Evaluation Service for MemeGPT.
Specification: 16_References/Technology_Stack.md

Covers:
- 20+ Technology Catalog entries across 5 Tiers:
  1. Backend (Python 3.11, FastAPI, Uvicorn)
  2. Frontend (React 18, Vite 5, Next.js 14, TailwindCSS 3)
  3. AI/ML (MiniLM-L6-v2, Groq Llama 3.1 8B, Qdrant, HuggingFace Transformers)
  4. Infrastructure (Vercel, Render/Railway, Supabase, Cloudflare R2, Upstash Redis)
  5. Development Tools (Prisma, Ruff, ESLint, Prettier, GitHub Actions, Docker, UptimeRobot, Sentry)
- Full 8-attribute specification per component
- Tier filtering, search, and architecture compliance evaluator
"""

from typing import Any, Dict, List, Optional


# ── Technology Catalog Database ────────────────────────────────────────────────

TECH_STACK_CATALOG: List[Dict[str, Any]] = [
    # ── Backend Technologies ───────────────────────────────────────────────────
    {
        "id": "TECH_BACKEND_PYTHON",
        "name": "Python 3.11",
        "tier": "backend",
        "what_it_is": "General-purpose high-level programming language.",
        "why_used": "Backend API development, business logic, and ML model inference runtime.",
        "why_selected": "Dominant ecosystem for AI/ML libraries (PyTorch, HuggingFace, sentence-transformers).",
        "benefits": ["Massive ML library ecosystem", "Async/await I/O support", "Strong static type hints with mypy/Pydantic"],
        "limitations": ["GIL limits multi-threaded CPU concurrency", "Higher execution latency compared to Go/Rust"],
        "alternatives_considered": ["Node.js (immature ML ecosystem)", "Go (lack of native HuggingFace libraries)", "Rust (steep learning curve)"],
        "configuration": "Python 3.11+, isolated virtual environment via venv/uv.",
        "best_practices": ["Use strict type hints", "Use async def for I/O", "Offload heavy CPU tasks to worker pools"],
    },
    {
        "id": "TECH_BACKEND_FASTAPI",
        "name": "FastAPI",
        "tier": "backend",
        "what_it_is": "Modern, high-performance web framework for building APIs with Python 3.8+.",
        "why_used": "Main HTTP and WebSocket REST API layer for MemeGPT.",
        "why_selected": "Automatic Swagger/OpenAPI documentation, Pydantic type validation, and native async support.",
        "benefits": ["Type-safe request validation", "Auto-generated Swagger UI & ReDoc", "Dependency injection system", "High async throughput"],
        "limitations": ["Smaller plugin ecosystem than legacy Django/Flask", "Requires ASGI runner"],
        "alternatives_considered": ["Flask (synchronous by default, manual validation)", "Django (monolithic overhead)", "Express.js (wrong language for Python ML)"],
        "configuration": "pip install fastapi uvicorn; ASGI router mount in app/main.py",
        "best_practices": ["Thin route controllers", "Service layer architecture pattern", "Pydantic DTO schemas for I/O"],
    },
    {
        "id": "TECH_BACKEND_UVICORN",
        "name": "Uvicorn",
        "tier": "backend",
        "what_it_is": "Lightning-fast ASGI web server implementation for Python.",
        "why_used": "Serves and powers the FastAPI ASGI application.",
        "why_selected": "Fastest Python ASGI server with uvloop and httptools backing.",
        "benefits": ["Asynchronous event loop", "Hot-reload support for dev", "Gunicorn worker compatibility"],
        "limitations": ["Single-threaded per worker without process manager"],
        "alternatives_considered": ["Hypercorn (slower)", "Daphne (Twisted-based, heavier)"],
        "configuration": "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1",
        "best_practices": ["Run behind Gunicorn or reverse proxy in production", "Tune worker count to CPU cores"],
    },

    # ── Frontend Technologies ──────────────────────────────────────────────────
    {
        "id": "TECH_FRONTEND_REACT",
        "name": "React 18",
        "tier": "frontend",
        "what_it_is": "JavaScript library for building modular, declarative user interfaces.",
        "why_used": "Web application client and UI component system.",
        "why_selected": "Massive global ecosystem, seamless component reuse with React Native, and hooks-based state.",
        "benefits": ["Component-driven architecture", "Virtual DOM performance", "Huge NPM component ecosystem", "Shared logic with React Native"],
        "limitations": ["Requires external state management and routing libraries", "JSX build tooling step"],
        "alternatives_considered": ["Vue.js (smaller ecosystem)", "Svelte (less mature for cross-platform)", "Angular (overly complex)"],
        "configuration": "React 18 with TypeScript and Vite bundler.",
        "best_practices": ["Functional components with hooks", "Memoize expensive calculations", "Clean component separation"],
    },
    {
        "id": "TECH_FRONTEND_VITE",
        "name": "Vite 5",
        "tier": "frontend",
        "what_it_is": "Next-generation frontend dev server and production bundler.",
        "why_used": "Local development environment and optimized production SPA builder.",
        "why_selected": "Sub-second Hot Module Replacement (HMR) powered by ESBuild and Rollup.",
        "benefits": ["10-100x faster startup than Webpack", "Native ESM dev server", "Minimal configuration overhead"],
        "limitations": ["Differs slightly between dev (ESBuild) and prod (Rollup)"],
        "alternatives_considered": ["Webpack (slow builds)", "Parcel (less granular control)", "Turbopack (early stage)"],
        "configuration": "vite.config.ts with @vitejs/plugin-react",
        "best_practices": ["Keep plugins minimal", "Use dynamic imports for route splitting"],
    },
    {
        "id": "TECH_FRONTEND_NEXTJS",
        "name": "Next.js 14",
        "tier": "frontend",
        "what_it_is": "Full-stack React framework with SSR, SSG, ISR, and API routes.",
        "why_used": "Server-side rendering and static SEO pages for individual memes.",
        "why_selected": "Best-in-class React SEO framework, App Router architecture, and seamless Vercel deployment.",
        "benefits": ["Static Site Generation (SSG)", "Incremental Static Regeneration (ISR)", "Built-in Image optimization", "OpenGraph dynamic tags"],
        "limitations": ["Heavier than pure Vite SPA", "Vercel-centric defaults"],
        "alternatives_considered": ["Remix (smaller community)", "Gatsby (legacy static builder)"],
        "configuration": "Next.js 14 App Router in frontend/src/app",
        "best_practices": ["Use Server Components by default", "Opt-in to Client Components only for interactivity"],
    },
    {
        "id": "TECH_FRONTEND_TAILWIND",
        "name": "TailwindCSS 3",
        "tier": "frontend",
        "what_it_is": "Utility-first CSS framework packed with atomic design classes.",
        "why_used": "Rapid, consistent styling across all UI components and responsive layouts.",
        "why_selected": "Fast prototyping speed, small purged CSS output, and standardized design tokens.",
        "benefits": ["Zero runtime CSS overhead", "Dead code elimination via PurgeCSS", "Consistent spacing and color scale"],
        "limitations": ["Cluttered HTML class strings", "Steep initial utility class learning curve"],
        "alternatives_considered": ["Vanilla CSS (slower maintenance)", "CSS Modules (verbose)", "Styled Components (runtime performance penalty)"],
        "configuration": "tailwind.config.js with custom color tokens and typography plugins",
        "best_practices": ["Use clsx/tailwind-merge for conditional classes", "Extract repetitive utility clusters into components"],
    },

    # ── AI/ML Technologies ─────────────────────────────────────────────────────
    {
        "id": "TECH_AIML_MINILM",
        "name": "sentence-transformers (all-MiniLM-L6-v2)",
        "tier": "ai_ml",
        "what_it_is": "Dense text embedding transformer model generating 384-dimensional vectors.",
        "why_used": "Converts search queries and meme captions into vector embeddings for cosine similarity.",
        "why_selected": "Top-tier MTEB score-to-size efficiency, ultra-lightweight (22MB), CPU runnable, ~50ms inference.",
        "benefits": ["22MB model footprint", "Pre-normalized L2 vectors", "Runs locally with zero external API fees"],
        "limitations": ["256-token maximum context window", "English-optimized"],
        "alternatives_considered": ["OpenAI text-embedding-ada-002 (costly API, network dependency)", "BGE-large (1.3GB RAM)", "E5-large (high latency on CPU)"],
        "configuration": "SentenceTransformer('all-MiniLM-L6-v2') cached on application startup",
        "best_practices": ["Pre-warm model during lifespan startup", "Batch embed indexing operations"],
    },
    {
        "id": "TECH_AIML_GROQ",
        "name": "Groq Cloud (Llama 3.1 8B)",
        "tier": "ai_ml",
        "what_it_is": "AI inference engine powered by custom Language Processing Units (LPUs).",
        "why_used": "Natural language intent parsing, keyword extraction, and emotion classification.",
        "why_selected": "6,000 free requests/day, ~200ms inference latency, structured JSON response mode.",
        "benefits": ["Sub-200ms latency", "Free tier capacity", "Llama 3.1 8B reasoning power", "Zero GPU server maintenance"],
        "limitations": ["30 requests/minute rate limit on free tier", "External cloud dependency"],
        "alternatives_considered": ["OpenAI GPT-3.5/4o (expensive)", "Local Ollama (requires dedicated GPU server)", "Together.ai (higher latency)"],
        "configuration": "Groq SDK client with GROQ_API_KEY environment variable",
        "best_practices": ["Temperature 0.1 for deterministic JSON", "Graceful fallback if API fails"],
    },
    {
        "id": "TECH_AIML_QDRANT",
        "name": "Qdrant",
        "tier": "ai_ml",
        "what_it_is": "High-performance open-source vector similarity search engine and database.",
        "why_used": "Stores and searches meme text and image embeddings using HNSW indexing.",
        "why_selected": "1GB free managed cloud tier, named vector support, and rich payload metadata filtering.",
        "benefits": ["Named vectors for multi-modal embeddings", "Fast HNSW cosine similarity", "Metadata payload filtering (NSFW, format)", "gRPC & REST APIs"],
        "limitations": ["Smaller ecosystem compared to Pinecone"],
        "alternatives_considered": ["Pinecone (restrictive free tier)", "Weaviate (heavier resource footprint)", "ChromaDB (no managed cloud tier)"],
        "configuration": "QdrantClient with QDRANT_URL and QDRANT_API_KEY",
        "best_practices": ["Use payload indexes on filtered fields", "Batch upsert operations in chunks of 100"],
    },
    {
        "id": "TECH_AIML_TRANSFORMERS",
        "name": "HuggingFace Transformers",
        "tier": "ai_ml",
        "what_it_is": "Comprehensive Python library for state-of-the-art transformer models.",
        "why_used": "Emotion detection (DistilRoBERTa), image captioning (BLIP), and image embeddings (CLIP).",
        "why_selected": "Global industry standard for deep learning model pipelines.",
        "benefits": ["Standardized pipeline API", "Thousands of pre-trained open models", "PyTorch/ONNX interop"],
        "limitations": ["Heavy PyTorch dependencies in Docker images"],
        "alternatives_considered": ["Direct ONNX runtime (more complex setup)", "TensorRT (NVIDIA GPU required)"],
        "configuration": "transformers pipeline('text-classification') with CPU thread limits",
        "best_practices": ["Lock model versions to specific commit SHAs", "Disable gradient calculation in inference"],
    },

    # ── Infrastructure Technologies ────────────────────────────────────────────
    {
        "id": "TECH_INFRA_VERCEL",
        "name": "Vercel",
        "tier": "infrastructure",
        "what_it_is": "Global frontend cloud hosting platform and Edge Network.",
        "why_used": "Hosts the Next.js web frontend at memegpt.com.",
        "why_selected": "Generous 100GB/month free tier, zero-config Next.js optimizations, automatic Git deployments.",
        "benefits": ["Global Edge CDN", "Automatic SSL certificates", "Instant preview deployments per PR"],
        "limitations": ["10s execution timeout on serverless functions", "100GB monthly bandwidth limit"],
        "alternatives_considered": ["Netlify (less optimized for Next.js)", "AWS CloudFront + S3 (complex DevOps)"],
        "configuration": "vercel.json routing and environment variable injection",
        "best_practices": ["Cache static assets at the edge", "Optimize images via next/image"],
    },
    {
        "id": "TECH_INFRA_RAILWAY_RENDER",
        "name": "Railway / Render",
        "tier": "infrastructure",
        "what_it_is": "PaaS cloud infrastructure platforms for backend container hosting.",
        "why_used": "Hosts the FastAPI backend API at api.memegpt.com.",
        "why_selected": "Docker container support, automated GitHub continuous deployment, straightforward logging.",
        "benefits": ["Zero DevOps server configuration", "Automatic HTTPS termination", "Built-in health monitoring"],
        "limitations": ["Render free tier sleeps after 15 minutes of inactivity"],
        "alternatives_considered": ["AWS ECS / Fargate (complex setup)", "DigitalOcean App Platform (costly starter tier)"],
        "configuration": "Dockerfile with Gunicorn + Uvicorn workers and PORT env binding",
        "best_practices": ["Use UptimeRobot 5-minute health check to prevent cold starts", "Monitor memory consumption"],
    },
    {
        "id": "TECH_INFRA_SUPABASE",
        "name": "Supabase",
        "tier": "infrastructure",
        "what_it_is": "Open-source Firebase alternative providing managed PostgreSQL, Auth, and Storage.",
        "why_used": "Primary relational database for meme metadata, user accounts, and analytics.",
        "why_selected": "500MB free PostgreSQL tier, built-in connection pooling with PgBouncer, and real-time support.",
        "benefits": ["Standard PostgreSQL capabilities", "PgBouncer connection pooling", "Built-in Row Level Security (RLS)"],
        "limitations": ["500MB storage ceiling on free tier", "Connection limits without PgBouncer"],
        "alternatives_considered": ["PlanetScale (removed free tier)", "Neon (serverless cold starts)"],
        "configuration": "DATABASE_URL connection string with pooled port 6543",
        "best_practices": ["Always use PgBouncer in serverless backends", "Enforce RLS security policies"],
    },
    {
        "id": "TECH_INFRA_CLOUDFLARE_R2",
        "name": "Cloudflare R2",
        "tier": "infrastructure",
        "what_it_is": "S3-compatible distributed object storage with zero egress fees.",
        "why_used": "Stores meme media files (GIF, PNG, JPG, MP4, WebP).",
        "why_selected": "10GB free storage and $0 egress bandwidth costs (ideal for media-heavy meme delivery).",
        "benefits": ["Zero egress charges", "Global Cloudflare CDN caching", "Standard AWS S3 SDK compatibility"],
        "limitations": ["Requires separate custom domain configuration for public CDN URLs"],
        "alternatives_considered": ["AWS S3 (steep egress bandwidth costs)", "Google Cloud Storage (egress bandwidth fees)"],
        "configuration": "boto3 S3 client configured with Cloudflare R2 endpoint URL",
        "best_practices": ["Set Cache-Control: public, max-age=31536000 on static meme files"],
    },
    {
        "id": "TECH_INFRA_UPSTASH_REDIS",
        "name": "Upstash Redis",
        "tier": "infrastructure",
        "what_it_is": "Serverless Redis database designed for edge and serverless architectures.",
        "why_used": "Caches search responses, intent parses, and enforces API rate limits.",
        "why_selected": "10,000 commands/day free tier, HTTP REST API support, and zero idle cost.",
        "benefits": ["Per-request pricing with no idle costs", "Sub-15ms cached response times", "Built-in TTL eviction"],
        "limitations": ["Network latency slightly higher than co-located Redis daemon"],
        "alternatives_considered": ["Redis Cloud (limited 30MB free tier)", "Self-hosted Redis (server management overhead)"],
        "configuration": "UPSTASH_REDIS_URL with upstash-redis client",
        "best_practices": ["Set 24h TTL on query cache keys", "Use Sliding Window for rate limiting"],
    },

    # ── Development Tools ──────────────────────────────────────────────────────
    {
        "id": "TECH_DEV_PRISMA",
        "name": "Prisma",
        "tier": "dev_tools",
        "what_it_is": "Next-generation TypeScript and Node.js ORM with declarative schema.",
        "why_used": "Database schema modeling, migrations, and visual Prisma Studio browsing.",
        "why_selected": "Type-safe client generation, unified schema for SQLite and PostgreSQL.",
        "benefits": ["Prisma Studio visual GUI", "Declarative schema migrations", "Strict type safety"],
        "limitations": ["Rust query engine binary footprint"],
        "alternatives_considered": ["TypeORM (verbose)", "Drizzle (newer, less tooling)"],
        "configuration": "prisma/schema.prisma with datasource db",
        "best_practices": ["Run prisma generate in CI", "Use prisma migrate deploy in production"],
    },
    {
        "id": "TECH_DEV_RUFF",
        "name": "Ruff",
        "tier": "dev_tools",
        "what_it_is": "Extremely fast Python linter and code formatter written in Rust.",
        "why_used": "Enforces Python code quality, linting, import sorting, and formatting.",
        "why_selected": "10-100x faster than Flake8/Black, consolidates multiple tools into one.",
        "benefits": ["Near-instant execution (<50ms)", "Drop-in Black & Flake8 compatibility", "Auto-fix capabilities"],
        "limitations": ["Rapidly evolving rule set"],
        "alternatives_considered": ["Flake8 + Black + isort (3 separate slow tools)", "Pylint (slow)"],
        "configuration": "pyproject.toml with line-length = 100",
        "best_practices": ["Run ruff check --fix and ruff format in pre-commit hooks"],
    },
    {
        "id": "TECH_DEV_ESLINT_PRETTIER",
        "name": "ESLint & Prettier",
        "tier": "dev_tools",
        "what_it_is": "Industry standard TypeScript/JavaScript linter and opinionated code formatter.",
        "why_used": "Maintains frontend and mobile code quality and consistent formatting.",
        "why_selected": "Universal standard in modern web and React Native development.",
        "benefits": ["Catch runtime syntax bugs early", "Automated code formatting on save"],
        "limitations": ["Occasional rule conflicts (resolved via eslint-config-prettier)"],
        "alternatives_considered": ["Biome (early stage for React Native)"],
        "configuration": ".eslintrc.json and .prettierrc",
        "best_practices": ["Run npm run lint in GitHub Actions CI"],
    },
    {
        "id": "TECH_DEV_GITHUB_ACTIONS",
        "name": "GitHub Actions",
        "tier": "dev_tools",
        "what_it_is": "Continuous Integration and Continuous Delivery (CI/CD) automation platform.",
        "why_used": "Automates linting, test suite execution, Docker builds, and deployment triggers.",
        "why_selected": "2,000 free runner minutes/month, seamless integration with GitHub repositories.",
        "benefits": ["Native GitHub workflow triggers", "Parallel job execution", "Secret management"],
        "limitations": ["Runner concurrency limits on free tier"],
        "alternatives_considered": ["GitLab CI", "CircleCI", "Travis CI"],
        "configuration": ".github/workflows/ci.yml and deploy.yml",
        "best_practices": ["Fail fast on linting errors", "Cache Python/Node dependencies"],
    },
    {
        "id": "TECH_DEV_DOCKER",
        "name": "Docker",
        "tier": "dev_tools",
        "what_it_is": "Containerization platform packaging code and all dependencies into portable images.",
        "why_used": "Ensures reproducible environments across development, testing, and production.",
        "why_selected": "Industry standard for container deployment on Railway, Render, and cloud VMs.",
        "benefits": ["Eliminates 'works on my machine' issues", "Reproducible builds", "Isolated dependencies"],
        "limitations": ["Image size overhead for PyTorch/ML dependencies (~1.2GB)"],
        "alternatives_considered": ["Direct host execution (environment drift risks)"],
        "configuration": "Multi-stage Dockerfile with python:3.11-slim base",
        "best_practices": ["Use multi-stage builds", "Run container as non-root user"],
    },
    {
        "id": "TECH_DEV_UPTIMEROBOT",
        "name": "UptimeRobot",
        "tier": "dev_tools",
        "what_it_is": "Cloud uptime and performance monitoring service.",
        "why_used": "Monitors /health uptime and mitigates free-tier backend cold starts.",
        "why_selected": "50 free monitors with 5-minute ping intervals and instant email/webhook alerts.",
        "benefits": ["Prevents server sleep on Render", "24/7 availability monitoring", "Incident alerting"],
        "limitations": ["5-minute minimum interval on free tier"],
        "alternatives_considered": ["Better Uptime", "Pingdom"],
        "configuration": "HTTP(s) keyword monitor pointing to https://api.memegpt.com/health",
        "best_practices": ["Monitor both API /health and web landing page"],
    },
    {
        "id": "TECH_DEV_SENTRY",
        "name": "Sentry",
        "tier": "dev_tools",
        "what_it_is": "Application performance monitoring and automated error tracking platform.",
        "why_used": "Captures unhandled exceptions, tracebacks, and performance bottlenecks in production.",
        "why_selected": "Generous free tier (5K errors/month), native FastAPI and Next.js SDKs.",
        "benefits": ["Real-time exception alerts", "Detailed stack trace with local variables", "Release tracking"],
        "limitations": ["Volume quota on free tier (mitigated via sampling)"],
        "alternatives_considered": ["LogRocket", "Rollbar", "Datadog (costly)"],
        "configuration": "sentry-sdk initialized in backend main.py with traces_sample_rate=0.1",
        "best_practices": ["Filter out PII and sensitive tokens before sending to Sentry"],
    },
]


# ── Service Functions ──────────────────────────────────────────────────────────

def get_all_tech_stack_components(tier: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all technologies or filter by tier (backend, frontend, ai_ml, infrastructure, dev_tools)."""
    if tier:
        tier_clean = tier.strip().lower()
        items = [t for t in TECH_STACK_CATALOG if t["tier"] == tier_clean]
    else:
        items = TECH_STACK_CATALOG

    return {
        "total_technologies": len(items),
        "tier_filter": tier,
        "technologies": items,
    }


def get_tech_stack_by_id(tech_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single technology entry by ID (e.g. TECH_BACKEND_FASTAPI)."""
    clean_id = tech_id.strip().upper()
    for t in TECH_STACK_CATALOG:
        if t["id"] == clean_id:
            return t
    return None


def search_tech_stack(query: str) -> Dict[str, Any]:
    """Full-text search across technology names, purposes, rationales, benefits, and best practices."""
    q_lower = query.strip().lower()
    matches = []

    for t in TECH_STACK_CATALOG:
        if (
            q_lower in t["name"].lower()
            or q_lower in t["what_it_is"].lower()
            or q_lower in t["why_used"].lower()
            or q_lower in t["why_selected"].lower()
            or any(q_lower in b.lower() for b in t.get("benefits", []))
            or any(q_lower in a.lower() for a in t.get("alternatives_considered", []))
        ):
            matches.append(t)

    return {
        "query": query,
        "total_matches": len(matches),
        "matches": matches,
    }


def get_tech_stack_tiers_summary() -> Dict[str, Any]:
    """Retrieve counts and distribution across all 5 technology tiers."""
    tier_counts = {}
    for t in TECH_STACK_CATALOG:
        tier = t["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    return {
        "total_technologies": len(TECH_STACK_CATALOG),
        "total_tiers": len(tier_counts),
        "tier_distribution": tier_counts,
    }


def evaluate_tech_stack_compliance() -> Dict[str, Any]:
    """Evaluate technology stack compliance against prompt.md Phase 6 specifications."""
    all_techs = TECH_STACK_CATALOG
    compliant_entries = 0

    required_keys = [
        "what_it_is",
        "why_used",
        "why_selected",
        "benefits",
        "limitations",
        "alternatives_considered",
        "configuration",
        "best_practices",
    ]

    for t in all_techs:
        if all(key in t for key in required_keys):
            compliant_entries += 1

    is_compliant = compliant_entries == len(all_techs) and len(all_techs) >= 20

    return {
        "status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
        "phase_6_requirement_met": is_compliant,
        "total_evaluated_technologies": len(all_techs),
        "fully_documented_technologies": compliant_entries,
        "compliance_percentage": f"{round((compliant_entries / len(all_techs)) * 100, 1)}%",
        "tiers_covered": ["backend", "frontend", "ai_ml", "infrastructure", "dev_tools"],
    }
