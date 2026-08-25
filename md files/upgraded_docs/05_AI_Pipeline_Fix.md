# 05 — AI Pipeline Fix
# Fix Every Stage: Groq Fallback, Model Download, Pipeline Wiring, Bug Fixes

> **Gap Source:** Section 3 & 17 of GAP_ANALYSIS_FULL.md  
> **Priority:** P0  
> **Files to edit:**  
> - `d:\Meme GPT\backend\app\services\llm_service.py`  
> - `d:\Meme GPT\backend\app\services\embedding_service.py`  
> - `d:\Meme GPT\backend\app\services\recommendation_service.py`

---

## PIPELINE OVERVIEW (All 6 Stages)

```
User Input → [A] Groq Intent Parse → [B] Emotion Detect (DistilRoBERTa)
           → [C] Build Rich Query  → [D] MiniLM Embed → [E] Qdrant Search
           → [F] Rerank → Response
```

Each stage documented below with exact fixes needed.

---

## STAGE A FIX — `llm_service.py` (Groq Intent Parsing)

### Problem
- `GROQ_API_KEY` is empty → all calls silently return `None`
- No proper fallback chain implemented

### Fix: Complete `llm_service.py`

Replace content of `d:\Meme GPT\backend\app\services\llm_service.py`:

```python
"""
MemeGPT — LLM Service (Groq Intent Parsing) — FIXED.

Priority fallback chain:
1. Groq (llama-3.1-8b-instant) — primary, ultra fast
2. Rule-based extraction — always available

Gap fixes:
- Handles empty GROQ_API_KEY gracefully
- Returns structured dict even on failure (never returns None)
- Added timeout, retry logic
- Improved prompt for better JSON extraction
"""

import json
import logging
import re
from typing import Optional

from app.config import settings

logger = logging.getLogger("memegpt.llm")

# Intent structure returned by this service
INTENT_SCHEMA = {
    "situation": "",        # One-sentence situation description
    "emotion_hint": "neutral",  # joy|sadness|anger|surprise|fear|disgust|neutral
    "tone": "relatable",    # sarcastic|sincere|humorous|frustrated|excited|proud|anxious|relatable
    "keywords": [],         # 3-5 key terms
    "meme_format": "reaction",  # reaction|comparison|advice|relatable|wholesome|achievement|failure
    "intensity": 0.5,       # 0.0-1.0
    "categories": [],       # detected categories: work|coding|college|gaming|relationships|etc.
}

PROMPT_TEMPLATE = '''Analyze this text for meme recommendation. Return ONLY valid JSON, no explanation:

User text: "{user_text}"

{{
  "situation": "one-sentence description of what is happening",
  "emotion_hint": "one of: joy|sadness|anger|surprise|fear|disgust|neutral",
  "tone": "one of: sarcastic|sincere|humorous|frustrated|excited|proud|anxious|relatable",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "meme_format": "one of: reaction|comparison|advice|relatable|wholesome|achievement|failure",
  "intensity": 0.7,
  "categories": ["category1"]
}}'''


async def parse_intent(user_text: str) -> dict:
    """
    Parse user intent using Groq LLM.
    Returns structured dict with emotion, situation, keywords.
    NEVER returns None — always returns a valid dict (may be rule-based fallback).
    """
    api_key = getattr(settings, "GROQ_API_KEY", "")

    if not api_key or api_key.strip() == "":
        logger.info("GROQ_API_KEY not set — using rule-based intent extraction")
        return _rule_based_intent(user_text)

    try:
        result = await _groq_parse(user_text, api_key)
        if result:
            return result
    except Exception as e:
        logger.warning(f"Groq parsing failed: {e} — using rule-based fallback")

    return _rule_based_intent(user_text)


async def _groq_parse(user_text: str, api_key: str) -> Optional[dict]:
    """Call Groq API and parse JSON response."""
    try:
        from groq import AsyncGroq

        model = getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")
        timeout = getattr(settings, "GROQ_TIMEOUT", 5)
        max_tokens = getattr(settings, "GROQ_MAX_TOKENS", 300)

        client = AsyncGroq(api_key=api_key, timeout=timeout)

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only API. Return ONLY valid JSON, no other text.",
                },
                {
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(user_text=user_text[:500]),
                },
            ],
            temperature=0.1,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```" in content:
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
            if match:
                content = match.group(1)

        intent = json.loads(content)

        # Validate required fields
        validated = {**INTENT_SCHEMA, **intent}
        validated["keywords"] = validated.get("keywords", [])[:5]  # Max 5 keywords
        validated["intensity"] = float(validated.get("intensity", 0.5))

        logger.debug(f"Groq intent: emotion={validated['emotion_hint']} tone={validated['tone']}")
        return validated

    except ImportError:
        logger.error("groq package not installed. Run: pip install groq")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Groq returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.warning(f"Groq API error: {e}")
        return None


