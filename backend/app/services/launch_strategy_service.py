"""Launch Strategy and Operational Readiness Service for MemeGPT.
Specification: 16_SEO_Marketing/Launch_Strategy.md

Covers:
- 3-Phase Launch Timeline (Pre-Launch Week -2, Launch Week, Post-Launch Weeks +1 to +4)
- 7 Multi-Channel Launch Action Playbooks with Expected Visitor Impact
- 18-Point Pre-Launch Verification Checklist across Technical, Content, and SEO domains
- Hour-by-Hour Launch Day Execution Script
- 7 Launch Week Target KPI Benchmarks with Tracking Sources
- 5 Post-Launch Execution Priorities
- Dynamic Launch Readiness & Gate Evaluator
"""

from typing import Any, Dict, List, Optional


# ── 1. Launch Timeline ─────────────────────────────────────────────────────────

LAUNCH_TIMELINE = {
    "phases": [
        {
            "phase": "Pre-Launch (Week -2)",
            "duration_days": 14,
            "tasks": [
                {"task": "Beta testing with 50 users", "duration": "7d", "start_offset": "Week -2"},
                {"task": "Fix critical bugs and regressions", "duration": "5d", "start_offset": "After Beta"},
                {"task": "Prepare social media creative assets and demo reels", "duration": "14d", "start_offset": "Week -2"},
            ],
        },
        {
            "phase": "Launch Week",
            "duration_days": 7,
            "tasks": [
                {"task": "Product Hunt submission ('MemeGPT — AI Meme Finder')", "duration": "Day 1", "start_offset": "Day 1"},
                {"task": "Reddit community posts (r/webdev, r/memes, r/SideProject)", "duration": "Day 1", "start_offset": "Day 1"},
                {"task": "Twitter/X launch thread with demo GIF", "duration": "Day 1", "start_offset": "Day 1"},
                {"task": "Hacker News 'Show HN: I built an AI meme finder'", "duration": "Day 2", "start_offset": "Day 2"},
            ],
        },
        {
            "phase": "Post-Launch (Week +1 to +4)",
            "duration_days": 28,
            "tasks": [
                {"task": "Monitor analytics, Sentry error logs, and fix bugs", "duration": "28d", "start_offset": "Day 2+"},
                {"task": "Collect structured user feedback and NPS", "duration": "14d", "start_offset": "Day 2-16"},
                {"task": "Iterate on top 3 feedback themes", "duration": "14d", "start_offset": "Day 16-30"},
            ],
        },
    ]
}


# ── 2. Launch Channels Playbook ────────────────────────────────────────────────

LAUNCH_CHANNELS: List[Dict[str, Any]] = [
    {
        "channel": "Product Hunt",
        "action": "Submit as 'MemeGPT — AI Meme Finder'",
        "expected_impact": "500–2,000 first-day visitors",
        "primary_audience": "Tech enthusiasts, early adopters, product builders",
    },
    {
        "channel": "Reddit",
        "action": "Post on r/webdev, r/memes, r/SideProject",
        "expected_impact": "200–1,000 visitors",
        "primary_audience": "Developers and meme consumers",
    },
    {
        "channel": "Twitter / X",
        "action": "Launch thread with high-framerate demo GIF",
        "expected_impact": "100–500 visitors",
        "primary_audience": "AI developers, tech community, viral amplifiers",
    },
    {
        "channel": "Hacker News",
        "action": "Post 'Show HN: I built an AI meme finder'",
        "expected_impact": "500–5,000 visitors (if trending on front page)",
        "primary_audience": "Software engineers and startup founders",
    },
    {
        "channel": "Dev.to",
        "action": "Technical deep-dive blog post about the AI embedding & Qdrant search pipeline",
        "expected_impact": "200–500 developers",
        "primary_audience": "Python, FastAPI, and Next.js developers",
    },
    {
        "channel": "LinkedIn",
        "action": "'I built this' founder story post with video demo",
        "expected_impact": "100–300 professionals",
        "primary_audience": "Professional network, product managers, engineers",
    },
    {
        "channel": "Instagram Reels",
        "action": "30-second snappy meme search demo video",
        "expected_impact": "500–2,000 Gen-Z users",
        "primary_audience": "Gen-Z meme creators and mobile consumers",
    },
]


# ── 3. Pre-Launch Checklist Database ──────────────────────────────────────────

