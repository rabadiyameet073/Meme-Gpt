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
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("memegpt.rerank")


# ──────────────────────────────────────────────────────────────────────────────
# Composite scoring weights
# ──────────────────────────────────────────────────────────────────────────────
#
# The previous formula added every bonus on top of the cosine similarity and
# then clipped at 0.99. Because MiniLM cosine values on short meme texts are
# routinely > 0.7, most candidates saturated at the clip and the final order was
# decided by dictionary iteration order — which is why the "best" meme was
# almost never first (AUDIT-REPORT AI-2).
#
# The weights below are a convex combination: they sum to exactly 1.0, so the
# result is a true normalised relevance in [0, 1] that preserves ordering
# between a strong and a weak match and can never create a tie by saturation.
COMPOSITE_WEIGHTS = {
    "semantic": 0.34,
    "lexical": 0.30,
    "emotion_primary": 0.14,
    "emotion_secondary": 0.06,
    "popularity": 0.08,
    "recency": 0.03,
    "format": 0.05,
}
assert abs(sum(COMPOSITE_WEIGHTS.values()) - 1.0) < 1e-9

# Maps the normalised relevance onto the confidence scale the UI already uses
# (0.15 floor / 0.99 ceiling). The transform is affine and strictly monotonic,
# so ranking order is untouched.
DISPLAY_SCORE_FLOOR = 0.15
DISPLAY_SCORE_SPAN = 0.84

# Emotion classifier labels (GoEmotions style) → the richer vocabulary used in
# memes.json (humor, smug, panic, pride, ...). Without this bridge an "angry"
# query and a "sad" query both matched nothing in the meme record and every
# scenario collapsed onto the same generic results.
EMOTION_FAMILIES = {
    "joy": {
        "joy", "happy", "happiness", "excited", "excitement", "celebrate",
        "celebratory", "celebration", "win", "winner", "victory", "success",
        "pride", "proud", "confident", "smug", "grateful", "love", "loved",
        "wholesome", "inspired", "hopeful", "relieved", "satisfied", "cheerful",
    },
    "sadness": {
        "sadness", "sad", "cry", "crying", "upset", "disappointed",
        "disappointment", "lonely", "alone", "resigned", "melancholy",
        "grief", "hurt", "heartbroken", "regret", "lost", "gloomy",
    },
    "anger": {
        "anger", "angry", "frustrated", "frustration", "rage", "annoyed",
        "irritated", "furious", "mad", "outraged",
    },
    "surprise": {
        "surprise", "surprised", "shocked", "confused", "confusion",
        "disbelief", "amazed", "unexpected", "stunned", "shook",
    },
    "fear": {
        "fear", "afraid", "scared", "anxious", "anxiety", "panic", "dread",
        "nervous", "worried", "stress", "stressed", "overwhelmed", "uneasy",
    },
    "disgust": {
        "disgust", "disgusted", "gross", "nasty", "cringe", "cringey",
    },
    "neutral": {
        "humor", "funny", "relatable", "calm", "peaceful", "serious",
        "indifferent", "chill", "sarcastic", "ironic", "irony", "deadpan",
    },
}

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "am",
    "of", "to", "in", "on", "for", "and", "or", "but", "so", "that",
    "this", "it", "its", "at", "with", "as", "by", "from", "when", "how",
    "what", "just", "really", "i", "im", "my", "me", "we", "you", "your",
}


def _tokens(value) -> set:
    """Lowercase content tokens from a string or list of strings."""
    if isinstance(value, (list, tuple, set)):
        text = " ".join(str(v) for v in value if v)
    else:
        text = str(value or "")
    return {
        t for t in re.findall(r"[a-z0-9']+", text.lower())
        if len(t) > 1 and t not in _STOPWORDS
    }


def _family(label: str) -> set:
    """Return the emotion family a label belongs to."""
    key = str(label or "").lower().strip()
    if not key:
        return set()
    if key in EMOTION_FAMILIES:
        return EMOTION_FAMILIES[key]
    for members in EMOTION_FAMILIES.values():
        if key in members:
            return members
    return {key}


def _field_overlap(query_tokens: set, meme: dict) -> float:
    """Best-field token overlap, with a bonus when several fields agree.

    Returns a value in [0, 1] that grows monotonically with how specifically
    the meme covers the query wording.
    """
    if not query_tokens:
        return 0.0

    fields = [
        (_tokens(meme.get("name")), 1.00),
        (_tokens(meme.get("dialogue")), 0.90),
        (_tokens(meme.get("keywords")), 0.85),
        (_tokens(meme.get("categories") or meme.get("category")), 0.70),
        (_tokens(meme.get("emotions")), 0.70),
        (_tokens(meme.get("explanation")), 0.55),
        (_tokens(meme.get("alt_text")), 0.45),
    ]

    best = 0.0
    agreeing = 0
    for tokens, weight in fields:
        if not tokens:
            continue
        overlap = len(query_tokens & tokens) / len(query_tokens)
        if overlap > 0:
            agreeing += 1
        best = max(best, overlap * weight)

    if agreeing > 1:
        best = min(1.0, best + 0.05 * (agreeing - 1))
    return round(best, 4)