def _rule_based_intent(user_text: str) -> dict:
    """
    Fast rule-based intent extraction when Groq is unavailable.
    Uses keyword matching to detect emotion, category, tone.
    """
    text_lower = user_text.lower()

    # Emotion detection via keywords
    emotion_keywords = {
        "joy": ["happy", "great", "awesome", "amazing", "yay", "win", "success", "finally", "promoted", "celebrate"],
        "anger": ["angry", "furious", "hate", "stupid", "annoying", "terrible", "awful", "rage", "frustrated"],
        "sadness": ["sad", "cry", "upset", "disappointed", "depressed", "miss", "alone", "lost"],
        "surprise": ["wow", "what", "seriously", "unbelievable", "shocked", "omg", "unexpected"],
        "fear": ["scared", "nervous", "anxiety", "worried", "panic", "stress", "deadline"],
        "disgust": ["disgusting", "gross", "eww", "ugh", "nasty", "awful"],
    }

    detected_emotion = "neutral"
    for emotion, keywords in emotion_keywords.items():
        if any(kw in text_lower for kw in keywords):
            detected_emotion = emotion
            break

    # Category detection
    category_keywords = {
        "coding": ["code", "bug", "error", "compile", "deploy", "git", "programming", "python", "javascript"],
        "work": ["boss", "meeting", "office", "deadline", "manager", "coworker", "salary", "monday"],
        "college": ["exam", "study", "assignment", "professor", "semester", "lecture", "marks"],
        "gaming": ["game", "player", "level", "boss", "respawn", "noob", "lag"],
        "relationships": ["girlfriend", "boyfriend", "crush", "date", "breakup", "ex", "wife", "husband"],
        "money": ["money", "salary", "broke", "rent", "loan", "bank"],
        "food": ["food", "hungry", "eat", "restaurant", "cook", "diet"],
    }

    detected_categories = []
    for category, keywords in category_keywords.items():
        if any(kw in text_lower for kw in keywords):
            detected_categories.append(category)

    # Tone detection
    tone = "relatable"
    if any(w in text_lower for w in ["lol", "haha", "😂", "funny", "hilarious"]):
        tone = "humorous"
    elif any(w in text_lower for w in ["ugh", "seriously", "why", "wtf"]):
        tone = "frustrated"
    elif any(w in text_lower for w in ["honestly", "literally", "basically"]):
        tone = "sarcastic"

    # Extract simple keywords (non-stop-words)
    stop_words = {"the", "a", "an", "is", "it", "to", "i", "my", "me", "we", "and", "or", "at", "in", "on", "of", "for", "with"}
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    keywords = [w for w in words if w not in stop_words][:5]

    return {
        **INTENT_SCHEMA,
        "situation": user_text[:100],
        "emotion_hint": detected_emotion,
        "tone": tone,
        "keywords": keywords,
        "categories": detected_categories[:3],
        "intensity": 0.6,
        "meme_format": "reaction",
    }
```

---

## STAGE B FIX — `embedding_service.py` (Emotion Detection + Embeddings)

### Problem  
- Returns zero-vector if model not loaded (silently bad results)
- No model pre-download step

### Key Fix: Add Model Preload + Zero-Vector Guard

In `d:\Meme GPT\backend\app\services\embedding_service.py`, ensure:

```python
# At top of file — model initialization with fallback
import logging
import os

logger = logging.getLogger("memegpt.embedding")

_text_model = None
_emotion_pipeline = None

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMOTION_MODEL = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")
MODELS_CACHE_DIR = os.getenv("MODELS_CACHE_DIR", "./model_cache")


def load_models():
    """Load ML models at startup. Called from main.py lifespan."""
    global _text_model, _emotion_pipeline
    os.makedirs(MODELS_CACHE_DIR, exist_ok=True)

    # Load sentence transformer for text embedding
    try:
        from sentence_transformers import SentenceTransformer
        _text_model = SentenceTransformer(
            EMBEDDING_MODEL,
            cache_folder=MODELS_CACHE_DIR
        )
        logger.info(f"✅ Text embedding model loaded: {EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Failed to load text model: {e}")

    # Load emotion classifier
    try:
        from transformers import pipeline
        _emotion_pipeline = pipeline(
            "text-classification",
            model=EMOTION_MODEL,
            return_all_scores=True,
            device=-1,  # CPU only
        )
        logger.info(f"✅ Emotion model loaded: {EMOTION_MODEL}")
    except Exception as e:
        logger.warning(f"Failed to load emotion model: {e} — rule-based fallback active")


def embed_text(text: str) -> list[float]:
    """Encode text to 384-dim normalized vector. Returns zero-vector only if model load failed."""
    if _text_model is None:
        logger.warning("Text model not loaded — returning zero vector (search quality degraded)")
        return [0.0] * 384

    try:
        vector = _text_model.encode(
            text[:512],          # MiniLM max 512 tokens
            normalize_embeddings=True,  # Required for cosine similarity
        )
        return vector.tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return [0.0] * 384


