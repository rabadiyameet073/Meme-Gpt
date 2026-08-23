"""Comprehensive Marketing Plan and Growth Strategy Service for MemeGPT.
Specification: 16_SEO_Marketing/Marketing_Plan.md

Covers:
- 4-Phase Growth Funnel (Soft Launch 100 DAU, Community 1K DAU, Content 5K DAU, Scaled Growth 50K DAU)
- Channel Strategy & Traffic Attribution Mix (SEO 50%, ASO 25%, Word of Mouth 15%, Content 5%, Dev API 5%)
- Targeted Subreddit Community Matrix (22.85M combined reach)
- Product Hunt Launch Playbook (Tuesday launch, <1h reply SLA, Top 5 target)
- Month 1 Content Calendar (6 strategic content drops)
- Organic Viral Growth Simulator with K-factor & referral loops
"""

from typing import Any, Dict, List, Optional


# ── 1. 4-Phase Marketing Funnel ────────────────────────────────────────────────

MARKETING_FUNNEL = {
    "total_phases": 4,
    "target_dau_milestone": 50000,
    "phases": [
        {
            "phase": 1,
            "name": "Phase 1: Soft Launch",
            "channels": "Friends & Family, Internal Testers",
            "target_dau": 100,
            "focus": "Core feedback, stability, usability testing",
        },
        {
            "phase": 2,
            "name": "Phase 2: Community Launch",
            "channels": "Reddit, Product Hunt, Twitter/X",
            "target_dau": 1000,
            "focus": "Viral early adopter acquisition and social proof",
        },
        {
            "phase": 3,
            "name": "Phase 3: Content Expansion",
            "channels": "SEO Blog, YouTube, Dev.to, Reels",
            "target_dau": 5000,
            "focus": "High-intent long-tail discovery and technical credibility",
        },
        {
            "phase": 4,
            "name": "Phase 4: Scaled Growth",
            "channels": "Programmatic SEO + ASO + Developer API",
            "target_dau": 50000,
            "focus": "Self-sustaining organic viral flywheel and ecosystem distribution",
        },
    ],
}


# ── 2. Channel Strategy & Traffic Mix ─────────────────────────────────────────

CHANNEL_STRATEGY: List[Dict[str, Any]] = [
    {
        "channel": "SEO",
        "strategy": "10,000+ programmatic indexed meme and tag pages",
        "expected_traffic_share": "50%",
        "expected_traffic_percentage": 50,
        "monthly_cost": "$0",
        "scaling_type": "Compounding organic",
    },
    {
        "channel": "App Store (ASO)",
        "strategy": "Keyword-optimized listing, localized screenshots, conversion video",
        "expected_traffic_share": "25%",
        "expected_traffic_percentage": 25,
        "monthly_cost": "$0",
        "scaling_type": "Store algorithmic discovery",
    },
    {
        "channel": "Word of mouth",
        "strategy": "Instant clipboard copy, deep link meme sharing, referral mechanics",
        "expected_traffic_share": "15%",
        "expected_traffic_percentage": 15,
        "monthly_cost": "$0",
        "scaling_type": "Viral peer-to-peer sharing",
    },
    {
        "channel": "Content marketing",
        "strategy": "Technical engineering blogs, meme listicles, social reels",
        "expected_traffic_share": "5%",
        "expected_traffic_percentage": 5,
        "monthly_cost": "$0",
        "scaling_type": "Top-of-funnel brand awareness",
    },
    {
        "channel": "Developer API",
        "strategy": "Generous free tier for Discord bot builders and app creators",
        "expected_traffic_share": "5%",
        "expected_traffic_percentage": 5,
        "monthly_cost": "$0",
        "scaling_type": "Ecosystem API integrations",
    },
]


# ── 3. Reddit Target Subreddits Matrix ────────────────────────────────────────

REDDIT_TARGETS: List[Dict[str, Any]] = [
    {
        "subreddit": "r/SideProject",
        "members": "250K",
        "member_count": 250000,
        "post_strategy": "I built an AI meme search engine that understands what you mean, not just keywords",
        "post_type": "Showcase / Founder Journey",
    },
    {
        "subreddit": "r/InternetIsBeautiful",
        "members": "17M",
        "member_count": 17000000,
        "post_strategy": "MemeGPT — describe a feeling or situation, get the exact perfect meme",
        "post_type": "Utility Discovery",
    },
    {
        "subreddit": "r/webdev",
        "members": "2M",
        "member_count": 2000000,
        "post_strategy": "Technical deep-dive: Building a sub-50ms semantic search engine with FastAPI & Qdrant",
        "post_type": "Technical Architecture",
    },
    {
        "subreddit": "r/ProgrammerHumor",
        "members": "3M",
        "member_count": 3000000,
        "post_strategy": "Demo finding developer memes (e.g. 'merge conflict in prod', 'css centering')",
        "post_type": "Humor Demo & Niche Appeal",
    },
    {
        "subreddit": "r/artificial",
        "members": "600K",
        "member_count": 600000,
        "post_strategy": "AI/ML architecture post: MiniLM embeddings + Groq LPU intent parsing breakdown",
        "post_type": "AI Research / ML Discussion",
    },
]


