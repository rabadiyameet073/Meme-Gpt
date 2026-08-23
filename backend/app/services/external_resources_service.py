"""External Resources and Citations Knowledge Base Service for MemeGPT.
Specification: 16_References/External_Resources.md

Covers:
- 25 Official Documentation Links across Frameworks, AI/ML, Infrastructure, and Dev Tools
- 6 Foundational AI/ML Research Papers
- 4 Meme Data Sources (Imgflip, Reddit, Tenor, Know Your Meme)
- 5 Community & Developer Learning Channels
- Full-text search and category filtering
"""

from typing import Any, Dict, List, Optional


# ── 1. Official Documentation Links ────────────────────────────────────────────

OFFICIAL_DOCUMENTATION: List[Dict[str, Any]] = [
    # Frameworks & Libraries
    {"category": "frameworks_libraries", "name": "FastAPI", "url": "https://fastapi.tiangolo.com", "description": "Modern, fast Python web framework for building APIs with type hints."},
    {"category": "frameworks_libraries", "name": "React", "url": "https://react.dev", "description": "The library for web and native user interfaces."},
    {"category": "frameworks_libraries", "name": "Next.js", "url": "https://nextjs.org/docs", "description": "The React framework for the web with SSR and App Router."},
    {"category": "frameworks_libraries", "name": "Vite", "url": "https://vitejs.dev", "description": "Next generation frontend tooling and development server."},
    {"category": "frameworks_libraries", "name": "TailwindCSS", "url": "https://tailwindcss.com/docs", "description": "Utility-first CSS framework for rapid UI development."},
    {"category": "frameworks_libraries", "name": "React Native", "url": "https://reactnative.dev", "description": "Cross-platform native mobile application framework."},
    {"category": "frameworks_libraries", "name": "Expo", "url": "https://docs.expo.dev", "description": "Ecosystem of tools, libraries, and services for universal React apps."},

    # AI/ML
    {"category": "ai_ml", "name": "HuggingFace Hub", "url": "https://huggingface.co", "description": "Platform for sharing machine learning models, datasets, and demos."},
    {"category": "ai_ml", "name": "sentence-transformers", "url": "https://www.sbert.net", "description": "Python framework for state-of-the-art sentence, text and image embeddings."},
    {"category": "ai_ml", "name": "MiniLM-L6-v2 Model Card", "url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2", "description": "384-dimensional dense embedding model for semantic search."},
    {"category": "ai_ml", "name": "CLIP Model Card", "url": "https://huggingface.co/openai/clip-vit-base-patch32", "description": "Vision-language model connecting images and text in shared latent space."},
    {"category": "ai_ml", "name": "BLIP Model Card", "url": "https://huggingface.co/Salesforce/blip-image-captioning-base", "description": "Bootstrapping Language-Image Pre-training for automated captioning."},
    {"category": "ai_ml", "name": "Emotion Model", "url": "https://huggingface.co/j-hartmann/emotion-english-distilroberta-base", "description": "DistilRoBERTa model fine-tuned for 7-class emotion classification."},
    {"category": "ai_ml", "name": "Groq", "url": "https://console.groq.com/docs", "description": "Ultra-low latency LPU cloud inference for Llama 3.1 8B."},

    # Infrastructure
    {"category": "infrastructure", "name": "Qdrant", "url": "https://qdrant.tech/documentation", "description": "Vector similarity search engine and payload database."},
    {"category": "infrastructure", "name": "Supabase", "url": "https://supabase.com/docs", "description": "Open source Firebase alternative powered by PostgreSQL."},
    {"category": "infrastructure", "name": "Vercel", "url": "https://vercel.com/docs", "description": "Cloud platform for static sites and Serverless Next.js functions."},
    {"category": "infrastructure", "name": "Render", "url": "https://render.com/docs", "description": "Unified cloud platform to build and run backend apps and services."},
    {"category": "infrastructure", "name": "Railway", "url": "https://docs.railway.app", "description": "Infrastructure platform for fast FastAPI deployment with zero config."},
    {"category": "infrastructure", "name": "Cloudflare R2", "url": "https://developers.cloudflare.com/r2", "description": "S3-compatible distributed object storage with zero egress fees."},
    {"category": "infrastructure", "name": "Upstash", "url": "https://upstash.com/docs", "description": "Serverless Redis cache with REST API and per-request pricing."},

    # Development Tools
    {"category": "development_tools", "name": "Prisma", "url": "https://www.prisma.io/docs", "description": "Next-generation ORM and visual schema database browser."},
    {"category": "development_tools", "name": "Ruff", "url": "https://docs.astral.sh/ruff", "description": "Extremely fast Python linter and code formatter written in Rust."},
    {"category": "development_tools", "name": "Sentry", "url": "https://docs.sentry.io", "description": "Application monitoring and error tracking software."},
    {"category": "development_tools", "name": "GitHub Actions", "url": "https://docs.github.com/en/actions", "description": "Automated CI/CD workflows and automated test execution."},
]


