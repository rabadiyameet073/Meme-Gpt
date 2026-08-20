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
import re
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


composite_score = rerank


def personalized_rerank(
    candidates: list[dict],
    category_weights: dict[str, float] | None = None,
) -> list[dict]:
    """Personalized re-ranking based on user session category interaction weights.

    Formula from 05_AI_System/Future_AI.md:
      final_score = base_score * (1 + 0.15 * category_weight)
    Where category_weight is clamped to [0.5, 2.0].
    """
    if not candidates:
        return []

    category_weights = category_weights or {}
    personalized = []

    for item in candidates:
        meme = item.get("meme", {})
        cat = str(meme.get("category", "")).lower().strip()
        base_score = float(item.get("score", 0.5))

        # Default weight is 1.0, clamped between 0.5 and 2.0
        raw_weight = category_weights.get(cat, 1.0)
        clamped_weight = max(0.5, min(2.0, float(raw_weight)))

        final_score = round(base_score * (1.0 + 0.15 * clamped_weight), 3)
        final_score = min(final_score, 0.99)

        personalized.append({
            **item,
            "score": final_score,
            "base_score": base_score,
            "personalized_weight": clamped_weight,
        })

    personalized.sort(key=lambda x: x["score"], reverse=True)
    return personalized


def calculate_viral_velocity(
    upvotes: int,
    comments: int,
    share_count: int,
    hours_since_post: float,
) -> dict:
    """Calculate viral velocity score for real-time priority indexing.

    Formula from 05_AI_System/Future_AI.md:
      velocity = (upvotes * 1.0 + comments * 2.0 + share_count * 3.0) / max(1, hours_since_post)
    Memes with velocity > 50/hr are flagged for priority indexing.
    """
    safe_hours = max(1.0, float(hours_since_post))
    velocity = (float(upvotes) * 1.0 + float(comments) * 2.0 + float(share_count) * 3.0) / safe_hours
    velocity = round(velocity, 2)
    return {
        "velocity": velocity,
        "is_priority_indexing": velocity > 50.0,
        "hours_since_post": safe_hours,
    }


def match_meme_template(
    caption: str,
    templates: list[dict] | None = None,
) -> list[dict]:
    """Match a user's caption to the best meme templates (Phase 4 Meme Generation).

    Specification: 05_AI_System/Future_AI.md
    """
    if not templates:
        templates = [
            {"id": "T001", "name": "Drake Hotline Bling", "best_for": "Approval/rejection", "keywords": ["approval", "reject", "preference", "better", "instead"]},
            {"id": "T002", "name": "Two Panel (This is Fine)", "best_for": "Denial/acceptance", "keywords": ["fire", "fine", "chaos", "crisis", "disaster", "calm"]},
            {"id": "T003", "name": "Distracted Boyfriend", "best_for": "Preference shift", "keywords": ["new", "old", "distracted", "switch", "temptation"]},
            {"id": "T004", "name": "Change My Mind", "best_for": "Unpopular opinion", "keywords": ["opinion", "truth", "debate", "mind", "fact"]},
            {"id": "T005", "name": "Woman Yelling at Cat", "best_for": "Confusion/misunderstanding", "keywords": ["yelling", "cat", "argument", "confused", "misunderstanding"]},
        ]

    caption_words = set(re.findall(r"\b\w+\b", caption.lower()))
    scored_templates = []

    for t in templates:
        t_keywords = set(t.get("keywords", []))
        overlap = len(caption_words.intersection(t_keywords))
        score = round(min(1.0, 0.3 + 0.2 * overlap), 2)
        scored_templates.append({
            **t,
            "match_score": score,
        })

    scored_templates.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_templates[:3]


