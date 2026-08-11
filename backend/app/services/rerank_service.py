"""MemeGPT — Re-Ranking Service.

Takes candidate memes from vector search and re-ranks them using the
composite scoring formula from Low_Level_Architecture.md:

  Keyword Match:     30%
  Semantic Score:    20%  (already in vector similarity)
  Emotion Match:     15% primary + 8% secondary
  Popularity:        20%
  Recency:           10%
  Format Preference:  5%

Also applies deduplication and ensures diversity in the top results.

Specification: 03_ML_PIPELINE_AND_TRAINING.md, Low_Level_Architecture.md
"""

import logging
from typing import Optional

logger = logging.getLogger("memegpt.rerank")


def rerank(
    candidates: list[dict],
    intent: dict,
    emotion: dict,
    format_pref: str = "",
) -> list[dict]:
    """Re-rank search candidates using the composite scoring formula.

    Args:
        candidates: List from search_service.search() with keys: id, score, meme
        intent: Parsed intent from LLM: keywords, categories, situation, tone
        emotion: Detected emotion: primary, confidence, all
        format_pref: User's format preference (gif, video, image)

    Returns:
        Re-ranked list of candidates (top 5), deduplicated.
    """
    if not candidates:
        return []

    primary_emotion = emotion.get("primary", "humor")
    intent_keywords = [k.lower() for k in intent.get("keywords", [])]
    intent_categories = [c.lower() for c in intent.get("categories", [])]

    scored = []
    for candidate in candidates:
        meme = candidate.get("meme", {})
        vector_score = candidate.get("score", 0.0)

        # ── A: Keyword match score (0.0 - 1.0) ──────────────────────────
        keyword_score = 0.0
        meme_keywords = [k.lower() for k in meme.get("keywords", [])]
        meme_name = meme.get("name", "").lower()
        meme_dialogue = meme.get("dialogue", "").lower()
        meme_category = meme.get("category", "").lower()

        # Category match
        if meme_category in intent_categories:
            keyword_score += 0.4

        # Keyword overlap
        for kw in intent_keywords:
            if any(kw in mk for mk in meme_keywords):
                keyword_score += 0.15
            if kw in meme_name or kw in meme_dialogue:
                keyword_score += 0.1

        keyword_score = min(keyword_score, 1.0)

        # ── B: Semantic score (from vector search) ───────────────────────
        semantic_score = min(vector_score, 1.0)

        # ── C: Emotion match ─────────────────────────────────────────────
        emotion_primary_match = False
        emotion_secondary_match = False

        meme_emotions = " ".join([
            meme.get("category", ""),
            " ".join(meme.get("keywords", [])),
            meme.get("explanation", ""),
        ]).lower()

        if primary_emotion in meme_emotions:
            emotion_primary_match = True

        # Check secondary emotions
        for emo, score in emotion.get("all", {}).items():
            if emo != primary_emotion and score > 0.1 and emo in meme_emotions:
                emotion_secondary_match = True
                break

        # ── D: Popularity score (0.0 - 1.0) ─────────────────────────────
        viral_raw = meme.get("viralScore", meme.get("viral_score", 0)) or 0
        usage_raw = meme.get("usageCount", meme.get("usage_count", 0)) or 0
        up_raw = meme.get("upvotes", 0) or 0
        popularity_score = min(
            (viral_raw / 100.0) * 0.5 +
            (usage_raw / 500.0) * 0.3 +
            (up_raw / 200.0) * 0.2,
            1.0,
        )

        # ── E: Recency (0.0 - 1.0, assume recent for now) ───────────────
        recency_score = 0.7  # Default — no timestamp logic yet

        # ── F: Format preference match ───────────────────────────────────
        format_match = False
        if format_pref:
            fp = format_pref.lower()
            if fp == "gif" and meme.get("gifRef", meme.get("gif_ref")):
                format_match = True
            elif fp in ("video", "mp4") and meme.get("videoRef", meme.get("video_ref")):
                format_match = True
            elif fp in ("image", "png", "webp") and meme.get("imageRef", meme.get("image_ref")):
                format_match = True

        # ── Composite Score (from Low_Level_Architecture.md) ─────────────
        composite = (
            keyword_score * 0.30 +
            semantic_score * 0.20 +
            popularity_score * 0.20 +
            recency_score * 0.10
        )

        if emotion_primary_match:
            composite += 0.15
        if emotion_secondary_match:
            composite += 0.08
        if format_match:
            composite += 0.05

        composite = min(max(composite, 0.05), 0.99)

        scored.append({
            "meme": meme,
            "id": candidate.get("id", meme.get("id", "")),
            "score": round(composite, 3),
            "vector_score": round(vector_score, 3),
            "keyword_score": round(keyword_score, 3),
            "emotion_match": emotion_primary_match,
        })

    # Sort by composite score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Deduplicate by meme name
    deduped = _deduplicate(scored)

    # Return top 5
    return deduped[:5]


def _deduplicate(results: list[dict]) -> list[dict]:
    """Remove memes with duplicate names (case-insensitive).

    As specified in Business_Logic.md.
    """
    seen_names = set()
    unique = []
    for item in results:
        name = item.get("meme", {}).get("name", "").lower().strip()
        if name and name not in seen_names:
            seen_names.add(name)
            unique.append(item)
        elif not name:
            unique.append(item)
    return unique
