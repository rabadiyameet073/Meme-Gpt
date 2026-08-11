"""
LLM Intent Parser — uses Groq API (Llama 3.1 8B) with rule-based fallback.
Target: ~300ms for intent parsing.
"""
import json
import logging
import os
import re

logger = logging.getLogger("services.llm")

INTENT_PROMPT = """Analyze this text for meme recommendation. Return ONLY valid JSON with no explanation:
"{user_text}"

{{
  "situation": "concise one-sentence situation description",
  "emotion_hint": "joy|sadness|anger|surprise|fear|disgust|neutral",
  "tone": "sarcastic|sincere|humorous|frustrated|excited|proud|anxious|relatable",
  "keywords": ["word1", "word2"],
  "meme_format": "reaction|comparison|advice|relatable|wholesome|achievement|failure",
  "intensity": 0.7
}}"""


class LLMService:
    def __init__(self):
        self._client = None
        self._attempted = False

    def _get_client(self):
        if self._attempted:
            return self._client
        self._attempted = True
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            logger.warning("GROQ_API_KEY not set — using rule-based fallback for intent parsing.")
            return None
        try:
            from groq import Groq
            self._client = Groq(api_key=api_key)
            logger.info("Groq LLM client initialised.")
        except Exception as e:
            logger.warning(f"Groq init failed: {e}")
        return self._client

    async def parse_intent(self, user_text: str) -> dict:
        """Parse intent using Groq LLM or rule-based fallback."""
        client = self._get_client()
        if client:
            try:
                prompt = INTENT_PROMPT.format(user_text=user_text[:500])
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200,
                )
                raw = response.choices[0].message.content.strip()
                # Extract JSON even if there's surrounding text
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception as e:
                logger.warning(f"Groq parse failed: {e} — using fallback")

        return self._rule_based_parse(user_text)

    def _rule_based_parse(self, text: str) -> dict:
        """
        Rule-based fallback for intent parsing when Groq is unavailable.
        Good enough for local dev.
        """
        t = text.lower()

        emotion = "neutral"
        situation = text[:100]
        tone = "humorous"
        meme_format = "reaction"

        if any(k in t for k in ["bug", "error", "crash", "broken", "fail", "doesn't work"]):
            emotion = "frustration"
            tone = "frustrated"
        elif any(k in t for k in ["exam", "test", "study", "marks", "grade"]):
            emotion = "anxiety"
            tone = "anxious"
        elif any(k in t for k in ["win", "success", "cracked", "passed", "finally"]):
            emotion = "joy"
            tone = "excited"
            meme_format = "achievement"
        elif any(k in t for k in ["monday", "morning", "tired", "sleep", "alarm"]):
            emotion = "sadness"
            tone = "relatable"
        elif any(k in t for k in ["boss", "meeting", "email", "deadline", "office"]):
            emotion = "frustration"
            tone = "sarcastic"

        keywords = [w for w in re.sub(r"[^\w\s]", "", t).split() if len(w) > 3][:5]

        return {
            "situation": situation,
            "emotion_hint": emotion,
            "tone": tone,
            "keywords": keywords,
            "meme_format": meme_format,
            "intensity": 0.7,
            # Extra fields used internally
            "detected_category": self._detect_category(t),
            "search_keywords": keywords,
        }

    def _detect_category(self, text: str) -> str:
        cats = {
            "coding": ["bug", "code", "deploy", "git", "stack overflow", "prod"],
            "exam": ["exam", "jee", "neet", "test", "marks", "study"],
            "office": ["boss", "meeting", "email", "deadline", "salary"],
            "startup": ["startup", "funding", "investor", "pitch"],
            "gaming": ["game", "gamer", "match", "ranked", "noob"],
            "relationship": ["crush", "date", "breakup", "girlfriend", "boyfriend"],
        }
        for cat, keywords in cats.items():
            if any(k in text for k in keywords):
                return cat
        return "funny"


llm_service = LLMService()
