"""Suggestion Chips Service for MemeGPT.
Specification: 08_Features/Suggestion_Chips.md
"""

import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.suggestion_chips")

STATIC_SUGGESTION_CHIPS = [
    {"label": "🤦 Monday vibe", "query": "Monday morning feeling", "emotion": "sadness"},
    {"label": "😤 Frustration", "query": "when everything goes wrong", "emotion": "anger"},
    {"label": "🎉 Win", "query": "when you finally succeed", "emotion": "joy"},
    {"label": "💻 Programmer life", "query": "when the code works on first try", "emotion": "surprise"},
    {"label": "🏠 WFH", "query": "working from home struggles", "emotion": "neutral"},
    {"label": "😴 Tired", "query": "when you haven't slept enough", "emotion": "sadness"},
    {"label": "🔥 Savage", "query": "sarcastic comeback moment", "emotion": "anger"},
    {"label": "💀 Dead", "query": "when something is too funny", "emotion": "joy"},
]


def get_static_suggestion_chips() -> List[Dict[str, str]]:
    """Return catalog of static suggestion chips."""
    return [c.copy() for c in STATIC_SUGGESTION_CHIPS]


def get_dynamic_time_based_chips(dt: Optional[datetime] = None) -> List[Dict[str, str]]:
    """Return time-contextual suggestion chips based on day and hour.
    
    Rules from 08_Features/Suggestion_Chips.md:
        - Monday 6–10 AM: [Monday morning] [Need coffee] [Back to work]
        - Friday 3–6 PM: [Friday feeling] [Weekend plans] [Almost there]
        - Weekend (Sat/Sun): [Weekend vibes] [Sunday scaries] [No work today]
    """
    now = dt or datetime.now(timezone.utc)
    weekday = now.weekday()  # Monday is 0, Sunday is 6
    hour = now.hour

    if weekday == 0 and 6 <= hour <= 10:
        return [
            {"label": "☕ Monday morning", "query": "Monday morning feeling", "emotion": "sadness"},
            {"label": "☕ Need coffee", "query": "need caffeine to survive", "emotion": "sadness"},
            {"label": "💼 Back to work", "query": "back to work reality check", "emotion": "neutral"},
        ]
    elif weekday == 4 and 15 <= hour <= 18:
        return [
            {"label": "🍻 Friday feeling", "query": "Friday afternoon celebration", "emotion": "joy"},
            {"label": "🌴 Weekend plans", "query": "weekend ready", "emotion": "joy"},
            {"label": "⏳ Almost there", "query": "almost the weekend clock watching", "emotion": "neutral"},
        ]
    elif weekday in (5, 6):
        return [
            {"label": "🏖️ Weekend vibes", "query": "relaxing weekend bliss", "emotion": "joy"},
            {"label": "😱 Sunday scaries", "query": "Sunday night realizing tomorrow is Monday", "emotion": "fear"},
            {"label": "🛌 No work today", "query": "sleeping in no alarms", "emotion": "joy"},
        ]
    return []


def get_active_suggestion_chips(
    limit: int = 8,
    randomize: bool = False,
    dt: Optional[datetime] = None,
) -> List[Dict[str, str]]:
    """Get active suggestion chips combining dynamic and static chips.
    Enforces 5–8 chips maximum to avoid decision paralysis.
    """
    max_chips = min(max(limit, 5), 8)
    dynamic = get_dynamic_time_based_chips(dt)
    static = get_static_suggestion_chips()

    # Prepend dynamic chips without duplicating queries
    dynamic_queries = {d["query"] for d in dynamic}
    combined = list(dynamic) + [s for s in static if s["query"] not in dynamic_queries]

    if randomize:
        # Slight randomize of static portion
        static_portion = combined[len(dynamic):]
        random.shuffle(static_portion)
        combined = combined[:len(dynamic)] + static_portion

    return combined[:max_chips]