# ── 4. Product Hunt Launch Playbook ───────────────────────────────────────────

PRODUCT_HUNT_PLAYBOOK = {
    "target_launch_day": "Tuesday",
    "rationale": "Highest global visitor and voter traffic on Product Hunt",
    "submission_assets": [
        "Catchy 60-character tagline ('AI Meme Finder — Describe any feeling, get the perfect meme')",
        "Comprehensive 250-word product description",
        "4 high-resolution 1270x760 product screenshots",
        "60-second high-framerate demo video",
    ],
    "maker_comment_strategy": "Post transparent founding story within 2 minutes of launch explaining why old meme search is broken",
    "community_response_sla": "Reply to 100% of comments within 1 hour",
    "target_ranking": "Top 5 Product of the Day",
}


# ── 5. Month 1 Content Calendar ───────────────────────────────────────────────

CONTENT_CALENDAR: List[Dict[str, Any]] = [
    {
        "week": "Week 1",
        "title": "I built an AI meme search engine",
        "platform": "Reddit",
        "channel": "r/SideProject & r/InternetIsBeautiful",
        "objective": "First public reaction and beta feedback",
    },
    {
        "week": "Week 2",
        "title": "Product Hunt Launch Day",
        "platform": "Product Hunt",
        "channel": "Product Hunt Community",
        "objective": "Top 5 Product of the Day badge & early adopters",
    },
    {
        "week": "Week 2",
        "title": "60-second Product Demo Video",
        "platform": "Twitter / X",
        "channel": "@memegpt",
        "objective": "Social media viral amplification",
    },
    {
        "week": "Week 3",
        "title": "How I Built MemeGPT (Architecture & ML Pipeline)",
        "platform": "Dev.to",
        "channel": "Dev.to / Hashnode",
        "objective": "Developer credibility and backlink authority",
    },
    {
        "week": "Week 4",
        "title": "Top 10 Work Memes for Monday Mornings",
        "platform": "Blog",
        "channel": "memegpt.com/blog",
        "objective": "Programmatic SEO landing page indexing",
    },
    {
        "week": "Week 4",
        "title": "MemeGPT Engineering Architecture Deep Dive",
        "platform": "Twitter / X",
        "channel": "@memegpt Thread",
        "objective": "Tech community engagement and bookmarks",
    },
]


# ── 6. Service Functions ──────────────────────────────────────────────────────

def get_marketing_funnel() -> Dict[str, Any]:
    """Retrieve 4-phase marketing growth funnel."""
    return MARKETING_FUNNEL


def get_channel_strategy() -> Dict[str, Any]:
    """Retrieve channel acquisition mix and expected traffic shares."""
    return {
        "total_channels": len(CHANNEL_STRATEGY),
        "total_budget": "$0 / month (100% organic acquisition)",
        "channels": CHANNEL_STRATEGY,
    }


def get_reddit_targets() -> Dict[str, Any]:
    """Retrieve 5 target subreddits with customized post angles and total reach."""
    total_members = sum(r["member_count"] for r in REDDIT_TARGETS)
    return {
        "total_subreddits": len(REDDIT_TARGETS),
        "aggregate_audience_reach": f"{round(total_members / 1_000_000, 2)}M members",
        "subreddits": REDDIT_TARGETS,
    }


def get_product_hunt_playbook() -> Dict[str, Any]:
    """Retrieve Product Hunt launch execution playbook."""
    return PRODUCT_HUNT_PLAYBOOK


def get_content_calendar() -> Dict[str, Any]:
    """Retrieve Month 1 weekly content publishing schedule."""
    return {
        "total_content_drops": len(CONTENT_CALENDAR),
        "schedule": CONTENT_CALENDAR,
    }


def simulate_viral_growth(
    initial_dau: int = 100,
    viral_k_factor: float = 1.15,
    days: int = 30,
) -> Dict[str, Any]:
    """Simulate viral DAU growth trajectory based on referral sharing K-factor."""
    trajectory = []
    current_dau = float(initial_dau)

    for d in range(1, days + 1):
        # Daily organic compounding with slight viral decay resistance
        daily_growth = (viral_k_factor - 1.0) / 7.0  # Normalized daily growth
        current_dau = current_dau * (1.0 + max(0.0, daily_growth))
        if d in [1, 7, 14, 21, 30]:
            trajectory.append({
                "day": d,
                "projected_dau": int(round(current_dau)),
            })

    return {
        "initial_dau": initial_dau,
        "viral_k_factor": viral_k_factor,
        "simulation_days": days,
        "final_projected_dau": int(round(current_dau)),
        "trajectory_milestones": trajectory,
    }
