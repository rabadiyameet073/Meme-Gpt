import time

from app.rule_engine import run_rule_engine
from app.semantic_search import semantic_scores


def _to_match(meme: dict, confidence: float) -> dict:
    return {
        "id": meme["id"],
        "name": meme["name"],
        "category": meme["category"],
        "dialogue": meme["dialogue"],
        "explanation": meme["explanation"],
        "confidence": round(confidence, 2),
        "videoRef": meme.get("videoRef"),
        "gifRef": meme.get("gifRef"),
        "viralScore": meme.get("viralScore", 0),
        "usageCount": meme.get("usageCount", 0),
    }


def match_memes(query: str, memes: list[dict]) -> dict:
    start = time.perf_counter()
    rules = run_rule_engine(query)
    sem = semantic_scores(query, memes)

    scored = []
    q_lower = query.lower()

    for meme in memes:
        score = sem.get(meme["id"], 0) * 0.45

        if meme["category"] in rules.categories:
            score += rules.scores.get(meme["category"], 0) * 0.35

        for kw in meme["keywords"]:
            if kw.lower() in q_lower:
                score += 0.08
            for tag in rules.tags:
                if tag.replace("_", " ") in kw.lower():
                    score += 0.05

        score += min(meme.get("viralScore", 0) / 100, 0.1)
        score += min(meme.get("usageCount", 0) / 1000, 0.05)
        scored.append({"meme": meme, "score": min(score, 0.99)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = [s for s in scored if s["score"] > 0.05] or scored

    primary = _to_match(top[0]["meme"], top[0]["score"])
    top_five = [_to_match(s["meme"], s["score"]) for s in top[:5]]
    alternatives = [_to_match(s["meme"], s["score"]) for s in top[1:11]]

    viral = sorted(
        memes,
        key=lambda m: m.get("viralScore", 0) + m.get("usageCount", 0) * 0.1,
        reverse=True,
    )[:5]
    viral_suggestions = [_to_match(m, 0.75) for m in viral]

    gifs = [s["meme"]["gifRef"] for s in top[:5] if s["meme"].get("gifRef")]

    latency = int((time.perf_counter() - start) * 1000)

    explanation = (
        f"{primary['explanation']} This meme fits because your situation aligns with "
        f"the {primary['category'].replace('_', ' ')} theme."
    )
    primary = {**primary, "explanation": explanation}

    return {
        "primary": primary,
        "topFive": top_five,
        "alternatives": alternatives,
        "detectedCategories": rules.categories,
        "detectedTags": rules.tags,
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
    for i, m in enumerate(result["topFive"], 1):
        lines.append(f"{i}. {m['name']} ({int(m['confidence']*100)}%) — \"{m['dialogue']}\"")
    lines.append("")
    lines.append("--- Alternatives ---")
    for i, m in enumerate(result["alternatives"], 1):
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
    for i, m in enumerate(result["topFive"], 1):
        md += f"{i}. **{m['name']}** ({int(m['confidence']*100)}%) — \"{m['dialogue']}\"\n"
    return md
