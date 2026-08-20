"""Suggestion Chips API Router for MemeGPT.
Specification: 08_Features/Suggestion_Chips.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query

from app.services.suggestion_chips_service import (
    get_static_suggestion_chips,
    get_dynamic_time_based_chips,
    get_active_suggestion_chips,
)

logger = logging.getLogger("memegpt.api.chips")
router = APIRouter(prefix="/chips", tags=["Suggestion Chips"])


@router.get("/suggestions", summary="Get active search suggestion chips")
def get_chips(
    limit: int = Query(8, ge=1, le=12, description="Maximum chips to return (default 8)"),
    randomize: bool = Query(False, description="Randomize static chip order"),
):
    """Retrieve time-contextual and static quick-search suggestion chips."""
    chips = get_active_suggestion_chips(limit=limit, randomize=randomize)
    return {
        "success": True,
        "chips": chips,
        "total": len(chips),
    }


@router.get("/catalog", summary="Get complete suggestion chips catalog")
def get_catalog():
    """Retrieve full catalog of static and time-based chips."""
    return {
        "success": True,
        "static_chips": get_static_suggestion_chips(),
        "time_based_rules": [
            {"time_window": "Monday 6–10 AM", "chips": ["Monday morning", "Need coffee", "Back to work"]},
            {"time_window": "Friday 3–6 PM", "chips": ["Friday feeling", "Weekend plans", "Almost there"]},
            {"time_window": "Weekend (Sat-Sun)", "chips": ["Weekend vibes", "Sunday scaries", "No work today"]},
            {"time_window": "Exam season", "chips": ["Exam stress", "All-nighter", "Passing grade"]},
        ],
    }
