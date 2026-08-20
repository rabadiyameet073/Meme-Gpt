"""MemeGPT — Retrieval-Augmented Generation (RAG) Service.

Implements MemeGPT's specialized RAG pattern from 05_AI_System/RAG.md:
  1. Query Enrichment (LLM Intent Parsing + Emotion Detection)
  2. ANN Vector Retrieval (Qdrant Cloud 384-dim semantic search)
  3. Augmentation / Re-ranking (Composite scoring: Emotion + Popularity + Keywords)
  - No LLM generation step (direct meme asset retrieval with zero hallucinations)
"""

import logging
import time
from typing import Any

from app.services.cdn_service import build_meme_urls
from app.services.embedding_service import detect_emotion, get_text_embedding
from app.services.llm_service import parse_intent
from app.services.rerank_service import rerank
from app.services.search_service import vector_search
from app.services.text_composer import compose_query_text

logger = logging.getLogger("memegpt.rag")


async def rag_recommend(
    query: str,
    format_pref: str = "",
    limit: int = 5,
    top_k_candidates: int = 10,
) -> dict[str, Any]:
    """Execute MemeGPT's complete 3-stage RAG recommendation pipeline.

    Specification: 05_AI_System/RAG.md
    """
    start_time = time.time()

    # ── Stage 1: Query Enrichment ─────────────────────────────────────────────
    stage1_start = time.time()
    intent = await parse_intent(query)
    emotion = detect_emotion(query)

    rich_query = compose_query_text({
        "query": query,
        "situation": intent.get("situation", ""),
        "emotion": intent.get("emotion", emotion.get("primary", "")),
        "tone": intent.get("tone", ""),
        "keywords": intent.get("keywords", []),
    })
    query_vector = get_text_embedding(rich_query)
    stage1_ms = round((time.time() - stage1_start) * 1000, 2)

    # ── Stage 2: ANN Vector Retrieval ─────────────────────────────────────────
    stage2_start = time.time()
    candidates = vector_search(query_vector, top_k=top_k_candidates)
    stage2_ms = round((time.time() - stage2_start) * 1000, 2)

    # ── Stage 3: Augmentation & Re-ranking ────────────────────────────────────
    stage3_start = time.time()
    reranked = rerank(
        candidates=candidates,
        intent=intent,
        emotion=emotion,
        format_pref=format_pref,
    )
    top_results = reranked[:limit]
    stage3_ms = round((time.time() - stage3_start) * 1000, 2)

    # Enrich each meme with CDN URLs
    formatted_memes = []
    for item in top_results:
        meme_data = item.get("meme", item)
        urls = build_meme_urls(meme_data)
        formatted_memes.append({
            **item,
            "urls": urls,
        })

    total_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "query": query,
        "memes": formatted_memes,
        "rag_metadata": {
            "query_enrichment": {
                "intent": intent,
                "emotion": emotion,
                "composed_query": rich_query,
                "latency_ms": stage1_ms,
            },
            "retrieval": {
                "vector_dim": len(query_vector),
                "candidates_retrieved": len(candidates),
                "latency_ms": stage2_ms,
            },
            "augmentation": {
                "strategy": "composite_rerank_no_hallucination",
                "signals_applied": ["keyword_30%", "semantic_20%", "emotion_23%", "popularity_20%", "format_5%"],
                "results_count": len(formatted_memes),
                "latency_ms": stage3_ms,
            },
            "total_latency_ms": total_ms,
        },
    }
