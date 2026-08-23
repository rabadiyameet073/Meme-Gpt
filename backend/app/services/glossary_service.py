"""Glossary and Technical Terminology Service for MemeGPT.
Specification: 17_Appendix/Glossary.md

Covers:
- 42 Technical Terms, Abbreviations, and Concepts across 5 Domains:
  1. AI/ML & Vector Search (ANN, BLIP, CLIP, Cosine Similarity, DistilRoBERTa, Embedding, Groq, HNSW, L2 Normalization, LLM, LPU, MiniLM, Named Vector, OCR, RAG, Vector, Vector Space)
  2. Architecture & Rendering (CSR, ISR, P50/P95, SSR)
  3. Backend & Storage (API Key, CORS, FastAPI, GIN Index, JWT, ORM, Pydantic, Qdrant, R2, Redis, Slug, Supabase, Token Bucket, Upstash, WebP)
  4. Security & Privacy (NSFW, PII, RBAC)
  5. Growth & Infrastructure (ASO, CDN)
- Category & initial letter filtering, search, and term definition lookups.
"""

from typing import Any, Dict, List, Optional


# ── Glossary Terms Database (42 Terms) ────────────────────────────────────────

GLOSSARY_TERMS: List[Dict[str, Any]] = [
    {
        "term": "ANN",
        "full_name": "Approximate Nearest Neighbor",
        "category": "ai_ml",
        "definition": "Search algorithm for finding vector similarity without exhaustive distance checks against every single vector in the index.",
        "usage_in_memegpt": "Used by Qdrant with HNSW graphs to perform sub-50ms vector searches over 10,000+ meme embeddings.",
    },
    {
        "term": "API Key",
        "full_name": "Application Programming Interface Key",
        "category": "backend_storage",
        "definition": "Secret cryptographic token for authenticating and attributing developer REST API client access.",
        "usage_in_memegpt": "Enforces tiered rate limits and access quotas for external Discord bots and developers.",
    },
    {
        "term": "ASO",
        "full_name": "App Store Optimization",
        "category": "marketing",
        "definition": "The process of optimizing mobile app titles, subtitles, keywords, screenshots, and ratings to maximize visibility in app stores.",
        "usage_in_memegpt": "Drives organic store downloads on iOS App Store and Google Play Store for MemeGPT mobile.",
    },
    {
        "term": "BLIP",
        "full_name": "Bootstrapping Language-Image Pre-training",
        "category": "ai_ml",
        "definition": "Salesforce multimodal vision-language model for generating natural language descriptions and captions from raw images.",
        "usage_in_memegpt": "Generates synthetic descriptive captions for uncaptioned meme image templates during pipeline ingestion.",
    },
    {
        "term": "CDN",
        "full_name": "Content Delivery Network",
        "category": "marketing",
        "definition": "Geographically distributed network of proxy edge servers that caches and delivers media content with low latency.",
        "usage_in_memegpt": "Cloudflare and Vercel edge networks serve meme images, WebP thumbnails, and static web assets globally.",
    },
    {
        "term": "CLIP",
        "full_name": "Contrastive Language-Image Pre-training",
        "category": "ai_ml",
        "definition": "OpenAI multimodal neural network that maps text and images into a shared semantic vector embedding space.",
        "usage_in_memegpt": "Generates 512-dim visual embeddings for zero-shot meme image search and visual style matching.",
    },
    {
        "term": "CORS",
        "full_name": "Cross-Origin Resource Sharing",
        "category": "backend_storage",
        "definition": "HTTP header-based browser security mechanism controlling which external domains are permitted to access API resources.",
        "usage_in_memegpt": "FastAPI CORSMiddleware restricts REST API calls to authorized web and mobile app origin domains.",
    },
    {
        "term": "Cosine Similarity",
        "full_name": "Cosine Similarity Metric",
        "category": "ai_ml",
        "definition": "Mathematical measure of similarity between two normalized non-zero vectors in inner product space (0.0 = orthogonal, 1.0 = identical).",
        "usage_in_memegpt": "Core metric used in Qdrant and Python scoring engine to calculate query-to-meme semantic alignment.",
    },
    {
        "term": "CSR",
        "full_name": "Client-Side Rendering",
        "category": "architecture",
        "definition": "Web rendering method where HTML and UI components are dynamically rendered in the client browser via JavaScript.",
        "usage_in_memegpt": "Used in the interactive MemeGPT search interface for instant client-side filtering and chip suggestions.",
    },
    {
        "term": "DistilRoBERTa",
        "full_name": "Distilled Robustly Optimized BERT Approach",
        "category": "ai_ml",
        "definition": "Lightweight, compressed transformer model distilled from RoBERTa for high-speed sequence classification.",
        "usage_in_memegpt": "Performs sub-30ms emotion classification (joy, anger, sadness, surprise, confusion) on user search queries.",
    },
    {
        "term": "Embedding",
        "full_name": "Dense Vector Embedding",
        "category": "ai_ml",
        "definition": "Continuous vector representation of high-dimensional text or image semantics where geometric distance reflects meaning.",
        "usage_in_memegpt": "384-dimensional dense floating-point arrays generated by all-MiniLM-L6-v2 representing meme context.",
    },
    {
        "term": "FastAPI",
        "full_name": "FastAPI Web Framework",
        "category": "backend_storage",
        "definition": "Modern, high-performance Python web framework for building REST APIs backed by Starlette, Pydantic, and OpenAPI.",
        "usage_in_memegpt": "Core backend service framework handling search requests, intent extraction, rate limiting, and analytics.",
    },
    {
        "term": "GIN Index",
        "full_name": "Generalized Inverted Index",
        "category": "backend_storage",
        "definition": "PostgreSQL database index designed for handling composite and array data types containing multiple values.",
        "usage_in_memegpt": "Accelerates exact-match tag and keyword array queries in PostgreSQL metadata tables.",
    },
    {
        "term": "Groq",
        "full_name": "Groq LPU AI Cloud",
        "category": "ai_ml",
        "definition": "AI acceleration cloud platform utilizing custom Language Processing Unit (LPU) silicon for ultra-low latency LLM inference.",
        "usage_in_memegpt": "Powers Llama 3.1 8B intent parsing with sub-200ms response times for query keyword & emotion extraction.",
    },
    {
        "term": "HNSW",
        "full_name": "Hierarchical Navigable Small World",
        "category": "ai_ml",
        "definition": "Graph-based ANN vector search algorithm organizing vectors into multi-layer hierarchical graphs with logarithmic search complexity.",
        "usage_in_memegpt": "Primary indexing algorithm configured on Qdrant collections for ultra-fast cosine similarity search.",
    },
    {
        "term": "ISR",
        "full_name": "Incremental Static Regeneration",
        "category": "architecture",
        "definition": "Next.js rendering feature enabling static pages to be re-rendered in the background on-demand without a full site rebuild.",
        "usage_in_memegpt": "Keeps 10,000+ meme SEO pages and trending lists up-to-date while serving static CDN cached HTML.",
    },
    {
        "term": "JWT",
        "full_name": "JSON Web Token",
        "category": "backend_storage",
        "definition": "Compact, URL-safe cryptographic token standard (RFC 7519) for transmitting claims securely between client and server.",
        "usage_in_memegpt": "Authenticates registered users and authorizes collection sync, favorites, and preference mutations.",
    },
    {
        "term": "L2 Normalization",
        "full_name": "Euclidean / L2 Vector Normalization",
        "category": "ai_ml",
        "definition": "Scaling a vector so that its Euclidean norm (magnitude) equals exactly 1.0 (unit vector).",
        "usage_in_memegpt": "Applied to all MiniLM and CLIP embeddings so that inner dot product calculations are equivalent to cosine similarity.",
    },
    {
        "term": "LLM",
        "full_name": "Large Language Model",
        "category": "ai_ml",
        "definition": "Deep neural network with billions of parameters trained on vast text corpora for language understanding and reasoning.",
        "usage_in_memegpt": "Llama 3.1 8B extracts situations, emotions, tone, and search keywords from colloquial user queries.",
    },
    {
        "term": "LPU",
        "full_name": "Language Processing Unit",
        "category": "ai_ml",
        "definition": "Custom semiconductor architecture engineered by Groq optimized specifically for sequential tensor and token processing.",
        "usage_in_memegpt": "Provides deterministic 500+ tokens/sec LLM inference speed for zero-latency user search parsing.",
    },
    {
        "term": "MiniLM",
        "full_name": "all-MiniLM-L6-v2 Sentence Transformer",
        "category": "ai_ml",
        "definition": "Lightweight 6-layer transformer distilled from MiniLM producing 384-dimensional text embeddings.",
        "usage_in_memegpt": "Primary dense text embedding engine running locally on CPU in ~50ms with 22MB memory footprint.",
    },
    {
        "term": "Named Vector",
        "full_name": "Qdrant Named Vector Space",
        "category": "ai_ml",
        "definition": "Vector database feature allowing a single indexed point/record to contain multiple distinct vector spaces (e.g. text vs image).",
        "usage_in_memegpt": "Allows MemeGPT to store both 384-dim MiniLM text vectors and 512-dim CLIP image vectors on each meme record.",
    },
    {
        "term": "NSFW",
        "full_name": "Not Safe For Work",
        "category": "security",
        "definition": "Content classification label identifying sexually explicit, overly violent, or profane media inappropriate for public viewing.",
        "usage_in_memegpt": "Automated content moderation filter that quarantines explicit memes and respects user safe-search toggles.",
    },
    {
        "term": "OCR",
        "full_name": "Optical Character Recognition",
        "category": "ai_ml",
        "definition": "Computer vision technology for detecting, extracting, and transcribing visual text printed on raster images.",
        "usage_in_memegpt": "Extracts top-text and bottom-text punchlines from meme images during ingestion via Tesseract.",
    },
    {
        "term": "ORM",
        "full_name": "Object-Relational Mapping",
        "category": "backend_storage",
        "definition": "Programming technique translating database relational tables and records into native object-oriented code entities.",
        "usage_in_memegpt": "Prisma ORM provides type-safe schema definitions and automated migrations across SQLite and PostgreSQL.",
    },
    {
        "term": "P50/P95",
        "full_name": "50th and 95th Percentile Latencies",
        "category": "architecture",
        "definition": "Statistical distribution metrics where P50 represents median latency and P95 represents the 95th percentile response threshold.",
        "usage_in_memegpt": "Enforces SLA targets: P50 < 1.0s and P95 < 2.5s for end-to-end natural language search queries.",
    },
    {
        "term": "PII",
        "full_name": "Personally Identifiable Information",
        "category": "security",
        "definition": "Any data that could potentially identify a specific individual (names, emails, IP addresses, phone numbers).",
        "usage_in_memegpt": "Strict privacy filter strips PII before writing telemetry to logs, Sentry, or vector indices.",
    },
    {
        "term": "Pydantic",
        "full_name": "Pydantic Data Validation Library",
        "category": "backend_storage",
        "definition": "Data parsing and validation library using standard Python type annotations to enforce runtime schema guarantees.",
        "usage_in_memegpt": "Validates API request payloads, query params, DTO schemas, and environment configuration variables.",
    },
    {
        "term": "Qdrant",
        "full_name": "Qdrant Vector Similarity Search Engine",
        "category": "ai_ml",
        "definition": "Production-grade, open-source vector database with payload-based filtering, named vectors, and gRPC/REST APIs.",
        "usage_in_memegpt": "Stores 10,000+ meme embeddings and conducts real-time vector similarity matching with metadata filtering.",
    },
    {
        "term": "R2",
        "full_name": "Cloudflare R2 Object Storage",
        "category": "backend_storage",
        "definition": "S3-compatible distributed blob storage service featuring zero egress bandwidth fees and global edge replication.",
        "usage_in_memegpt": "Stores master meme media files (GIF, PNG, MP4, WebP) with zero egress bandwidth expenses.",
    },
    {
        "term": "RAG",
        "full_name": "Retrieval-Augmented Generation",
        "category": "ai_ml",
        "definition": "AI architecture that retrieves relevant domain data from vector databases to augment prompt context for language models.",
        "usage_in_memegpt": "Retrieves top meme candidates before re-ranking and generating contextual meme recommendation explanations.",
    },
    {
        "term": "RBAC",
        "full_name": "Role-Based Access Control",
        "category": "security",
        "definition": "Security access model restricting system and API capabilities based on assigned user roles (Admin, Member, Developer).",
        "usage_in_memegpt": "Protects internal admin moderation routes, meme tagging tools, and webhook management endpoints.",
    },
    {
        "term": "Redis",
        "full_name": "Remote Dictionary Server",
        "category": "backend_storage",
        "definition": "High-performance in-memory key-value data structure store used for caching, pub/sub, and fast rate limiting.",
        "usage_in_memegpt": "Caches identical search queries and intent parsing outputs with 24-hour TTL to reduce backend compute.",
    },
    {
        "term": "Slug",
        "full_name": "URL Slug Identifier",
        "category": "backend_storage",
        "definition": "Human-readable, URL-friendly unique string composed of lowercase alphanumeric characters and hyphens.",
        "usage_in_memegpt": "Permanent identifier for meme pages (e.g. `this-is-fine`, `drake-hotline-bling`) to optimize SEO routing.",
    },
    {
        "term": "SSR",
        "full_name": "Server-Side Rendering",
        "category": "architecture",
        "definition": "Rendering webpage HTML on the server on each request prior to sending the fully formed document to the client.",
        "usage_in_memegpt": "Powers dynamic Next.js 14 meme landing pages for instant web crawler indexing and social link previews.",
    },
    {
        "term": "Supabase",
        "full_name": "Supabase Managed Backend Platform",
        "category": "backend_storage",
        "definition": "Open-source developer platform built on managed PostgreSQL, Auth, Row Level Security, and Realtime listeners.",
        "usage_in_memegpt": "Hosts production PostgreSQL database, handles connection pooling via PgBouncer, and provides authentication.",
    },
    {
        "term": "Token Bucket",
        "full_name": "Token Bucket Algorithm",
        "category": "backend_storage",
        "definition": "Rate limiting algorithm maintaining a bucket of tokens refilled at a constant rate, allowing controlled traffic bursts.",
        "usage_in_memegpt": "Throttles anonymous and authenticated API requests to protect vector search from DDoS and scraping.",
    },
    {
        "term": "Upstash",
        "full_name": "Upstash Serverless Redis & Kafka",
        "category": "backend_storage",
        "definition": "Serverless Redis database offering pay-per-request pricing, REST APIs, and zero idle infrastructure costs.",
        "usage_in_memegpt": "Provides edge caching layer for search responses and sliding-window rate limiting in serverless environments.",
    },
    {
        "term": "Vector",
        "full_name": "Vector / Numeric Array",
        "category": "ai_ml",
        "definition": "One-dimensional array of floating-point numbers encoding linguistic or visual semantics in mathematical coordinates.",
        "usage_in_memegpt": "384-dimensional text vectors and 512-dimensional visual vectors representing meme semantics.",
    },
    {
        "term": "Vector Space",
        "full_name": "Semantic Vector Embedding Space",
        "category": "ai_ml",
        "definition": "High-dimensional coordinate space where conceptual and semantic similarity correlates directly with geometric proximity.",
        "usage_in_memegpt": "384-dimensional Euclidean space where related feelings (e.g. 'exhausted' and 'burnout') cluster tightly together.",
    },
    {
        "term": "WebP",
        "full_name": "WebP Modern Image Format",
        "category": "backend_storage",
        "definition": "Raster image format developed by Google providing superior lossless and lossy compression compared to JPEG and PNG.",
        "usage_in_memegpt": "Standard format for all generated meme thumbnails, cutting payload sizes by 30-50% for fast mobile loading.",
    },
]