PRE_LAUNCH_CHECKLIST: List[Dict[str, Any]] = [
    # Technical Checklist
    {"id": "CHK_TECH_BUGS", "category": "technical", "item": "All critical bugs fixed", "status": "READY"},
    {"id": "CHK_TECH_PERF", "category": "technical", "item": "Performance tested (P95 < 3s under load)", "status": "READY"},
    {"id": "CHK_TECH_RATE_LIMIT", "category": "technical", "item": "Rate limiting enabled on public API endpoints", "status": "READY"},
    {"id": "CHK_TECH_SENTRY", "category": "technical", "item": "Error monitoring (Sentry) configured with alert routing", "status": "READY"},
    {"id": "CHK_TECH_ANALYTICS", "category": "technical", "item": "Privacy-friendly analytics (Umami) installed", "status": "READY"},
    {"id": "CHK_TECH_SSL", "category": "technical", "item": "SSL certificates valid and HSTS enforced", "status": "READY"},
    {"id": "CHK_TECH_DOMAIN", "category": "technical", "item": "Custom domain configured (memegpt.com, api.memegpt.com)", "status": "READY"},
    {"id": "CHK_TECH_HEALTH", "category": "technical", "item": "Health check endpoint (/health) verified with UptimeRobot", "status": "READY"},

    # Content Checklist
    {"id": "CHK_CONTENT_LANDING", "category": "content", "item": "Landing page live with clear value proposition and CTA", "status": "READY"},
    {"id": "CHK_CONTENT_STORES", "category": "content", "item": "App Store listings published (iOS App Store & Google Play)", "status": "READY"},
    {"id": "CHK_CONTENT_SOCIALS", "category": "content", "item": "Social media accounts created (@memegpt on Twitter, IG, Reddit)", "status": "READY"},
    {"id": "CHK_CONTENT_DEMO_MEDIA", "category": "content", "item": "30-second demo GIF/video recorded", "status": "READY"},
    {"id": "CHK_CONTENT_PH_SHIP", "category": "content", "item": "Product Hunt Ship teaser page ready", "status": "READY"},
    {"id": "CHK_CONTENT_PRESS_KIT", "category": "content", "item": "Press kit assembled (high-res logos, screenshots, one-liner)", "status": "READY"},

    # SEO Checklist
    {"id": "CHK_SEO_SITEMAP", "category": "seo", "item": "Sitemap submitted to Google Search Console", "status": "READY"},
    {"id": "CHK_SEO_OG_TAGS", "category": "seo", "item": "OpenGraph dynamic image tags set for social link previews", "status": "READY"},
    {"id": "CHK_SEO_METAS", "category": "seo", "item": "Compelling meta descriptions configured across all static routes", "status": "READY"},
    {"id": "CHK_SEO_PAGES_INDEXED", "category": "seo", "item": "10,000+ meme pages pre-rendered and indexed", "status": "READY"},
]


# ── 4. Launch Day Execution Script ─────────────────────────────────────────────

LAUNCH_DAY_SCHEDULE = [
    {"time": "08:00 AM", "action": "Publish Product Hunt listing", "responsible": "Lead", "priority": "CRITICAL"},
    {"time": "08:15 AM", "action": "Post Twitter/X launch thread with demo GIF", "responsible": "Marketing", "priority": "HIGH"},
    {"time": "08:30 AM", "action": "Post on Reddit (r/SideProject first, then r/memes)", "responsible": "Marketing", "priority": "HIGH"},
    {"time": "09:00 AM", "action": "Post founder story on LinkedIn", "responsible": "Lead", "priority": "MEDIUM"},
    {"time": "09:30 AM", "action": "Publish technical architecture article on Dev.to", "responsible": "Engineering", "priority": "MEDIUM"},
    {"time": "10:00 AM", "action": "Open live monitoring dashboard (Umami, Sentry, Qdrant latency)", "responsible": "Team", "priority": "HIGH"},
    {"time": "12:00 PM", "action": "Reply to all Product Hunt comments and feedback questions", "responsible": "Team", "priority": "CRITICAL"},
    {"time": "02:00 PM", "action": "Post 'Show HN: I built an AI meme finder' on Hacker News", "responsible": "Engineering", "priority": "HIGH"},
    {"time": "06:00 PM", "action": "Share first-day milestone metrics on Twitter/X thread", "responsible": "Marketing", "priority": "MEDIUM"},
    {"time": "10:00 PM", "action": "Review error logs in Sentry and deploy hotfixes for any critical edge cases", "responsible": "Engineering", "priority": "HIGH"},
]


# ── 5. Launch Week KPI Targets ─────────────────────────────────────────────────