def _popularity_component(meme: dict) -> float:
    """Engagement signal normalised to [0, 1]."""
    viral = float(meme.get("viralScore", meme.get("viral_score", 0)) or 0)
    usage = float(meme.get("usageCount", meme.get("usage_count", 0)) or 0)
    up = float(meme.get("upvotes", 0) or 0)
    stored = float(meme.get("popularity_score", 0) or 0)

    computed = min((viral / 100.0) * 0.5 + (usage / 500.0) * 0.3 + (up / 200.0) * 0.2, 1.0)
    return max(computed, min(stored, 1.0)) if stored <= 1.0 else computed


def _recency_component(meme: dict) -> float:
    """Exponential decay over a 365-day half-window.

    The old implementation returned a hard-coded 0.7 for every candidate, which
    was a constant: it diluted the ranking without differentiating anything.
    """
    raw = meme.get("created_at") or meme.get("createdAt")
    if not raw:
        return 0.5

    try:
        if isinstance(raw, str):
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        else:
            parsed = raw
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        age_days = max((datetime.now(timezone.utc) - parsed).days, 0)
        return round(max(0.0, 1.0 - age_days / 365.0), 4)
    except Exception:
        return 0.5


def _format_component(meme: dict, format_pref: str) -> bool:
    """True when the meme carries the requested media format."""
    if not format_pref:
        return False

    pref = format_pref.lower()
    has_gif = bool(meme.get("gif_url") or meme.get("gifRef") or meme.get("gif_ref"))
    has_video = bool(meme.get("mp4_url") or meme.get("videoRef") or meme.get("video_ref"))
    has_image = bool(meme.get("image_url") or meme.get("imageRef") or meme.get("image_ref"))

    if pref == "gif":
        return has_gif
    if pref in ("video", "mp4"):
        return has_video
    if pref in ("image", "png", "jpg", "webp"):
        return has_image
    return False


def to_display_score(relevance: float) -> float:
    """Map normalised relevance onto the confidence scale shown in the UI."""
    raw = DISPLAY_SCORE_FLOOR + DISPLAY_SCORE_SPAN * min(max(relevance, 0.0), 1.0)
    return round(min(raw, 0.99), 3)



