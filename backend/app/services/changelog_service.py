"""Changelog and Version History Service for MemeGPT.
Specification: 17_Appendix/Changelog.md

Covers:
- Semantic Versioning (SemVer) release history:
  1. v1.0.0 — Initial Release (Released 2026-01-15: Features, Architecture, Deployment)
  2. v1.1.0 — Polish & Mobile (Planned)
  3. v1.2.0 — Growth (Planned)
  4. v2.0.0 — Scale (Planned)
- Release queries by version, status, and latest
- Changelog full-text search engine
- Semantic version comparison and upgrade path evaluator
"""

from typing import Any, Dict, List, Optional


# ── Changelog Release Database ────────────────────────────────────────────────

CHANGELOG_RELEASES: List[Dict[str, Any]] = [
    {
        "version": "v1.0.0",
        "title": "v1.0.0 — Initial Release",
        "release_date": "2026-01-15",
        "status": "RELEASED",
        "major": 1,
        "minor": 0,
        "patch": 0,
        "sections": {
            "features": [
                "Smart meme search with natural language input",
                "AI-powered intent parsing (Groq Llama 3.1 8B)",
                "Emotion detection (DistilRoBERTa)",
                "Semantic vector search (MiniLM + Qdrant)",
                "Multi-format support (GIF, PNG, MP4)",
                "One-click copy to clipboard",
                "One-click download",
                "Trending memes page",
                "User feedback (thumbs up/down)",
                "Dark mode UI",
            ],
            "architecture": [
                "FastAPI backend (Python 3.11)",
                "React frontend (Vite)",
                "SQLite database (Prisma ORM)",
                "MiniLM text embeddings (384-dim)",
                "Rule engine + semantic scoring",
            ],
            "deployment": [
                "Frontend: Vercel",
                "Backend: Render.com",
                "Vector DB: Qdrant Cloud",
                "Media: Cloudflare R2",
            ],
        },
    },
    {
        "version": "v1.1.0",
        "title": "v1.1.0 — Polish & Mobile",
        "release_date": "Planned (Q1 2026)",
        "status": "PLANNED",
        "major": 1,
        "minor": 1,
        "patch": 0,
        "sections": {
            "planned": [
                "React Native mobile app (Expo SDK 51)",
                "Favorites and collections management",
                "Improved search quality with CLIP image embeddings",
                "Enhanced loading states and micro-animations",
                "App Store submission (iOS App Store + Google Play)",
            ],
        },
    },
    {
        "version": "v1.2.0",
        "title": "v1.2.0 — Growth",
        "release_date": "Planned (Q2 2026)",
        "status": "PLANNED",
        "major": 1,
        "minor": 2,
        "patch": 0,
        "sections": {
            "planned": [
                "10,000+ individual meme programmatic SEO pages",
                "Public developer REST API with free tier",
                "Discord bot integration",
                "Telegram bot integration",
                "Chrome extension for in-browser meme search",
            ],
        },
    },
    {
        "version": "v2.0.0",
        "title": "v2.0.0 — Scale",
        "release_date": "Planned (Q3 2026)",
        "status": "PLANNED",
        "major": 2,
        "minor": 0,
        "patch": 0,
        "sections": {
            "planned": [
                "25,000+ curated meme database",
                "Multi-language support (Hindi, Spanish, Portuguese)",
                "Pro tier subscription ($5/month)",
                "Fine-tuned domain embedding model",
                "Personalized search re-ranking",
                "Team workspaces and collaborative meme collections",
            ],
        },
    },
]


# ── Service Functions ──────────────────────────────────────────────────────────

def get_all_releases(status: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all changelog releases or filter by status ('RELEASED' or 'PLANNED')."""
    if status:
        status_clean = status.strip().upper()
        items = [r for r in CHANGELOG_RELEASES if r["status"] == status_clean]
    else:
        items = CHANGELOG_RELEASES

    return {
        "total_releases": len(items),
        "status_filter": status,
        "releases": items,
    }


def get_release_by_version(version: str) -> Optional[Dict[str, Any]]:
    """Retrieve release details by version string (e.g. 'v1.0.0' or '1.0.0')."""
    clean_v = version.strip().lower()
    if not clean_v.startswith("v"):
        clean_v = f"v{clean_v}"

    for r in CHANGELOG_RELEASES:
        if r["version"].lower() == clean_v:
            return r
    return None


def get_latest_release() -> Dict[str, Any]:
    """Retrieve the most recent released version."""
    released = [r for r in CHANGELOG_RELEASES if r["status"] == "RELEASED"]
    latest = released[0] if released else CHANGELOG_RELEASES[0]
    return {
        "latest_version": latest["version"],
        "release_date": latest["release_date"],
        "details": latest,
    }


def search_changelog(query: str) -> Dict[str, Any]:
    """Full-text search across all changelog items, feature bullets, and architecture specs."""
    q_lower = query.strip().lower()
    matches = []

    for r in CHANGELOG_RELEASES:
        release_matches = []
        for sec_name, items in r.get("sections", {}).items():
            for item in items:
                if q_lower in item.lower():
                    release_matches.append({"section": sec_name, "item": item})

        if release_matches or q_lower in r["title"].lower() or q_lower in r["version"].lower():
            matches.append({
                "version": r["version"],
                "status": r["status"],
                "matched_items": release_matches,
            })

    return {
        "query": query,
        "total_matching_releases": len(matches),
        "matches": matches,
    }


def get_changelog_summary() -> Dict[str, Any]:
    """Retrieve summary counts across all versions, total feature additions, and roadmap milestones."""
    total_features = 0
    total_planned = 0

    for r in CHANGELOG_RELEASES:
        for sec_name, items in r.get("sections", {}).items():
            if sec_name == "features":
                total_features += len(items)
            elif sec_name == "planned":
                total_planned += len(items)

    return {
        "total_tracked_releases": len(CHANGELOG_RELEASES),
        "released_versions_count": sum(1 for r in CHANGELOG_RELEASES if r["status"] == "RELEASED"),
        "planned_versions_count": sum(1 for r in CHANGELOG_RELEASES if r["status"] == "PLANNED"),
        "initial_release_features_count": total_features,
        "future_roadmap_milestones_count": total_planned,
        "semver_scheme": "MAJOR.MINOR.PATCH",
    }


def evaluate_version_upgrade(current_version: str, target_version: str) -> Dict[str, Any]:
    """Evaluate SemVer upgrade path and list all intervening changes and features."""
    curr = get_release_by_version(current_version)
    target = get_release_by_version(target_version)

    if not curr:
        return {"error": f"Current version '{current_version}' not found."}
    if not target:
        return {"error": f"Target version '{target_version}' not found."}

    # Determine changes between current and target
    intervening = []
    for r in CHANGELOG_RELEASES:
        if (r["major"] > curr["major"]) or (r["major"] == curr["major"] and r["minor"] > curr["minor"]):
            if (r["major"] < target["major"]) or (r["major"] == target["major"] and r["minor"] <= target["minor"]):
                intervening.append(r)

    is_breaking = target["major"] > curr["major"]

    return {
        "current_version": curr["version"],
        "target_version": target["version"],
        "is_major_breaking_upgrade": is_breaking,
        "upgrade_type": "MAJOR" if is_breaking else ("MINOR" if target["minor"] > curr["minor"] else "PATCH"),
        "intervening_releases_count": len(intervening),
        "intervening_releases": [r["version"] for r in intervening],
    }