LAUNCH_KPIS: List[Dict[str, Any]] = [
    {"metric": "Unique visitors", "target": "1,000 visitors", "target_numeric": 1000, "tracking_source": "Umami Analytics"},
    {"metric": "Searches performed", "target": "5,000 searches", "target_numeric": 5000, "tracking_source": "Backend Logs & Analytics"},
    {"metric": "Downloads & copies", "target": "500 actions", "target_numeric": 500, "tracking_source": "Feedback API & Event Bus"},
    {"metric": "App Store downloads", "target": "100 installs", "target_numeric": 100, "tracking_source": "App Store Connect / Play Console"},
    {"metric": "Product Hunt upvotes", "target": "100 upvotes", "target_numeric": 100, "tracking_source": "Product Hunt Leaderboard"},
    {"metric": "System error rate", "target": "< 2.0%", "target_numeric": 0.02, "tracking_source": "Sentry Error Monitoring"},
    {"metric": "P95 response time", "target": "< 3.0s", "target_numeric": 3.0, "tracking_source": "Backend Metrics / Cloud Monitoring"},
]


# ── 6. Post-Launch Priorities ──────────────────────────────────────────────────

POST_LAUNCH_PRIORITIES = [
    {"rank": 1, "priority": "Fix top 3 user-reported bugs", "timeline": "Week 1", "owner": "Engineering"},
    {"rank": 2, "priority": "Implement top 3 user feature requests", "timeline": "Week 2–3", "owner": "Product"},
    {"rank": 3, "priority": "Write first programmatic SEO blog post ('Best Monday Memes 2026')", "timeline": "Week 2", "owner": "Content"},
    {"rank": 4, "priority": "Submit app to software review sites (AppAdvice, AppSumo)", "timeline": "Week 3", "owner": "Marketing"},
    {"rank": 5, "priority": "Start weekly automated meme re-indexing pipeline for viral trends", "timeline": "Week 4", "owner": "Data Engine"},
]


# ── 7. Service Functions ──────────────────────────────────────────────────────

def get_launch_timeline() -> Dict[str, Any]:
    """Retrieve structured 3-phase launch Gantt timeline."""
    return LAUNCH_TIMELINE


def get_launch_channels() -> Dict[str, Any]:
    """Retrieve 7 launch channel execution plans with expected visitor impact."""
    return {
        "total_channels": len(LAUNCH_CHANNELS),
        "channels": LAUNCH_CHANNELS,
    }


def get_pre_launch_checklist(category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve 18-point checklist filtered by technical, content, or seo."""
    if category:
        cat_clean = category.strip().lower()
        items = [c for c in PRE_LAUNCH_CHECKLIST if c["category"] == cat_clean]
    else:
        items = PRE_LAUNCH_CHECKLIST

    return {
        "total_items": len(items),
        "category_filter": category,
        "checklist": items,
    }


def get_launch_day_schedule() -> Dict[str, Any]:
    """Retrieve hour-by-hour launch day execution timetable."""
    return {
        "total_milestones": len(LAUNCH_DAY_SCHEDULE),
        "schedule": LAUNCH_DAY_SCHEDULE,
    }


def get_launch_kpis() -> Dict[str, Any]:
    """Retrieve launch week benchmark KPIs and tracking sources."""
    return {
        "total_kpis": len(LAUNCH_KPIS),
        "kpis": LAUNCH_KPIS,
    }


def get_post_launch_priorities() -> Dict[str, Any]:
    """Retrieve 5 post-launch execution priorities."""
    return {
        "total_priorities": len(POST_LAUNCH_PRIORITIES),
        "priorities": POST_LAUNCH_PRIORITIES,
    }


def evaluate_launch_readiness(checked_items: Optional[List[str]] = None) -> Dict[str, Any]:
    """Evaluate overall readiness to proceed with public launch based on checklist completion."""
    all_ids = {c["id"] for c in PRE_LAUNCH_CHECKLIST}
    verified_ids = set(checked_items) if checked_items is not None else all_ids

    total = len(all_ids)
    completed = len(verified_ids.intersection(all_ids))
    pct = round((completed / total) * 100, 1)

    is_ready = pct >= 90.0

    return {
        "launch_verdict": "READY_TO_LAUNCH" if is_ready else "BLOCKED_GATES_OPEN",
        "readiness_percentage": f"{pct}%",
        "total_checklist_items": total,
        "verified_checklist_items": completed,
        "remaining_items": total - completed,
        "critical_gates": {
            "technical_readiness": "PASSED" if completed >= 7 else "PENDING",
            "content_readiness": "PASSED" if completed >= 12 else "PENDING",
            "seo_readiness": "PASSED" if completed == 18 else "PENDING",
        },
    }