# ── Service Functions ──────────────────────────────────────────────────────────

def get_all_glossary_terms(
    category: Optional[str] = None,
    letter: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve all 42 glossary terms with optional category or initial letter filtering."""
    items = GLOSSARY_TERMS

    if category:
        cat_clean = category.strip().lower()
        items = [t for t in items if t["category"] == cat_clean]

    if letter:
        let_clean = letter.strip().upper()
        items = [t for t in items if t["term"].upper().startswith(let_clean)]

    # Sort alphabetically by term
    sorted_items = sorted(items, key=lambda x: x["term"].upper())

    return {
        "total_terms": len(sorted_items),
        "category_filter": category,
        "letter_filter": letter,
        "terms": sorted_items,
    }


def get_glossary_term_by_name(term_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve exact glossary term definition by term string or acronym."""
    t_clean = term_name.strip().lower()
    for t in GLOSSARY_TERMS:
        if t["term"].lower() == t_clean or t.get("full_name", "").lower() == t_clean:
            return t
    return None


def search_glossary(query: str) -> Dict[str, Any]:
    """Full-text search across terms, full names, definitions, and MemeGPT usage descriptions."""
    q_lower = query.strip().lower()
    matches = []

    for t in GLOSSARY_TERMS:
        if (
            q_lower in t["term"].lower()
            or q_lower in t.get("full_name", "").lower()
            or q_lower in t["definition"].lower()
            or q_lower in t.get("usage_in_memegpt", "").lower()
        ):
            matches.append(t)

    sorted_matches = sorted(matches, key=lambda x: x["term"].upper())

    return {
        "query": query,
        "total_matches": len(sorted_matches),
        "matches": sorted_matches,
    }


def get_glossary_summary() -> Dict[str, Any]:
    """Retrieve summary statistics across all glossary terms, domain distributions, and initial letters."""
    category_counts = {}
    letter_counts = {}

    for t in GLOSSARY_TERMS:
        cat = t["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        let = t["term"][0].upper()
        letter_counts[let] = letter_counts.get(let, 0) + 1

    return {
        "total_terms": len(GLOSSARY_TERMS),
        "categories_count": len(category_counts),
        "category_distribution": category_counts,
        "letter_distribution": letter_counts,
        "domains": ["ai_ml", "backend_storage", "architecture", "security", "marketing"],
    }
