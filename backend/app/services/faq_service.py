"""Comprehensive FAQ Knowledge Base Service for MemeGPT.
Specification: 15_FAQs/General_FAQ.md

Covers:
- 21 Question & Answer pairs across 3 categories: General (8), Technical (8), API (5)
- Full-text search and category filtering
- AI Model inventory table (6 models)
- Graceful Degradation failure matrix
"""

from typing import Any, Dict, List, Optional


# ── AI Model Specifications ───────────────────────────────────────────────────

AI_MODELS_CATALOG = [
    {"model": "MiniLM-L6-v2", "purpose": "Text embedding (semantic search)", "size": "22MB", "runtime": "Local CPU/GPU"},
    {"model": "DistilRoBERTa", "purpose": "Emotion detection (7 emotions)", "size": "250MB", "runtime": "Local CPU/GPU"},
    {"model": "Llama 3.1 8B (Groq)", "purpose": "Intent parsing & JSON extraction", "size": "Cloud", "runtime": "Groq LPU (~200ms)"},
    {"model": "BLIP", "purpose": "Image captioning (offline indexing)", "size": "446MB", "runtime": "Offline Pipeline"},
    {"model": "CLIP ViT-B/32", "purpose": "Image embedding (offline indexing)", "size": "400MB", "runtime": "Offline Pipeline"},
    {"model": "Tesseract", "purpose": "OCR text extraction (offline indexing)", "size": "30MB", "runtime": "Offline Pipeline"},
]


# ── Graceful Degradation Matrix ────────────────────────────────────────────────

GRACEFUL_DEGRADATION_MATRIX = [
    {
        "subsystem": "Groq LLM API",
        "failure_scenario": "Groq API outage / rate limit / bad token",
        "degradation_behavior": "Skip intent parsing; fallback to raw query embedding directly with MiniLM.",
        "user_impact": "Search still functions with high accuracy, slightly reduced nuance on complex queries.",
    },
    {
        "subsystem": "Qdrant Vector DB",
        "failure_scenario": "Qdrant cluster unreachable / timeout",
        "degradation_behavior": "Serve cached search results from Redis or fallback to relational DB trending memes.",
        "user_impact": "Popular memes returned; custom semantic search temporarily paused.",
    },
    {
        "subsystem": "Redis Cache",
        "failure_scenario": "Redis down / network partition",
        "degradation_behavior": "Bypass cache layer; compute embeddings and search queries fresh on every request.",
        "user_impact": "Latency increases slightly (from ~15ms cached to ~180ms fresh), 100% functional.",
    },
    {
        "subsystem": "Total External Outage",
        "failure_scenario": "Groq + Qdrant + Redis simultaneously offline",
        "degradation_behavior": "FastAPI serves curated popular trending memes directly from SQLite/PostgreSQL.",
        "user_impact": "Zero downtime 500 error; UI renders offline fallback trending collection.",
    },
]


# ── 21 Categorized FAQ Items ───────────────────────────────────────────────────

