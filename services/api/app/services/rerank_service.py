"""
Re-ranking Service — applies business logic on top of vector similarity scores.
Documented in 03_Backend/Business_Logic.md and 03_ML_PIPELINE_AND_TRAINING.md.

Re-ranking rules:
  +15% if primary emotion matches meme emotion tags
  +8%  secondary emotion match
  +10% popularity boost (weighted)
  +5%  if user prefers GIF and meme has GIF
  Score capped at 1.0
"""
import logging

logger = logging.getLogger("services.rerank")


class RerankService:
    def rerank(
        self,
        results: list,
        intent: dict | None = None,
        emotion: dict | None = None,
        format_pref: str = "any",
    ) -> list[dict]:
        """
        Apply business-logic re-ranking.
        Returns top-5 results sorted by final score descending.
        """
        intent = intent or {}
        emotion = emotion or {"primary": "neutral"}

        scored = []
        for r in results:
            # Handle both {meme: {}, score: N} and flat dict formats
            if isinstance(r, dict) and "meme" in r:
                payload = r["meme"]
                base_score = r.get("score", 0.5)
            else:
                payload = r
                base_score = r.get("score", 0.5) if isinstance(r, dict) else 0.5

            score = float(base_score)
            emotions_list = []
            if isinstance(payload, dict):
                emotions_list = payload.get("emotions", [])

            # +15% primary emotion match
            if emotion.get("primary") in emotions_list:
                score += 0.15

            # +8% secondary emotion match
            if emotion.get("secondary") and emotion["secondary"] in emotions_list:
                score += 0.08

            # +10% popularity boost
            popularity = payload.get("popularity_score", 0) if isinstance(payload, dict) else 0
            score += float(popularity) * 0.10

            # +5% format preference match
            has_gif = payload.get("has_gif", False) if isinstance(payload, dict) else False
            has_video = payload.get("has_video", False) if isinstance(payload, dict) else False
            if format_pref == "gif" and has_gif:
                score += 0.05
            elif format_pref == "video" and has_video:
                score += 0.05

            scored.append({
                "meme": payload,
                "score": min(score, 1.0),
                "vector_score": float(base_score),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:5]


rerank_service = RerankService()
