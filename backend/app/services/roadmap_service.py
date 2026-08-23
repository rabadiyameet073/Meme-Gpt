"""Product Roadmap & Milestone Governance Service for MemeGPT.
Specification: 13_Project_Management/Roadmap.md

Covers:
- 4 Product Lifecycle Phases (Phase 1 MVP, Phase 2 Growth, Phase 3 Scale, Phase 4 Expand)
- Detailed Feature Inventories with Priorities (P0, P1, P2) and Timelines
- Mermaid Gantt Chart Specification
- Success Metrics Benchmarks by Phase
- Phase Readiness Evaluator
"""

from typing import Any, Dict, List, Optional


# ── 1. 4 Product Roadmap Phases Catalog ────────────────────────────────────────

ROADMAP_PHASES = [
    {
        "phase_id": 1,
        "name": "Phase 1: MVP",
        "duration": "Months 1–4",
        "timeline": "2026-01 to 2026-04",
        "status": "COMPLETED",
        "success_metrics": {
            "dau_target": "1,000 DAU",
            "feedback_target": "75% positive feedback",
            "latency_p95": "P95 < 3.0s",
            "cost_target": "$0/month",
        },
        "features": [
            {"feature": "AI-powered meme search", "priority": "P0", "status": "Done", "completed": True, "details": "Groq + MiniLM + Qdrant pipeline"},
            {"feature": "Emotion detection", "priority": "P0", "status": "Done", "completed": True, "details": "DistilRoBERTa, 7 emotions"},
            {"feature": "Multi-format support", "priority": "P0", "status": "Done", "completed": True, "details": "GIF, PNG, MP4, WebP"},
            {"feature": "Copy to clipboard", "priority": "P1", "status": "Done", "completed": True, "details": "Clipboard API"},
            {"feature": "Download", "priority": "P1", "status": "Done", "completed": True, "details": "CDN redirect"},
            {"feature": "Suggestion chips", "priority": "P1", "status": "Done", "completed": True, "details": "Quick search tags"},
            {"feature": "Trending memes", "priority": "P1", "status": "Done", "completed": True, "details": "Hourly refresh, 6 categories"},
            {"feature": "Feedback (👍/👎)", "priority": "P1", "status": "Done", "completed": True, "details": "Weight-based scoring"},
            {"feature": "SEO meme pages", "priority": "P2", "status": "Done", "completed": True, "details": "SSR with Next.js 14"},
            {"feature": "Responsive web app", "priority": "P0", "status": "Done", "completed": True, "details": "Desktop + mobile"},
        ],
    },
    {
        "phase_id": 2,
        "name": "Phase 2: Growth",
        "duration": "Months 5–8",
        "timeline": "2026-05 to 2026-08",
        "status": "IN_PROGRESS",
        "success_metrics": {
            "dau_target": "5,000 DAU",
            "api_keys_issued": "100 API keys",
            "error_rate_target": "< 2% error rate",
            "monthly_cost": "~$42/month",
        },
        "features": [
            {"feature": "User accounts (OAuth)", "priority": "P0", "status": "Planned", "completed": False, "details": "Google/GitHub login via NextAuth"},
            {"feature": "Developer API keys", "priority": "P0", "status": "Planned", "completed": False, "details": "API key registration, tier management"},
            {"feature": "Saved favorites", "priority": "P1", "status": "Planned", "completed": False, "details": "Save memes to personal library"},
            {"feature": "Search history", "priority": "P1", "status": "Planned", "completed": False, "details": "View last 50 searches"},
            {"feature": "Analytics dashboard", "priority": "P1", "status": "Planned", "completed": False, "details": "Usage charts, popular queries"},
            {"feature": "Content moderation", "priority": "P1", "status": "Planned", "completed": False, "details": "NSFW detection, user reports"},
            {"feature": "Webhooks", "priority": "P2", "status": "Planned", "completed": False, "details": "Notify on trending changes"},
        ],
    },
    {
        "phase_id": 3,
        "name": "Phase 3: Scale",
        "duration": "Months 9–12",
        "timeline": "2026-09 to 2026-12",
        "status": "PLANNED",
        "success_metrics": {
            "dau_target": "10,000 DAU",
            "mobile_downloads": "1,000 mobile downloads",
            "latency_p95": "P95 < 2.0s",
            "monthly_cost": "~$200/month",
        },
        "features": [
            {"feature": "React Native mobile app", "priority": "P0", "status": "Planned", "completed": False, "details": "iOS + Android via Expo"},
            {"feature": "Chat refinement", "priority": "P1", "status": "Planned", "completed": False, "details": "'Something more sarcastic' follow-ups"},
            {"feature": "Collections", "priority": "P1", "status": "Planned", "completed": False, "details": "Create/share meme collections"},
            {"feature": "Image-based search", "priority": "P2", "status": "Planned", "completed": False, "details": "Upload image -> find similar memes"},
            {"feature": "Personalization", "priority": "P2", "status": "Planned", "completed": False, "details": "Rank based on user's past likes"},
            {"feature": "Multi-language UI", "priority": "P2", "status": "Planned", "completed": False, "details": "Spanish, Hindi, Portuguese"},
        ],
    },
    {
        "phase_id": 4,
        "name": "Phase 4: Expand",
        "duration": "Year 2",
        "timeline": "2027-01 to 2027-09",
        "status": "PLANNED",
        "success_metrics": {
            "dau_target": "50,000 DAU",
            "mrr_target": "$1,000 MRR",
            "uptime_target": "99.9% uptime",
            "monthly_cost": "~$500/month",
        },
        "features": [
            {"feature": "Meme creation tool", "priority": "P1", "status": "Planned", "completed": False, "details": "Text overlay, template library"},
            {"feature": "Premium tier ($9/mo)", "priority": "P0", "status": "Planned", "completed": False, "details": "Unlimited searches, priority API"},
            {"feature": "Enterprise API", "priority": "P1", "status": "Planned", "completed": False, "details": "SLA, dedicated support, bulk pricing"},
            {"feature": "Real-time meme tracking", "priority": "P2", "status": "Planned", "completed": False, "details": "Live trending from Twitter/Reddit"},
            {"feature": "AI meme generation", "priority": "P2", "status": "Planned", "completed": False, "details": "Generate new memes from prompts"},
        ],
    },
]