FAQS_DATABASE: List[Dict[str, Any]] = [
    # ── General FAQs ───────────────────────────────────────────────────────────
    {
        "id": "FAQ_GEN_1",
        "category": "general",
        "question": "What is MemeGPT?",
        "answer": "MemeGPT is an AI-powered meme recommendation engine. You describe a situation, emotion, or context in natural language, and MemeGPT uses AI to find the most relevant memes — no keyword hunting required.",
        "tags": ["overview", "product", "natural language", "ai"],
    },
    {
        "id": "FAQ_GEN_2",
        "category": "general",
        "question": "How is MemeGPT different from Giphy or Google Image Search?",
        "answer": "Traditional meme search requires exact keywords ('sad dog meme'). MemeGPT understands natural language — you can type 'when your code compiles but the output is completely wrong' and it finds contextually perfect memes. It uses emotion detection, semantic search, and LLM-powered intent parsing.",
        "tags": ["comparison", "giphy", "google", "semantic search"],
    },
    {
        "id": "FAQ_GEN_3",
        "category": "general",
        "question": "Is MemeGPT free?",
        "answer": "Yes. The MVP is completely free with no account required. Future Pro tiers may add higher rate limits and exclusive features for $5/month.",
        "tags": ["pricing", "free", "pro tier", "cost"],
    },
    {
        "id": "FAQ_GEN_4",
        "category": "general",
        "question": "Do I need to create an account?",
        "answer": "No. MemeGPT is fully anonymous by default. No login, no signup, no tracking. You can optionally create an account in Phase 3 to sync favorites across devices.",
        "tags": ["privacy", "account", "anonymous", "signup"],
    },
    {
        "id": "FAQ_GEN_5",
        "category": "general",
        "question": "What meme formats are supported?",
        "answer": "GIF, PNG/JPG (static images), MP4 (video), and WebP (stickers). Each meme is available in multiple formats when possible.",
        "tags": ["formats", "gif", "mp4", "webp", "png"],
    },
    {
        "id": "FAQ_GEN_6",
        "category": "general",
        "question": "How many memes does MemeGPT have?",
        "answer": "MVP launches with ~1,000 curated memes. Phase 2 expands to 5,000, Phase 3 to 25,000, and Phase 4 targets 100,000+ memes.",
        "tags": ["catalog size", "mvp", "dataset", "growth"],
    },
    {
        "id": "FAQ_GEN_7",
        "category": "general",
        "question": "Is there a mobile app?",
        "answer": "A React Native (Expo) mobile app is planned for Phase 2, targeting both iOS and Android.",
        "tags": ["mobile", "react native", "expo", "ios", "android"],
    },
    {
        "id": "FAQ_GEN_8",
        "category": "general",
        "question": "Does MemeGPT work offline?",
        "answer": "Not currently. Search requires the backend API. However, the mobile app will cache the last 50 viewed memes for offline access.",
        "tags": ["offline", "cache", "mobile", "network"],
    },

    # ── Technical FAQs ─────────────────────────────────────────────────────────
    {
        "id": "FAQ_TECH_1",
        "category": "technical",
        "question": "What AI models does MemeGPT use?",
        "answer": "MemeGPT uses MiniLM-L6-v2 (text embeddings, 22MB), DistilRoBERTa (emotion detection, 250MB), Llama 3.1 8B via Groq (intent parsing), BLIP (image captioning, 446MB), CLIP ViT-B/32 (image embeddings, 400MB), and Tesseract (OCR extraction, 30MB).",
        "tags": ["models", "ai", "minilm", "groq", "llama", "distilroberta", "clip", "blip"],
    },
    {
        "id": "FAQ_TECH_2",
        "category": "technical",
        "question": "Why FastAPI instead of Express.js?",
        "answer": "FastAPI was chosen for: (1) Python ML ecosystem native integration (sentence-transformers, torch), (2) Automatic Swagger & ReDoc OpenAPI generation, (3) High async I/O performance on Uvicorn, and (4) Strict type safety and Pydantic validation.",
        "tags": ["fastapi", "express", "architecture", "python"],
    },
    {
        "id": "FAQ_TECH_3",
        "category": "technical",
        "question": "Why Qdrant instead of Pinecone?",
        "answer": "Qdrant provides: (1) Generous 1GB free tier, (2) Named vectors to store text, image, and composite embeddings separately, (3) Rich payload filtering by NSFW, format, and category during vector search, and (4) Open-source flexibility for self-hosting.",
        "tags": ["qdrant", "pinecone", "vector database", "embeddings"],
    },
    {
        "id": "FAQ_TECH_4",
        "category": "technical",
        "question": "Why Groq instead of OpenAI?",
        "answer": "Groq provides: (1) 6,000 free requests/day, (2) ~200ms ultra-low inference latency on LPUs, (3) High quality structured JSON extraction with Llama 3.1 8B, and (4) Graceful zero-failure fallback if the service is unreachable.",
        "tags": ["groq", "openai", "latency", "llama"],
    },
    {
        "id": "FAQ_TECH_5",
        "category": "technical",
        "question": "How does the scoring algorithm work?",
        "answer": "Each meme receives a composite score (0.0 to 1.0) composed of: Keyword Match (30%), Semantic Similarity (20%), Popularity (20%), Primary/Secondary Emotion Match (15% + 8%), Recency (10%), and Format Preference (5% bonus).",
        "tags": ["scoring", "algorithm", "weights", "ranking"],
    },
    {
        "id": "FAQ_TECH_6",
        "category": "technical",
        "question": "What happens if an external service goes down?",
        "answer": "MemeGPT degrades gracefully: Groq down -> raw query embedding; Qdrant down -> cached Redis or trending memes; Redis down -> fresh search bypass; All down -> SQLite/Postgres fallback trending list.",
        "tags": ["reliability", "fallback", "degradation", "resilience"],
    },
    {
        "id": "FAQ_TECH_7",
        "category": "technical",
        "question": "How do I add new memes?",
        "answer": "Memes are ingested via a 4-step pipeline: (1) Add raw source files to datasets/, (2) Run python scripts/preprocess_memes.py, (3) Run python scripts/generate_embeddings.py, and (4) Run python scripts/index_qdrant.py.",
        "tags": ["pipeline", "indexing", "ingestion", "scripts"],
    },
    {
        "id": "FAQ_TECH_8",
        "category": "technical",
        "question": "What is the maximum query length?",
        "answer": "The maximum query length is 2,000 characters. This accommodates multi-line conversation context pastes while preventing denial-of-service abuse.",
        "tags": ["query length", "validation", "limits"],
    },

    # ── API FAQs ───────────────────────────────────────────────────────────────
    {
        "id": "FAQ_API_1",
        "category": "api",
        "question": "What is the API rate limit?",
        "answer": "Free tier (no key): 60 requests/minute per IP, with a dedicated 30 requests/minute limit for search. Developer tier (API key): 300 requests/minute.",
        "tags": ["rate limits", "throttling", "ip", "api key"],
    },
    {
        "id": "FAQ_API_2",
        "category": "api",
        "question": "How do I get an API key?",
        "answer": "Developer API keys will become available in Phase 2. Sign up at memegpt.com/developer with your email address to generate keys and access higher throughput.",
        "tags": ["api key", "developer", "signup"],
    },
    {
        "id": "FAQ_API_3",
        "category": "api",
        "question": "Is the API RESTful?",
        "answer": "Yes. All endpoints follow strict REST conventions with JSON request and response payloads, standard HTTP status codes, and versioned URL paths (/api/v1/).",
        "tags": ["rest", "api standard", "json", "http"],
    },
    {
        "id": "FAQ_API_4",
        "category": "api",
        "question": "Can I use MemeGPT in my Discord bot?",
        "answer": "Yes! The REST API can be integrated into Discord, Slack, Telegram, or any custom client in any programming language. A turnkey pre-built Discord bot is scheduled for Phase 3.",
        "tags": ["discord", "bot", "integration", "slack"],
    },
    {
        "id": "FAQ_API_5",
        "category": "api",
        "question": "Is there a WebSocket API for real-time?",
        "answer": "Not currently. The REST API efficiently handles discrete meme search queries. WebSocket streaming support is planned for conversational refinement in Phase 3.",
        "tags": ["websocket", "realtime", "chat", "streaming"],
    },
]


