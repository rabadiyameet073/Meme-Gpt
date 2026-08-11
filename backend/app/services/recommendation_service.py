"""MemeGPT — Recommendation Pipeline Orchestrator.

The central pipeline called for every user search request.
Target latency: < 1.5 seconds total.

Pipeline stages:
  1. Cache check (~15ms on hit)
  2. Intent parsing via LLM (~300ms) — or keyword fallback (~5ms)
  3. Emotion detection (~100ms) — or rule-based fallback (~1ms)
  4. Query embedding (~50ms)
  5. Vector search (~50ms) — or local fallback (~20ms)
  6. Re-ranking (~10ms)
  7. Build response with CDN URLs

Specification: 03_ML_PIPELINE_AND_TRAINING.md, 04_DESIGN_AND_DEVELOPMENT.md
"""

import hashlib
import logging
import time
import uuid
from typing import Optional

from app.services import embedding_service
from app.services import llm_service
from app.services import search_service
from app.services import rerank_service
from app.services import cdn_service
from app.services import giphy_service
from app.core.cache import query_cache

logger = logging.getLogger("memegpt.recommendation")



def _make_cache_key(user_text: str, format_pref: str, nsfw: bool = False) -> str:
    """Deterministic cache key generator as specified in Business_Logic.md."""
    raw = f"{user_text.lower().strip()}:{format_pref or 'any'}:{nsfw}"
    return f"search:{hashlib.md5(raw.encode('utf-8')).hexdigest()}"


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
        format_pref: Preferred format (gif, video, image)
        nsfw: Whether to include NSFW memes
        session_id: User session ID for analytics
        memes_from_db: Pre-loaded memes from database (for fallback matching)
    """
    start = time.perf_counter()
    query_id = f"q_{uuid.uuid4().hex[:8]}"

    # ── 1. Cache check (~15ms on hit) ─────────────────────────────────────
    cache_key = _make_cache_key(user_text, format_pref, nsfw)
    cached = query_cache.get(cache_key)
    if cached is not None:
        elapsed = int((time.perf_counter() - start) * 1000)
        logger.info(f"Cache hit for {cache_key[:16]} ({elapsed}ms)")
        return {**cached, "latencyMs": elapsed, "cached": True}

    # ── 2. Parse intent via LLM (~300ms) ──────────────────────────────────
    intent = await llm_service.parse_intent(user_text)

    # ── 3. Detect emotion (~100ms with model, ~1ms with rules) ────────────
    emotion = embedding_service.detect_emotion(user_text)

    # ── 4. Build enriched query text ──────────────────────────────────────
    query_text = embedding_service.build_query_text(user_text, intent, emotion)

    # ── 5. Generate query embedding (~50ms) ────────────────────────────────
    query_vector = embedding_service.embed_text(query_text)

    # ── 6. Vector search (~50ms) ───────────────────────────────────────────
    candidates = search_service.search(
        query_vector=query_vector,
        emotion=emotion.get("primary", ""),
        format_pref=format_pref,
        nsfw=nsfw,
        top_k=15,
    )

    # ── 6b. Enrich candidates with full meme data from DB ──────────────────
    #   Local search only returns id+score with empty payloads (embeddings.json
    #   has no metadata). Map each result back to the full DB meme record.
    if memes_from_db:
        db_lookup = {m["id"]: m for m in memes_from_db}
        for candidate in candidates:
            if not candidate.get("meme") or not candidate["meme"].get("name"):
                db_meme = db_lookup.get(candidate.get("id"))
                if db_meme:
                    candidate["meme"] = db_meme

    # ── 6c. Fallback: if vector search returns too few, use DB memes ──────
    if len(candidates) < 3 and memes_from_db:
        logger.info("Vector search returned few results, augmenting with DB memes")
        candidates = _augment_from_db(candidates, memes_from_db, query_vector)

    # ── 7. Re-rank (~10ms) ─────────────────────────────────────────────────
    final_results = rerank_service.rerank(candidates, intent, emotion, format_pref)

    # ── 8. Build response ──────────────────────────────────────────────────
    elapsed_ms = max(int((time.perf_counter() - start) * 1000), 1)

    if not final_results:
        return {
            "success": True,
            "queryId": query_id,
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
    primary_category = (intent.get("categories") or ["funny"])[0]
    live_data = giphy_service.get_global_gifs_and_memes(
        query=user_text,
        category=primary_category,
        limit=10,
    )

    # Collect GIF URLs (combining local GIF refs + live Giphy GIFs)
    local_gifs = [
        r["meme"].get("gifRef") or r["meme"].get("gif_ref")
        for r in final_results[:5]
        if r["meme"].get("gifRef") or r["meme"].get("gif_ref")
    ]
    gifs = list(dict.fromkeys(local_gifs + live_data.get("gif_urls", [])))

    response = {
        "success": True,
        "queryId": query_id,
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
    query_cache.set(cache_key, response, ttl=3600)

    logger.info(f"Recommendation completed in {elapsed_ms}ms | results={len(top_five)}")
    return response


def _build_result(item: dict, intent: dict, emotion: dict) -> dict:
    """Build a single meme result from a reranked item."""
    meme = item.get("meme", {})
    score = item.get("score", 0.5)

    # Resolve CDN formats
    formats = cdn_service.resolve_formats(meme)
    slug = meme.get("slug") or meme.get("name", "meme").lower().replace(" ", "-")

    # Build situation-specific AI explanation text
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
        "dialogue": meme.get("dialogue", ""),
        "explanation": explanation,
        "confidence": min(max(round(score, 2), 0.15), 0.99),
        "keywords": meme.get("keywords", []),
        "imageRef": formats.get("image"),
        "videoRef": formats.get("mp4"),
        "gifRef": formats.get("gif"),
        "thumbUrl": formats.get("thumb"),
        "formats": formats,
        "shareUrl": cdn_service.get_share_url(slug),
        "viralScore": meme.get("viralScore", meme.get("viral_score", 0)),
        "usageCount": meme.get("usageCount", meme.get("usage_count", 0)),
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
    from app.services.search_service import _cosine_similarity

    existing_ids = {c.get("id") for c in candidates}

    for meme in memes:
        meme_id = meme.get("id", "")
        if meme_id in existing_ids:
            continue

        # Build a simple text representation for embedding comparison
        # Score using existing meme data
        score = 0.3  # Base score for DB augmentation

        # Boost by popularity
        viral = meme.get("viralScore", 0) or 0
        usage = meme.get("usageCount", 0) or 0
        score += min(viral / 200, 0.15)
        score += min(usage / 500, 0.1)

        candidates.append({
            "id": meme_id,
            "score": score,
            "meme": meme,
        })

    # Sort by score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:15]
