"""
Core Recommendation Engine — called for every user search request.
Target latency: < 1.5 seconds total.

Pipeline:
  Cache check → Intent parsing (LLM ~300ms) → Emotion detection (~100ms)
  → Query embedding (~50ms) → Vector search (~50ms) → Re-ranking (~10ms)
  → Return top-5 with CDN URLs
"""
import hashlib
import json
import logging
import time
import uuid

from app.services.embedding import embedding_service
from app.services.llm import llm_service
from app.services.search_service import search_service
from app.services.rerank_service import rerank_service
from app.services.cdn_service import cdn_service
from app.core.cache import cache_service
from app.models.search import SearchResponse, ParsedIntent
from app.models.meme import MemeResult, MemeFormats

logger = logging.getLogger("services.recommendation")


def _make_cache_key(user_text: str, format_pref: str, nsfw: bool) -> str:
    raw = f"{user_text.lower().strip()}:{format_pref}:{nsfw}"
    return f"search:{hashlib.md5(raw.encode()).hexdigest()}"


def _build_meme_result(item: dict, query_id: str) -> MemeResult:
    """Convert a reranked item into a MemeResult response object."""
    payload = item.get("meme", item)
    slug = payload.get("slug") or payload.get("name", "meme").lower().replace(" ", "-")
    formats_dict = cdn_service.resolve_formats(payload)

    return MemeResult(
        id=payload.get("id", slug),
        name=payload.get("name", "Unknown Meme"),
        slug=slug,
        relevance_score=round(item.get("score", 0.5), 3),
        emotion_match=payload.get("emotions", []),
        preview_url=formats_dict.get("webp") or formats_dict.get("image"),
        formats=MemeFormats(**formats_dict),
        share_url=cdn_service.get_share_url(slug, query_id),
        meme_type=payload.get("meme_type", "reaction"),
        categories=payload.get("categories", [payload.get("category", "general")]),
        emotions=payload.get("emotions", []),
        nsfw=payload.get("nsfw", False),
        popularity_score=payload.get("popularity_score", 0.0),
    )


class RecommendationService:
    async def recommend(
        self,
        user_text: str,
        format_pref: str = "gif",
        nsfw: bool = False,
        session_id: str | None = None,
    ) -> SearchResponse:
        """Full recommendation pipeline. Returns SearchResponse."""
        start = time.time()
        query_id = f"q_{uuid.uuid4().hex[:8]}"

        # ── Cache check (~15ms on hit) ────────────────────────────────────────
        cache_key = _make_cache_key(user_text, format_pref, nsfw)
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key[:16]}")
            return SearchResponse(**cached, cached=True, response_time_ms=5)

        # ── A: Parse intent (Groq LLM ~300ms) ────────────────────────────────
        intent = await llm_service.parse_intent(user_text)

        # ── B: Detect emotion (local model ~100ms) ────────────────────────────
        emotion = embedding_service.detect_emotion(user_text)

        # ── C: Build rich query text ──────────────────────────────────────────
        query_text = embedding_service.build_query_text(user_text, intent, emotion)

        # ── D: Generate query embedding (~50ms) ───────────────────────────────
        query_vector = embedding_service.embed_text(query_text)

        # ── E: Vector search (~50ms) ──────────────────────────────────────────
        candidates = search_service.search(
            query_vector=query_vector,
            emotion=emotion["primary"],
            format_pref=format_pref,
            nsfw=nsfw,
            top_k=10,
        )

        # ── F: Re-rank (~10ms) ────────────────────────────────────────────────
        final_results = rerank_service.rerank(candidates, intent, emotion, format_pref)

        # ── G: Build response ─────────────────────────────────────────────────
        meme_results = [_build_meme_result(item, query_id) for item in final_results]
        elapsed_ms = int((time.time() - start) * 1000)

        parsed = ParsedIntent(
            emotion=emotion.get("primary", "neutral"),
            situation=intent.get("situation", ""),
            tone=intent.get("tone", "humorous"),
            keywords=intent.get("keywords", []),
            meme_format=intent.get("meme_format", "reaction"),
        )

        response = SearchResponse(
            success=True,
            query_id=query_id,
            results=meme_results,
            intent_parsed=parsed,
            response_time_ms=elapsed_ms,
            cached=False,
        )

        # ── Cache result for 1 hour ───────────────────────────────────────────
        if meme_results:
            cache_service.set(cache_key, response.model_dump(), ttl=3600)

        logger.info(f"Recommendation completed in {elapsed_ms}ms | results={len(meme_results)}")
        return response


recommendation_service = RecommendationService()