# ── 2. Research Papers ─────────────────────────────────────────────────────────

RESEARCH_PAPERS: List[Dict[str, Any]] = [
    {
        "id": "PAPER_1",
        "paper": "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
        "authors": "Reimers & Gurevych",
        "year": 2019,
        "relevance": "Foundation for MiniLM sentence embeddings and cosine semantic search.",
    },
    {
        "id": "PAPER_2",
        "paper": "Learning Transferable Visual Models From Natural Language Supervision (CLIP)",
        "authors": "Radford et al.",
        "year": 2021,
        "relevance": "Vision-language alignment enabling direct multimodal text-to-image similarity.",
    },
    {
        "id": "PAPER_3",
        "paper": "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation",
        "authors": "Li et al.",
        "year": 2022,
        "relevance": "Automated high-fidelity meme image captioning for synthetic text descriptions.",
    },
    {
        "id": "PAPER_4",
        "paper": "MTEB: Massive Text Embedding Benchmark",
        "authors": "Muennighoff et al.",
        "year": 2023,
        "relevance": "Standardized benchmark framework used to select all-MiniLM-L6-v2 for latency vs quality.",
    },
    {
        "id": "PAPER_5",
        "paper": "Efficient Estimation of Word Representations in Vector Space (Word2Vec)",
        "authors": "Mikolov et al.",
        "year": 2013,
        "relevance": "Foundational vector space representation concepts and distributed semantics.",
    },
    {
        "id": "PAPER_6",
        "paper": "Attention Is All You Need",
        "authors": "Vaswani et al.",
        "year": 2017,
        "relevance": "Transformer multi-head self-attention architecture underlying BERT, RoBERTa, and Llama.",
    },
]


# ── 3. Meme Data Sources ───────────────────────────────────────────────────────

MEME_DATA_SOURCES: List[Dict[str, Any]] = [
    {
        "source": "Imgflip",
        "type": "Meme templates + metadata",
        "api": "Public API",
        "usage": "Primary meme template catalog and baseline viral scores.",
        "url": "https://api.imgflip.com/get_memes",
    },
    {
        "source": "Reddit (r/memes)",
        "type": "Trending memes",
        "api": "PRAW / Reddit API",
        "usage": "Viral meme discovery and dynamic trend scoring feed.",
        "url": "https://www.reddit.com/r/memes",
    },
    {
        "source": "Tenor (Google)",
        "type": "GIF search",
        "api": "Public API",
        "usage": "High quality animated GIF format source and search indexing.",
        "url": "https://tenor.com",
    },
    {
        "source": "Know Your Meme",
        "type": "Meme encyclopedia",
        "api": "No API (ethical scraping / research)",
        "usage": "Origin stories, cultural context, emotional connotations, and alias keywords.",
        "url": "https://knowyourmeme.com",
    },
]


# ── 4. Community & Learning Channels ──────────────────────────────────────────