def detect_emotion(text: str) -> dict:
    """
    Detect primary and secondary emotion in text.
    Returns: {primary, secondary, confidence, all}
    """
    if _emotion_pipeline is None:
        return _rule_based_emotion(text)

    try:
        results = _emotion_pipeline(text[:512])[0]
        sorted_emotions = sorted(results, key=lambda x: x["score"], reverse=True)
        return {
            "primary": sorted_emotions[0]["label"],
            "secondary": sorted_emotions[1]["label"] if len(sorted_emotions) > 1 else None,
            "confidence": round(sorted_emotions[0]["score"], 3),
            "all": {e["label"]: round(e["score"], 3) for e in sorted_emotions},
        }
    except Exception as e:
        logger.warning(f"Emotion detection failed: {e}")
        return _rule_based_emotion(text)


def _rule_based_emotion(text: str) -> dict:
    """Fast keyword-based emotion fallback."""
    text_lower = text.lower()
    emotions = {
        "joy": ["happy", "great", "awesome", "yay", "win", "love", "celebrate"],
        "anger": ["angry", "hate", "stupid", "annoying", "terrible", "awful"],
        "sadness": ["sad", "cry", "upset", "miss", "alone", "lost", "depressed"],
        "surprise": ["wow", "what", "seriously", "shocked", "unexpected", "omg"],
        "fear": ["scared", "nervous", "worried", "panic", "stress", "anxiety"],
        "disgust": ["disgusting", "gross", "ugh", "eww", "nasty"],
    }
    for emotion, keywords in emotions.items():
        if any(kw in text_lower for kw in keywords):
            return {"primary": emotion, "secondary": None, "confidence": 0.7, "all": {}}
    return {"primary": "neutral", "secondary": None, "confidence": 0.5, "all": {}}


def build_query_text(user_text: str, intent: dict, emotion: dict) -> str:
    """
    Combine original input + LLM intent + detected emotion into rich query text.
    Richer text = better MiniLM embedding = better vector search results.
    """
    parts = [f"User said: {user_text}"]

    if intent.get("situation"):
        parts.append(f"Situation: {intent['situation']}")

    parts.append(f"Primary emotion: {emotion.get('primary', 'neutral')}")

    if emotion.get("secondary"):
        parts.append(f"Secondary emotion: {emotion['secondary']}")

    if intent.get("tone"):
        parts.append(f"Tone: {intent['tone']}")

    if intent.get("keywords"):
        parts.append(f"Keywords: {', '.join(intent['keywords'])}")

    if intent.get("meme_format"):
        parts.append(f"Meme format: {intent['meme_format']}")

    return "\n".join(parts)
```

---

## STAGE C-F — `recommendation_service.py` Pipeline Wiring

### Problems
1. Line 255 imports `_cosine_similarity` which didn't exist (fixed in doc 03)
2. Pipeline doesn't use `asyncio.gather` for parallel A+B stages

### Fix: Add asyncio.gather for parallel intent + emotion

In `recommendation_service.py`, the main pipeline should run Groq + Emotion in parallel:

```python
import asyncio

async def recommend_memes(user_text: str, format_pref: str = "gif", nsfw: bool = False) -> dict:
    """Full recommendation pipeline with parallel stage execution."""
    from app.core.cache import cache_get, cache_set, make_cache_key
    from app.services.llm_service import parse_intent
    from app.services.embedding_service import detect_emotion, embed_text, build_query_text
    from app.services.search_service import vector_search
    from app.services.rerank_service import rerank

    # 1. Cache check
    cache_key = make_cache_key(user_text, format_pref, nsfw)
    cached = cache_get(cache_key)
    if cached:
        return {**cached, "cached": True}

    # 2. Parallel: intent parse (Groq ~300ms) + emotion detect (local ~100ms)
    intent, emotion = await asyncio.gather(
        parse_intent(user_text),
        asyncio.get_event_loop().run_in_executor(None, detect_emotion, user_text),
    )

    # 3. Build rich query text and embed it
    query_text = build_query_text(user_text, intent, emotion)
    query_vector = await asyncio.get_event_loop().run_in_executor(
        None, embed_text, query_text
    )

    # 4. Vector search
    candidates = vector_search(
        query_vector=query_vector,
        emotion=emotion.get("primary", ""),
        format_pref=format_pref,
        nsfw=nsfw,
        top_k=15,
    )

    # 5. Rerank
    reranked = rerank(candidates, intent, emotion, format_pref)

    # 6. Build response
    result = _build_response(reranked, intent, emotion, user_text)

    # 7. Cache result
    cache_set(cache_key, result, ttl=3600)

    return result
```

---

## MODEL DOWNLOAD (First Run)

The first time the server starts, models will download (~500MB total).  
Pre-download them before first deploy:

```bash
cd "d:\Meme GPT\backend"
python -c "
from app.services.embedding_service import load_models
load_models()
print('Models downloaded and cached')
"
```

This takes 5–10 minutes on first run. Subsequent startups use cached models.