def get_all_faqs(category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all FAQ entries or filter by category (general, technical, api)."""
    if category:
        cat_lower = category.strip().lower()
        items = [f for f in FAQS_DATABASE if f["category"] == cat_lower]
    else:
        items = FAQS_DATABASE

    return {
        "total_faqs": len(items),
        "category_filter": category,
        "faqs": items,
    }


def get_faq_by_id(faq_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single FAQ entry by its ID (e.g. FAQ_GEN_1, FAQ_TECH_4)."""
    faq_id_clean = faq_id.strip().upper()
    for f in FAQS_DATABASE:
        if f["id"] == faq_id_clean:
            return f
    return None


def search_faqs(query: str) -> Dict[str, Any]:
    """Full-text search across FAQ questions, answers, and tags."""
    q_lower = query.strip().lower()
    matches = []

    for f in FAQS_DATABASE:
        if (
            q_lower in f["question"].lower()
            or q_lower in f["answer"].lower()
            or any(q_lower in tag.lower() for tag in f.get("tags", []))
        ):
            matches.append(f)

    return {
        "query": query,
        "total_matches": len(matches),
        "results": matches,
    }


def get_faq_categories_summary() -> Dict[str, Any]:
    """Return counts and metadata for each FAQ category."""
    categories = {}
    for f in FAQS_DATABASE:
        cat = f["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_faqs": len(FAQS_DATABASE),
        "total_categories": len(categories),
        "category_counts": categories,
    }


def get_ai_models_catalog() -> Dict[str, Any]:
    """Return the 6 AI models used across MemeGPT search and offline ingestion."""
    return {
        "total_models": len(AI_MODELS_CATALOG),
        "models": AI_MODELS_CATALOG,
    }


def get_graceful_degradation_matrix() -> Dict[str, Any]:
    """Return external service failure degradation paths."""
    return {
        "total_scenarios": len(GRACEFUL_DEGRADATION_MATRIX),
        "matrix": GRACEFUL_DEGRADATION_MATRIX,
    }
