"""App Store Optimization (ASO) Service for MemeGPT.
Specification: 16_SEO_Marketing/App_Store_Optimization.md

Covers:
- iOS App Store metadata & keyword optimization
- Google Play Store metadata, short description, and tags
- 5-Screenshot conversion narrative plan
- Keyword research matrix (search volume & competition)
- In-app rating prompt strategy & eligibility evaluator
- 6 ASO Best Practices
"""

from typing import Any, Dict, List, Optional


# ── 1. iOS App Store Listing Metadata ──────────────────────────────────────────

IOS_LISTING = {
    "platform": "iOS App Store",
    "app_name": "MemeGPT – AI Meme Finder",
    "app_name_character_count": 25,
    "subtitle": "Find Perfect Memes Instantly",
    "subtitle_character_count": 27,
    "primary_category": "Entertainment",
    "secondary_category": "Utilities",
    "keywords_field": "meme,ai meme,meme finder,funny memes,meme generator,gpt meme,meme download,reaction meme,gif meme",
    "keywords_character_count": 94,  # Within 100 char limit
    "description": (
        "🤣 Find the PERFECT meme for any situation in seconds using AI!\n\n"
        "Just type what's happening — \"my boss called at midnight\" — and MemeGPT "
        "finds exactly the right meme. Download as GIF, PNG, or video.\n\n"
        "★ FEATURES\n"
        "• AI-powered meme search — not just keyword matching\n"
        "• 10,000+ memes and GIFs\n"
        "• All formats: GIF, PNG, MP4, WebP\n"
        "• Instant copy to clipboard\n"
        "• Save favorites to your personal library\n"
        "• Zero ads. Zero watermarks.\n\n"
        "★ HOW IT WORKS\n"
        "1. Type anything — a situation, a feeling, a conversation\n"
        "2. AI finds the perfect meme in under 2 seconds\n"
        "3. Download, copy, or share instantly\n\n"
        "★ WHY MEMEGPT?\n"
        "Unlike Google or Giphy, MemeGPT understands what you MEAN, "
        "not just what you TYPE. Try it once — you'll never search for memes the old way again."
    ),
}


# ── 2. Google Play Store Listing Metadata ─────────────────────────────────────

GOOGLE_PLAY_LISTING = {
    "platform": "Google Play Store",
    "app_name": "MemeGPT: AI Meme Finder & Download",
    "short_description": "Type anything → AI finds your perfect meme. Download GIF, PNG, video free!",
    "short_description_character_count": 76,  # Within 80 char limit
    "category": "Entertainment",
    "tags": ["meme", "funny", "gif", "ai", "humor"],
}


# ── 3. Screenshot Strategy (5 Screenshots) ────────────────────────────────────

SCREENSHOT_STRATEGY = [
    {
        "position": 1,
        "screen": "Home screen with search",
        "purpose": "Show the clean, intuitive search interface",
        "key_message": "Just type anything...",
        "focus_element": "Natural language prompt input bar",
    },
    {
        "position": 2,
        "screen": "Search results (2 seconds)",
        "purpose": "Show search speed, relevance, and semantic quality",
        "key_message": "AI finds perfect memes instantly",
        "focus_element": "Result grid with composite scores and tags",
    },
    {
        "position": 3,
        "screen": "Meme detail with formats",
        "purpose": "Show format flexibility and download options",
        "key_message": "GIF, PNG, MP4 — your choice",
        "focus_element": "Format picker and resolution switcher",
    },
    {
        "position": 4,
        "screen": "Native share sheet",
        "purpose": "Show instant usability and social sharing",
        "key_message": "Share anywhere in seconds",
        "focus_element": "WhatsApp, iMessage, and Instagram sharing",
    },
    {
        "position": 5,
        "screen": "Trending page",
        "purpose": "Show catalog depth, variety, and community favorites",
        "key_message": "10,000+ memes and growing",
        "focus_element": "Trending memes carousel and categories",
    },
]


# ── 4. Keyword Research Matrix ────────────────────────────────────────────────

KEYWORD_RESEARCH = [
    {"keyword": "meme", "monthly_searches": 1200000, "competition": "Very High", "strategy": "Use in title"},
    {"keyword": "meme generator", "monthly_searches": 450000, "competition": "Very High", "strategy": "Use in keywords field"},
    {"keyword": "funny memes", "monthly_searches": 200000, "competition": "High", "strategy": "Blog and description copy"},
    {"keyword": "gif maker", "monthly_searches": 100000, "competition": "Medium", "strategy": "Use in keywords field"},
    {"keyword": "ai meme", "monthly_searches": 40000, "competition": "Low", "strategy": "Title and description copy"},
    {"keyword": "meme finder", "monthly_searches": 22000, "competition": "Very Low", "strategy": "Title exact match target"},
    {"keyword": "meme gpt", "monthly_searches": 8000, "competition": "Very Low", "strategy": "Primary brand keyword"},
]