def rerank(
    candidates: list[dict],
    intent: dict,
    emotion: dict,
    format_pref: str = "",
    limit: int = 5,
) -> list[dict]:
    """Re-rank search candidates using the composite scoring formula.

    Args:
        candidates: List from search_service.search() with keys: id, score, meme
        intent: Parsed intent from LLM: keywords, categories, situation, tone
        emotion: Detected emotion: primary, confidence, all
        format_pref: User's format preference (gif, video, image)
        limit: Number of candidates to return (default 5)

    Returns:
        Re-ranked list of top candidates, deduplicated. Each item carries both
        ``score`` (display confidence, 0.15–0.99) and ``relevance`` (the raw
        normalised composite used for ordering).
    """
    if not candidates:
        return []

    # ── Build the user's emotion profile ────────────────────────────────
    primary_emotion = str(
        emotion.get("primary")
        or intent.get("emotion_hint")
        or intent.get("emotion")
        or "neutral"
    ).lower()

    # Every label that describes the query with non-trivial weight, plus the
    # LLM's tone/intent hints, contributes to the secondary emotion signal.
    secondary_labels = {
        str(label).lower()
        for label, score in (emotion.get("all") or {}).items()
        if score is not None and float(score) >= 0.15 and str(label).lower() != primary_emotion
    }
    for hint in (intent.get("emotion_hint"), intent.get("tone"), intent.get("emotion")):
        if hint:
            hint_label = str(hint).lower()
            if hint_label not in (primary_emotion, "neutral"):
                secondary_labels.add(hint_label)

    secondary_family: set = set()
    for label in secondary_labels:
        secondary_family |= _family(label)
    secondary_family -= _family(primary_emotion)

    # ── Query tokens: the intent keywords plus the situation summary ─────
    query_tokens = _tokens(intent.get("keywords"))
    query_tokens |= _tokens(intent.get("situation"))

    categories = [str(c).lower() for c in (intent.get("categories") or [])]
    secondary_pick = sorted(secondary_labels)[0] if secondary_labels else ""

    scored = []
    for candidate in candidates:
        meme = candidate.get("meme", {}) or {}
        vector_score = max(0.0, min(float(candidate.get("score", 0.0) or 0.0), 1.0))

        # ── A: Lexical match (query-specific) ────────────────────────────
        lexical_score = _field_overlap(query_tokens, meme)
        if categories:
            owned = {str(c).lower() for c in (meme.get("categories") or [meme.get("category")])}
            if owned & set(categories):
                lexical_score = min(1.0, lexical_score + 0.1)

        # ── B: Emotion affinity ─────────────────────────────────
        # Memes carry a rich tag vocabulary (humor, smug, panic, pride, ...)
        # while the classifier emits GoEmotions labels. Compare families so an
        # "angry" query and a "sad" query resolve to different memes.
        meme_emotion_terms = {str(e).lower() for e in (meme.get("emotions") or [])}
        meme_emotion_terms |= _tokens(meme.get("keywords"))
        meme_emotion_terms |= _tokens(meme.get("categories") or meme.get("category"))
        meme_emotion_terms |= _tokens(meme.get("explanation"))
        meme_emotion_terms |= _tokens(meme.get("name"))

        primary_match = bool(_family(primary_emotion) & meme_emotion_terms)
        secondary_match = bool(secondary_family & meme_emotion_terms)

        # ── C–F: Composite ──────────────────────────────────────────────
        composite = calculate_composite_score(
            cosine_similarity=vector_score,
            meme_emotions=list(meme_emotion_terms),
            user_emotion_primary=primary_emotion,
            user_emotion_secondary=secondary_pick,
            popularity_score=_popularity_component(meme),
            format_match=_format_component(meme, format_pref),
            lexical_score=lexical_score,
            recency_score=_recency_component(meme),
        )

        scored.append({
            "meme": meme,
            "id": candidate.get("id", meme.get("id", "")),
            "score": to_display_score(composite),
            "relevance": round(composite, 4),
            "vector_score": round(vector_score, 3),
            "keyword_score": round(lexical_score, 3),
            "emotion_match": primary_match,
            "emotion_secondary_match": secondary_match,
        })

    # Sort by relevance descending. The explicit secondary key keeps ordering
    # deterministic when two memes genuinely tie.
    scored.sort(
        key=lambda x: (x["relevance"], x["vector_score"], x["keyword_score"]),
        reverse=True,
    )

    deduped = _deduplicate(scored)

    return deduped[:max(1, limit)]


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
    lexical_score: float = 0.0,
    recency_score: float = 0.5,
) -> float:
    """Composite relevance score — a convex blend of the six signals.

    Specification: 05_AI_System/Scoring_Logic.md (weights rebalanced).

    Every component is normalised to [0, 1] and multiplied by a weight from
    :data:`COMPOSITE_WEIGHTS`, which sums to exactly 1.0. Consequently the
    result is always in [0, 1], is strictly monotonic in each signal, and can
    never saturate into a tie — the failure mode that previously made the
    "best" meme rank below generic ones.

    Weights:
    - semantic (cosine similarity):  0.34
    - lexical (query/token overlap): 0.30
    - emotion primary match:         0.14
    - emotion secondary match:       0.06
    - popularity:                    0.08
    - recency:                       0.03
    - format preference match:       0.05
    """
    semantic = min(max(float(cosine_similarity or 0.0), 0.0), 1.0)
    lexical = min(max(float(lexical_score or 0.0), 0.0), 1.0)
    popularity = min(max(float(popularity_score or 0.0), 0.0), 1.0)
    recency = min(max(float(recency_score or 0.0), 0.0), 1.0)

    # Emotion matching is resolved against families so that the classifier's
    # GoEmotions labels line up with the meme tag vocabulary (joy -> happy,
    # celebratory, pride, ...).
    meme_terms = {str(e).lower().strip() for e in meme_emotions if str(e).strip()}
    primary_hit = bool(_family(user_emotion_primary) & meme_terms)
    secondary_hit = bool(_family(user_emotion_secondary) & meme_terms)

    score = (
        semantic * COMPOSITE_WEIGHTS["semantic"]
        + lexical * COMPOSITE_WEIGHTS["lexical"]
        + (COMPOSITE_WEIGHTS["emotion_primary"] if primary_hit else 0.0)
        + (COMPOSITE_WEIGHTS["emotion_secondary"] if secondary_hit else 0.0)
        + popularity * COMPOSITE_WEIGHTS["popularity"]
        + recency * COMPOSITE_WEIGHTS["recency"]
        + (COMPOSITE_WEIGHTS["format"] if format_match else 0.0)
    )

    return round(min(max(score, 0.0), 1.0), 4)


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

