import time

from app.rule_engine import run_rule_engine, detect_emotion
from app.semantic_search import semantic_scores


def _to_match(meme: dict, confidence: float) -> dict:
    return {
        "id": meme["id"],
        "name": meme["name"],
        "category": meme["category"],
        "dialogue": meme["dialogue"],
        "explanation": meme["explanation"],
        "confidence": min(max(round(confidence, 2), 0.15), 0.99),
        "videoRef": meme.get("videoRef"),
        "gifRef": meme.get("gifRef"),
        "viralScore": meme.get("viralScore", 0),
        "usageCount": meme.get("usageCount", 0),
        "upvotes": meme.get("upvotes", 0),
        "downvotes": meme.get("downvotes", 0),
    }


def calculate_composite_score(
    keyword_score: float,
    semantic_score: float,
    emotion_match: bool,
    emotion_secondary: bool,
    popularity_score: float,
    format_match: bool,
    recency_days: int = 0,
) -> float:
    """
    Weighted scoring formula from Low_Level_Architecture.md.
    """
    score = (
        min(keyword_score, 1.0) * 0.30 +
        min(semantic_score, 1.0) * 0.20 +
        min(popularity_score, 1.0) * 0.20 +
        max(0, (30 - recency_days) / 30) * 0.10
    )

    if emotion_match:
        score += 0.15
    if emotion_secondary:
        score += 0.08
    if format_match:
        score += 0.05

    return min(max(score, 0.0), 1.0)


def deduplicate(results: list) -> list:
    """Remove memes that are too similar to each other as specified in Business_Logic.md."""
    seen_names = set()
    deduplicated = []
    for item in results:
        name_normalized = item["meme"]["name"].lower().strip()
        if name_normalized not in seen_names:
            seen_names.add(name_normalized)
            deduplicated.append(item)
    return deduplicated


def match_memes(query: str, memes: list[dict], format_preference: str | None = None) -> dict:
    start = time.perf_counter()
    rules = run_rule_engine(query)
    detected_emo = detect_emotion(query)
    primary_emo = detected_emo.get("primary", "")
    sem = semantic_scores(query, memes)

    scored = []
    q_lower = query.lower()

    for meme in memes:
        # Keyword score (max 1.0)
        kw_score = 0.0
        if meme.get("category") in rules.categories:
            kw_score += rules.scores.get(meme["category"], 0.0) * 0.5
        for kw in meme.get("keywords", []):
            kw_l = kw.lower()
            if kw_l in q_lower:
                kw_score += 0.3
            for tag in rules.tags:
                if tag.replace("_", " ") in kw_l:
                    kw_score += 0.2

        sem_score = sem.get(meme["id"], 0.0)

        # Popularity score (0.0 - 1.0)
        viral_raw = meme.get("viralScore", 0) or 0
        usage_raw = meme.get("usageCount", 0) or 0
        up_raw = meme.get("upvotes", 0) or 0
        pop_score = min((viral_raw / 100.0) * 0.5 + (usage_raw / 500.0) * 0.3 + (up_raw / 200.0) * 0.2, 1.0)

        # Emotion match
        categories = meme.get("category", "")
        keywords = " ".join(meme.get("keywords", [])).lower()
        explanation = meme.get("explanation", "").lower()

        emo_match = (
            primary_emo in categories or primary_emo in keywords or primary_emo in explanation
        )
        emo_sec_match = False
        for sec_tag in rules.tags:
            if sec_tag in keywords or sec_tag in explanation:
                emo_sec_match = True
                break

        # Format match (+0.05)
        fmt_match = False
        if format_preference:
            fmt_pref = format_preference.lower()
            if fmt_pref == "gif" and meme.get("gifRef"):
                fmt_match = True
            elif fmt_pref in ("video", "mp4") and meme.get("videoRef"):
                fmt_match = True
            elif fmt_pref in ("image", "png", "webp") and meme.get("imageRef"):
                fmt_match = True

        score = calculate_composite_score(
            keyword_score=kw_score,
            semantic_score=sem_score,
            emotion_match=emo_match,
            emotion_secondary=emo_sec_match,
            popularity_score=pop_score,
            format_match=fmt_match,
            recency_days=0,
        )

        scored.append({"meme": meme, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    deduped = deduplicate(scored)
    top = [s for s in deduped if s["score"] > 0.05] or deduped

    primary = _to_match(top[0]["meme"], top[0]["score"])
    top_five = [_to_match(s["meme"], s["score"]) for s in top[:5]]
    alternatives = [_to_match(s["meme"], s["score"]) for s in top[1:11]]

    viral = sorted(
        memes,
        key=lambda m: m.get("viralScore", 0) + m.get("usageCount", 0) * 0.1,
        reverse=True,
    )[:5]
    viral_suggestions = [_to_match(m, 0.78) for m in viral]

    gifs = [s["meme"]["gifRef"] for s in top[:5] if s["meme"].get("gifRef")]

    latency = max(int((time.perf_counter() - start) * 1000), 1)

    tag_str = ", ".join(rules.tags) if rules.tags else "general vibe"
    explanation_text = (
        f"{primary['explanation']} This meme perfectly fits because your situation aligns with "
        f"the '{primary['category'].replace('_', ' ')}' context ({tag_str})."
    )
    primary = {**primary, "explanation": explanation_text}

    return {
        "primary": primary,
        "topFive": top_five,
        "alternatives": alternatives,
        "detectedCategories": rules.categories,
        "detectedTags": rules.tags,
        "emotion": detected_emo,
        "gifs": gifs,
        "viralSuggestions": viral_suggestions,
        "latencyMs": latency,
    }


def export_txt(result: dict, query: str) -> str:
    lines = [
        "=== MemeGPT Result ===",
        "",
        f"Situation: {query}",
        "",
        "--- Primary Meme ---",
        f"Name: {result['primary']['name']}",
        f"Category: {result['primary']['category']}",
        f"Dialogue: {result['primary']['dialogue']}",
        f"Confidence: {int(result['primary']['confidence'] * 100)}%",
        f"Explanation: {result['primary']['explanation']}",
        "",
        "--- Top 5 ---",
    ]
    for i, m in enumerate(result.get("topFive", []), 1):
        lines.append(f"{i}. {m['name']} ({int(m['confidence']*100)}%) — \"{m['dialogue']}\"")
    lines.append("")
    lines.append("--- Alternatives ---")
    for i, m in enumerate(result.get("alternatives", []), 1):
        lines.append(f"{i}. {m['name']} ({int(m['confidence']*100)}%) — \"{m['dialogue']}\"")
    return "\n".join(lines)


def export_markdown(result: dict, query: str) -> str:
    p = result["primary"]
    md = f"""# MemeGPT Result

## Situation
> {query}

## Primary Meme
- **Name:** {p['name']}
- **Category:** {p['category']}
- **Dialogue:** "{p['dialogue']}"
- **Confidence:** {int(p['confidence']*100)}%
- **Explanation:** {p['explanation']}

## Top 5
"""
    for i, m in enumerate(result.get("topFive", []), 1):
        md += f"{i}. **{m['name']}** ({int(m['confidence']*100)}%) — \"{m['dialogue']}\"\n"
    return md