COMMUNITY_RESOURCES: List[Dict[str, Any]] = [
    {"name": "FastAPI Discord", "type": "Community", "url": "https://discord.gg/fastapi", "description": "Official FastAPI community for async Python web services."},
    {"name": "r/FastAPI", "type": "Reddit", "url": "https://reddit.com/r/FastAPI", "description": "Reddit discussions, tutorials, and architecture patterns for FastAPI."},
    {"name": "HuggingFace Forums", "type": "Community", "url": "https://discuss.huggingface.co", "description": "Discussions on transformers, sentence-transformers, and model optimization."},
    {"name": "Qdrant Discord", "type": "Community", "url": "https://discord.gg/qdrant", "description": "Vector database developers, tuning, and indexing help."},
    {"name": "Supabase Discord", "type": "Community", "url": "https://discord.supabase.com", "description": "PostgreSQL, auth, real-time, and database hosting community."},
]


# ── 5. Service Functions ──────────────────────────────────────────────────────

def get_official_documentation(category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve official documentation links with optional category filter."""
    if category:
        cat_lower = category.strip().lower()
        items = [d for d in OFFICIAL_DOCUMENTATION if d["category"] == cat_lower]
    else:
        items = OFFICIAL_DOCUMENTATION

    return {
        "total_documentation_links": len(items),
        "category_filter": category,
        "documentation": items,
    }


def get_research_papers() -> Dict[str, Any]:
    """Retrieve the 6 foundational AI/ML research papers underlying MemeGPT."""
    return {
        "total_papers": len(RESEARCH_PAPERS),
        "papers": RESEARCH_PAPERS,
    }


def get_meme_data_sources() -> Dict[str, Any]:
    """Retrieve external meme data sources and API ingestion methods."""
    return {
        "total_sources": len(MEME_DATA_SOURCES),
        "sources": MEME_DATA_SOURCES,
    }


def get_community_resources() -> Dict[str, Any]:
    """Retrieve community Discord servers, Reddit forums, and discussion boards."""
    return {
        "total_resources": len(COMMUNITY_RESOURCES),
        "resources": COMMUNITY_RESOURCES,
    }


def search_external_resources(query: str) -> Dict[str, Any]:
    """Full-text search across documentation links, research papers, meme sources, and community forums."""
    q_lower = query.strip().lower()
    matches: List[Dict[str, Any]] = []

    # Search docs
    for d in OFFICIAL_DOCUMENTATION:
        if q_lower in d["name"].lower() or q_lower in d["description"].lower() or q_lower in d["url"].lower():
            matches.append({"resource_type": "documentation", **d})

    # Search papers
    for p in RESEARCH_PAPERS:
        if q_lower in p["paper"].lower() or q_lower in p["authors"].lower() or q_lower in p["relevance"].lower():
            matches.append({"resource_type": "research_paper", "name": p["paper"], "details": p})

    # Search meme sources
    for s in MEME_DATA_SOURCES:
        if q_lower in s["source"].lower() or q_lower in s["usage"].lower() or q_lower in s["type"].lower():
            matches.append({"resource_type": "meme_data_source", "name": s["source"], "details": s})

    # Search community
    for c in COMMUNITY_RESOURCES:
        if q_lower in c["name"].lower() or q_lower in c["description"].lower() or q_lower in c["url"].lower():
            matches.append({"resource_type": "community", **c})

    return {
        "query": query,
        "total_matches": len(matches),
        "matches": matches,
    }


def get_external_resources_summary() -> Dict[str, Any]:
    """Retrieve summary counts and taxonomy across all external reference assets."""
    doc_cats = {}
    for d in OFFICIAL_DOCUMENTATION:
        cat = d["category"]
        doc_cats[cat] = doc_cats.get(cat, 0) + 1

    return {
        "total_official_documentation": len(OFFICIAL_DOCUMENTATION),
        "documentation_categories": doc_cats,
        "total_research_papers": len(RESEARCH_PAPERS),
        "total_meme_sources": len(MEME_DATA_SOURCES),
        "total_community_channels": len(COMMUNITY_RESOURCES),
        "grand_total_external_resources": (
            len(OFFICIAL_DOCUMENTATION)
            + len(RESEARCH_PAPERS)
            + len(MEME_DATA_SOURCES)
            + len(COMMUNITY_RESOURCES)
        ),
    }