def get_roadmap_phases() -> Dict[str, Any]:
    """Return all 4 product roadmap phases with feature inventory."""
    total_features = sum(len(p["features"]) for p in ROADMAP_PHASES)
    completed_features = sum(sum(1 for f in p["features"] if f["completed"]) for p in ROADMAP_PHASES)

    return {
        "total_phases": len(ROADMAP_PHASES),
        "total_features": total_features,
        "completed_features": completed_features,
        "progress_percentage": f"{round((completed_features / total_features) * 100, 1)}%",
        "phases": ROADMAP_PHASES,
    }


def get_roadmap_phase_by_id(phase_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve detailed feature breakdown for a single phase (1 to 4)."""
    phase = next((p for p in ROADMAP_PHASES if p["phase_id"] == phase_id), None)
    if not phase:
        return None

    total = len(phase["features"])
    done = sum(1 for f in phase["features"] if f["completed"])

    return {
        **phase,
        "total_features": total,
        "completed_features": done,
        "progress_percentage": round((done / total) * 100, 1),
    }


# ── 2. Gantt Chart Specification ───────────────────────────────────────────────

GANTT_CHART_SPEC = {
    "title": "MemeGPT Product Roadmap",
    "date_format": "YYYY-MM",
    "sections": [
        {
            "section": "Phase 1 — MVP",
            "items": [
                {"name": "AI Meme Search", "status": "done", "id": "p1a", "start": "2026-01", "end": "2026-02"},
                {"name": "Multi-Format Support", "status": "done", "id": "p1b", "start": "2026-02", "end": "2026-03"},
                {"name": "Trending + Feedback", "status": "done", "id": "p1c", "start": "2026-03", "end": "2026-04"},
                {"name": "Web App Launch", "status": "milestone", "id": "p1m", "start": "2026-04", "end": "0d"},
            ],
        },
        {
            "section": "Phase 2 — Growth",
            "items": [
                {"name": "User Accounts", "status": "active", "id": "p2a", "start": "2026-05", "end": "2026-06"},
                {"name": "Developer API + Keys", "status": "active", "id": "p2b", "start": "2026-06", "end": "2026-07"},
                {"name": "Analytics Dashboard", "status": "active", "id": "p2c", "start": "2026-07", "end": "2026-08"},
            ],
        },
        {
            "section": "Phase 3 — Scale",
            "items": [
                {"name": "React Native App", "status": "future", "id": "p3a", "start": "2026-09", "end": "2026-10"},
                {"name": "Chat Refinement", "status": "future", "id": "p3b", "start": "2026-10", "end": "2026-11"},
                {"name": "Collections + Favorites", "status": "future", "id": "p3c", "start": "2026-11", "end": "2026-12"},
            ],
        },
        {
            "section": "Phase 4 — Expand",
            "items": [
                {"name": "Meme Creation", "status": "future", "id": "p4a", "start": "2027-01", "end": "2027-03"},
                {"name": "Premium Tier", "status": "future", "id": "p4b", "start": "2027-03", "end": "2027-06"},
                {"name": "Enterprise API", "status": "future", "id": "p4c", "start": "2027-06", "end": "2027-09"},
            ],
        },
    ],
}


def get_roadmap_gantt_chart() -> Dict[str, Any]:
    """Return the Gantt chart schedule metadata."""
    return GANTT_CHART_SPEC


# ── 3. Success Metrics Matrix ──────────────────────────────────────────────────

def get_success_metrics_by_phase() -> Dict[str, Any]:
    """Return success metrics targets across all 4 roadmap phases."""
    return {
        "total_phases": len(ROADMAP_PHASES),
        "phases_metrics": [
            {
                "phase_id": p["phase_id"],
                "phase_name": p["name"],
                "metrics": p["success_metrics"],
            }
            for p in ROADMAP_PHASES
        ],
    }


# ── 4. Phase Readiness Evaluator ───────────────────────────────────────────────

def evaluate_phase_readiness(phase_id: int) -> Dict[str, Any]:
    """Evaluate completion readiness and feature delivery for a specific roadmap phase."""
    phase = get_roadmap_phase_by_id(phase_id)
    if not phase:
        return {
            "success": False,
            "error": f"Invalid phase ID '{phase_id}'. Must be 1 to 4.",
        }

    total = phase["total_features"]
    done = phase["completed_features"]
    is_ready = done == total

    return {
        "success": True,
        "phase_id": phase_id,
        "phase_name": phase["name"],
        "is_ready_for_next_phase": is_ready,
        "status": "PHASE_COMPLETE" if is_ready else "PHASE_IN_DEVELOPMENT",
        "total_features": total,
        "completed_features": done,
        "pending_features": total - done,
        "progress_percentage": f"{phase['progress_percentage']}%",
    }