# ── 5. Rating & Review Prompt Strategy ─────────────────────────────────────────

RATING_PROMPT_STRATEGY = {
    "triggers": [
        {"trigger_event": "3rd successful search", "prompt_copy": "Enjoying MemeGPT? Rate us!", "goal": "Capture strong first impression ratings"},
        {"trigger_event": "5th meme download", "prompt_copy": "You've downloaded 5 memes! Rate us?", "goal": "Capture engaged power user ratings"},
        {"trigger_event": "Successful meme share", "prompt_copy": "Thanks for sharing! Rate us?", "goal": "Capture viral promoter ratings"},
    ],
    "strict_rules": [
        "Never prompt on first app launch or first search",
        "Never prompt after an error, network drop, or 0-result search",
        "Enforce maximum 1 prompt per 30-day window",
        "Always offer clear 'Not now' dismissal button",
    ],
}


# ── 6. ASO Best Practices ──────────────────────────────────────────────────────

ASO_BEST_PRACTICES = [
    {"practice": "Include primary keyword in app title", "details": "'MemeGPT – AI Meme Finder' incorporates high-intent low-competition keyword directly."},
    {"practice": "Optimize first 2 lines of description", "details": "Hook users before the 'Read More' fold with high-impact value proposition."},
    {"practice": "Storytelling screenshot sequence", "details": "Guide prospective users through the full search -> find -> download -> share journey."},
    {"practice": "Localize for top growth markets", "details": "Translate metadata and screenshots for English, Hindi, Spanish, and Portuguese."},
    {"practice": "Refresh screenshots every major release", "details": "Stale visual assets directly correlate with 15-25% drop in store conversions."},
    {"practice": "100% review response rate", "details": "Acknowledge 5-star reviews and actively troubleshoot negative user reviews within 24h."},
]


# ── 7. Service Functions ──────────────────────────────────────────────────────

def get_ios_app_store_listing() -> Dict[str, Any]:
    """Retrieve iOS App Store metadata, character counts, and keyword fields."""
    return IOS_LISTING


def get_google_play_listing() -> Dict[str, Any]:
    """Retrieve Google Play Store metadata, short description, and tags."""
    return GOOGLE_PLAY_LISTING


def get_screenshot_strategy() -> Dict[str, Any]:
    """Retrieve the 5-screenshot storytelling visual conversion sequence."""
    return {
        "total_screenshots": len(SCREENSHOT_STRATEGY),
        "screenshots": SCREENSHOT_STRATEGY,
    }


def get_keyword_research_matrix() -> Dict[str, Any]:
    """Retrieve target keywords with monthly search volume, competition, and ranking strategy."""
    total_searches = sum(k["monthly_searches"] for k in KEYWORD_RESEARCH)
    return {
        "total_tracked_keywords": len(KEYWORD_RESEARCH),
        "aggregate_monthly_search_volume": total_searches,
        "keywords": KEYWORD_RESEARCH,
    }


def get_rating_prompt_strategy() -> Dict[str, Any]:
    """Retrieve rating prompt triggers and safety rules."""
    return RATING_PROMPT_STRATEGY


def get_aso_best_practices() -> Dict[str, Any]:
    """Retrieve the 6 ASO best practices."""
    return {
        "total_practices": len(ASO_BEST_PRACTICES),
        "practices": ASO_BEST_PRACTICES,
    }


def evaluate_rating_prompt_eligibility(
    searches_count: int,
    downloads_count: int,
    shares_count: int,
    days_since_last_prompt: int,
    last_action_was_error: bool = False,
) -> Dict[str, Any]:
    """Evaluate whether the user is eligible to receive an in-app rating prompt."""
    if last_action_was_error:
        return {
            "eligible": False,
            "reason": "Blocked: Never prompt after an error or failed action.",
        }

    if days_since_last_prompt < 30:
        return {
            "eligible": False,
            "reason": f"Blocked: Enforced 30-day cooldown (only {days_since_last_prompt} days elapsed).",
        }

    if searches_count >= 3:
        return {
            "eligible": True,
            "trigger": "3rd successful search",
            "prompt_copy": "Enjoying MemeGPT? Rate us!",
        }

    if downloads_count >= 5:
        return {
            "eligible": True,
            "trigger": "5th meme download",
            "prompt_copy": "You've downloaded 5 memes! Rate us?",
        }

    if shares_count >= 1:
        return {
            "eligible": True,
            "trigger": "Successful meme share",
            "prompt_copy": "Thanks for sharing! Rate us?",
        }

    return {
        "eligible": False,
        "reason": "User has not yet reached any engagement thresholds (3 searches, 5 downloads, or 1 share).",
    }