def calculate_composite_score(
    cosine_similarity: float,
    meme_emotions: list[str],
    user_emotion_primary: str,
    user_emotion_secondary: str = "",
    popularity_score: float = 0.0,
    format_match: bool = False,
) -> float:
    """Composite relevance score formula from 05_AI_System/Scoring_Logic.md.

    Components:
    - Base: cosine similarity (0.0–1.0)
    - Emotion primary match: +15%
    - Emotion secondary match: +8%
    - Popularity boost: +0-10% (weighted)
    - Format preference match: +5%
    - Cap: 1.0 maximum
    """
    score = float(cosine_similarity)

    meme_emotions_lower = [str(e).lower() for e in meme_emotions]

    # Emotion matching (+15% primary, +8% secondary)
    if user_emotion_primary and str(user_emotion_primary).lower() in meme_emotions_lower:
        score += 0.15
    if user_emotion_secondary and str(user_emotion_secondary).lower() in meme_emotions_lower:
        score += 0.08

    # Popularity boost (0–10%)
    score += float(popularity_score) * 0.10

    # Format preference match (+5%)
    if format_match:
        score += 0.05

    return round(min(score, 1.0), 4)


def calculate_popularity_score(feedback: dict | str) -> float:
    """Aggregate engagement signals from the last 30 days normalized to 0.0-1.0.

    Specification: 05_AI_System/Scoring_Logic.md
    """
    if isinstance(feedback, str):
        # Passed meme_id, simulate or return default baseline
        return 0.5

    raw_score = (
        float(feedback.get("view_count", feedback.get("views", 0))) * 0.1
        + float(feedback.get("click_count", feedback.get("clicks", 0))) * 0.5
        + float(feedback.get("copy_count", feedback.get("copies", 0))) * 1.0
        + float(feedback.get("download_count", feedback.get("downloads", 0))) * 2.0
        + float(feedback.get("share_count", feedback.get("shares", 0))) * 3.0
        + float(feedback.get("thumbs_up", feedback.get("likes", 0))) * 2.0
        + float(feedback.get("thumbs_down", feedback.get("dislikes", 0))) * -1.0
    )

    normalized = min(1.0, max(0.0, raw_score / 10000.0))
    return round(normalized, 4)


def calculate_trending_score(feedback_24h: dict | str) -> float:
    """Short-term velocity engagement score in the LAST 24 HOURS.

    Specification: 05_AI_System/Scoring_Logic.md
    """
    if isinstance(feedback_24h, str):
        return 0.5

    raw = (
        float(feedback_24h.get("view_count", feedback_24h.get("views", 0))) * 0.1
        + float(feedback_24h.get("download_count", feedback_24h.get("downloads", 0))) * 2.0
        + float(feedback_24h.get("share_count", feedback_24h.get("shares", 0))) * 3.0
        + float(feedback_24h.get("thumbs_up", feedback_24h.get("likes", 0))) * 2.0
    )

    normalized = min(1.0, max(0.0, raw / 1000.0))
    return round(normalized, 4)


def recalculate_all_popularity_scores(memes: list[dict]) -> list[dict]:
    """Recalculate popularity for a collection of memes (used in weekly cron)."""
    updated = []
    for m in memes:
        feedback = m.get("feedback", {})
        pop_score = calculate_popularity_score(feedback)
        updated.append({
            **m,
            "popularity_score": pop_score,
            "popularityScore": pop_score,
        })
    return updated


def format_score_display(score: float) -> dict:
    """Format relevance score for UI display badge matching Scoring_Logic.md."""
    pct = round(score * 100)
    if score >= 0.90:
        return {
            "display": f"🎯 {pct}% match",
            "color": "#22C55E",
            "is_visible": True,
            "tier": "high",
        }
    elif score >= 0.70:
        return {
            "display": f"🎯 {pct}% match",
            "color": "#F59E0B",
            "is_visible": True,
            "tier": "medium",
        }
    elif score >= 0.50:
        return {
            "display": f"🎯 {pct}% match",
            "color": "#FB923C",
            "is_visible": True,
            "tier": "fair",
        }
    else:
        return {
            "display": "",
            "color": "transparent",
            "is_visible": False,
            "tier": "low",
        }

