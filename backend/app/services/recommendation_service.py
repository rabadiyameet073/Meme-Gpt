"""MemeGPT — Recommendation Pipeline Orchestrator (FIXED).

The central pipeline called for every user search request.
Target latency: < 1.5 seconds total.

Pipeline stages:
  1. Cache check (~15ms on hit)
  2. Intent parsing via LLM (~300ms) in parallel with emotion detection (~100ms)
  3. Query embedding (~50ms)
  4. Vector search (~50ms) via Qdrant with payload filters
  5. Re-ranking (~10ms)
  6. Response construction with CDN media URLs & 1hr cache storage

Specification: 03_ML_PIPELINE_AND_TRAINING.md, 05_AI_Pipeline_Fix.md
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, List, Dict, Any

from app.core.cache import cache_get, cache_set, make_cache_key, query_cache
from app.services import embedding_service
from app.services import llm_service
from app.services import search_service
from app.services import rerank_service
from app.services import cdn_service
from app.services import giphy_service

logger = logging.getLogger("memegpt.recommendation")

_make_cache_key = make_cache_key

SIGNAL_WEIGHTS = {
    "view": 0.1,
    "click": 0.5,
    "copy": 1.0,
    "download": 2.0,
    "share": 3.0,
    "thumbs_up": 2.0,
    "thumbs_down": -1.0,
    "skip": -0.3,
}


async def recommend(
    user_text: str,
    format_pref: str = "gif",
    nsfw: bool = False,
    session_id: str | None = None,
    memes_from_db: list[dict] | None = None,
) -> dict:
    """Full recommendation pipeline. Returns a response dict.

    Args:
        user_text: The user's query/situation description
        format_pref: Preferred format (gif, video, image, any)
        nsfw: Whether to include NSFW memes
        session_id: User session ID for analytics
        memes_from_db: Pre-loaded memes from database (for fallback matching)
    """
    start = time.perf_counter()
    query_id = f"q_{uuid.uuid4().hex[:8]}"

    clean_text = (user_text or "")[:2000].strip()
    if not clean_text:
        clean_text = "funny reaction"
    emotion_text = clean_text[:512]

    # ── 1. Cache check (~15ms on hit) ─────────────────────────────────────
    cache_key = make_cache_key(clean_text, format_pref, nsfw)
    cached = cache_get(cache_key)
    if cached is not None:
        elapsed = int((time.perf_counter() - start) * 1000)
        logger.debug(f"Cache hit for {cache_key[:16]} ({elapsed}ms)")
        return {**cached, "latencyMs": elapsed, "cached": True}

    # ── 2 & 3. Concurrent Intent Parsing & Emotion Detection (~300ms) ─────
    loop = asyncio.get_event_loop()
    intent, emotion = await asyncio.gather(
        llm_service.parse_intent(clean_text),
        loop.run_in_executor(None, embedding_service.detect_emotion, emotion_text),
    )

    # ── 4. Build enriched query text ──────────────────────────────────────
    query_text = embedding_service.build_query_text(clean_text, intent, emotion)

    # ── 5. Generate query embedding (~50ms) ────────────────────────────────
    query_vector = await loop.run_in_executor(
        None, embedding_service.embed_text, query_text[:512]
    )

    # ── 6. Vector search (~50ms) ───────────────────────────────────────────
    candidates = search_service.vector_search(
        query_vector=query_vector,
        emotion=emotion.get("primary", ""),
        format_pref=format_pref,
        nsfw=nsfw,
        top_k=15,
    )

    # ── 6b. Enrich candidates with full meme data from DB ──────────────────
    if memes_from_db:
        db_lookup = {m["id"]: m for m in memes_from_db}
        for candidate in candidates:
            if not candidate.get("meme") or not candidate["meme"].get("name"):
                db_meme = db_lookup.get(candidate.get("id"))
                if db_meme:
                    candidate["meme"] = db_meme

    # ── 6c. Fallback: if vector search returns too few, use DB memes ──────
    if len(candidates) < 3 and memes_from_db:
        logger.debug("Vector search returned few results, augmenting with DB memes")
        candidates = _augment_from_db(candidates, memes_from_db, query_vector)

    # If still no candidates, pull directly from DB
    if not candidates:
        candidates = search_service._db_fallback_search(10)

    # ── 7. Re-rank (~10ms) ─────────────────────────────────────────────────
    final_results = rerank_service.rerank(candidates, intent, emotion, format_pref)

    # ── 8. Build response ──────────────────────────────────────────────────
    elapsed_ms = max(int((time.perf_counter() - start) * 1000), 1)

    if not final_results:
        return {
            "success": True,
            "queryId": query_id,
            "results": [],
            "primary": None,
            "topFive": [],
            "alternatives": [],
            "emotion": emotion,
            "detectedCategories": intent.get("categories", []),
            "detectedTags": intent.get("keywords", []),
            "gifs": [],
            "viralSuggestions": [],
            "latencyMs": elapsed_ms,
            "cached": False,
        }

    # Build structured response matching the API contract
    primary = _build_result(final_results[0], intent, emotion)
    top_five = [_build_result(r, intent, emotion) for r in final_results[:5]]
    alternatives = [_build_result(r, intent, emotion) for r in final_results[1:]]

    # Fetch live Giphy GIFs and Global Meme Stream
    primary_category = (intent.get("categories") or ["reaction"])[0]
    live_data = giphy_service.get_global_gifs_and_memes(
        query=clean_text,
        category=primary_category,
        limit=10,
    )

    # Collect GIF URLs
    local_gifs = [
        r["meme"].get("gifRef") or r["meme"].get("gif_ref") or r["meme"].get("gif_url")
        for r in final_results[:5]
        if r["meme"].get("gifRef") or r["meme"].get("gif_ref") or r["meme"].get("gif_url")
    ]
    gifs = list(dict.fromkeys(local_gifs + live_data.get("gif_urls", [])))

    response = {
        "success": True,
        "queryId": query_id,
        "results": top_five,
        "primary": primary,
        "topFive": top_five,
        "alternatives": alternatives,
        "emotion": emotion,
        "detectedCategories": intent.get("categories", []),
        "detectedTags": intent.get("keywords", []),
        "gifs": gifs,
        "viralSuggestions": live_data.get("memes", []),
        "latencyMs": elapsed_ms,
        "cached": False,
    }

    # ── Cache successful result ───────────────────────────────────────────
    cache_set(cache_key, response, ttl=3600)

    logger.info(f"Recommendation completed in {elapsed_ms}ms | results={len(top_five)}")
    return response


recommend_memes = recommend


def _build_result(item: dict, intent: dict, emotion: dict) -> dict:
    """Build a single meme result from a reranked item."""
    meme = item.get("meme", {})
    score = item.get("score", 0.5)

    formats = cdn_service.resolve_formats(meme)
    slug = meme.get("slug") or meme.get("name", "meme").lower().replace(" ", "-")

    keywords_str = ", ".join(intent.get("keywords", [])[:4]) or "the situation"
    category = meme.get("category", "general")
    base_explanation = meme.get("explanation", "")
    situation_summary = intent.get("situation", "").strip()

    if situation_summary:
        explanation = (
            f"{base_explanation} When dealing with '{situation_summary}', "
            f"this '{category.replace('_', ' ')}' meme captures the exact mood ({keywords_str})."
        )
    else:
        explanation = (
            f"{base_explanation} This meme fits because your situation aligns with "
            f"the '{category.replace('_', ' ')}' context ({keywords_str})."
        )

    return {
        "id": meme.get("id", item.get("id", "")),
        "name": meme.get("name", "Unknown Meme"),
        "slug": slug,
        "category": category,
        "categories": meme.get("categories", [category]),
        "emotions": meme.get("emotions", []),
        "dialogue": meme.get("dialogue", ""),
        "explanation": explanation,
        "confidence": min(max(round(score, 2), 0.15), 0.99),
        "keywords": meme.get("keywords", []),
        "image_url": formats.get("image"),
        "gif_url": formats.get("gif"),
        "mp4_url": formats.get("mp4"),
        "thumb_url": formats.get("thumb"),
        "imageRef": formats.get("image"),
        "videoRef": formats.get("mp4"),
        "gifRef": formats.get("gif"),
        "thumbUrl": formats.get("thumb"),
        "formats": formats,
        "shareUrl": cdn_service.get_share_url(slug),
        "viralScore": meme.get("viralScore", meme.get("viral_score", 0)),
        "viral_score": meme.get("viral_score", meme.get("viralScore", 0)),
        "usageCount": meme.get("usageCount", meme.get("usage_count", 0)),
        "usage_count": meme.get("usage_count", meme.get("usageCount", 0)),
        "upvotes": meme.get("upvotes", 0),
        "downvotes": meme.get("downvotes", 0),
        "emotionMatch": item.get("emotion_match", False),
    }


def _augment_from_db(
    candidates: list[dict],
    memes: list[dict],
    query_vector: list[float],
) -> list[dict]:
    """Augment sparse vector search results with database memes scored by cosine similarity."""
    existing_ids = {c.get("id") for c in candidates}

    for meme in memes:
        meme_id = meme.get("id", "")
        if meme_id in existing_ids:
            continue

        score = 0.3
        viral = meme.get("viralScore", 0) or meme.get("viral_score", 0) or 0
        usage = meme.get("usageCount", 0) or meme.get("usage_count", 0) or 0
        score += min(viral / 200, 0.15)
        score += min(usage / 500, 0.1)

        candidates.append({
            "id": meme_id,
            "score": score,
            "meme": meme,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:15]
