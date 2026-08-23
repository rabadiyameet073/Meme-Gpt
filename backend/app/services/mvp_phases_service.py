"""MVP Phases & Detailed Sprint Planning Service for MemeGPT.
Specification: 13_Project_Management/MVP_Phases.md

Covers:
- 4 Sprints Breakdown across 8 Weeks (Backend Foundation, AI Integration, Frontend + Deploy, Polish + Feedback)
- 30 Sprint Tasks with Owners, Deliverables, and Completion Status
- 6 Definition of Done (DoD) Criteria & Validation Engine
- MVP Velocity and Milestone Completion Evaluator
"""

from typing import Any, Dict, List, Optional


# ── 1. Sprint Breakdown Catalog ────────────────────────────────────────────────

SPRINT_BREAKDOWN = [
    {
        "sprint_id": 1,
        "name": "Sprint 1: Backend Foundation",
        "weeks": "Weeks 1–2",
        "theme": "Backend Foundation & Core REST Services",
        "tasks": [
            {"task": "FastAPI app scaffold", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "main.py, config.py"},
            {"task": "Database schema (Prisma)", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "schema.prisma"},
            {"task": "Meme seeder script", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "seed_memes.py"},
            {"task": "Health endpoint", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "GET /health"},
            {"task": "Search endpoint", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "POST /search"},
            {"task": "Meme CRUD endpoints", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "GET /memes, GET /memes/{id}"},
            {"task": "Rule engine scoring", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "rule_engine.py"},
            {"task": "CORS + basic middleware", "status": "Done", "completed": True, "owner": "Backend", "deliverable": "Middleware stack"},
        ],
    },
    {
        "sprint_id": 2,
        "name": "Sprint 2: AI Integration",
        "weeks": "Weeks 3–4",
        "theme": "AI & Multimodal Search Pipeline",
        "tasks": [
            {"task": "MiniLM embedding generation", "status": "Done", "completed": True, "owner": "ML", "deliverable": "semantic_search.py"},
            {"task": "Semantic search implementation", "status": "Done", "completed": True, "owner": "ML", "deliverable": "Cosine similarity search"},
            {"task": "Groq LLM intent parsing", "status": "Done", "completed": True, "owner": "ML", "deliverable": "Intent JSON extraction"},
            {"task": "Emotion detection", "status": "Done", "completed": True, "owner": "ML", "deliverable": "DistilRoBERTa pipeline"},
            {"task": "Combined scoring pipeline", "status": "Done", "completed": True, "owner": "ML", "deliverable": "meme_matcher.py"},
            {"task": "Offline indexing scripts", "status": "Done", "completed": True, "owner": "ML", "deliverable": "scripts/ directory"},
        ],
    },
    {
        "sprint_id": 3,
        "name": "Sprint 3: Frontend + Deploy",
        "weeks": "Weeks 5–6",
        "theme": "Client UI & Production Deployment",
        "tasks": [
            {"task": "React app scaffold (Vite)", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "Project structure"},
            {"task": "Search input component", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "SearchInput.tsx"},
            {"task": "Results grid + MemeCard", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "ResultsGrid.tsx, MemeCard.tsx"},
            {"task": "Copy/download functionality", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "Clipboard + download"},
            {"task": "Dark mode design system", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "CSS design tokens"},
            {"task": "Format selector (GIF/PNG/MP4)", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "FormatSelector.tsx"},
            {"task": "Vercel deployment", "status": "Done", "completed": True, "owner": "DevOps", "deliverable": "memegpt.com live"},
            {"task": "Render/Railway deployment", "status": "Done", "completed": True, "owner": "DevOps", "deliverable": "api.memegpt.com live"},
        ],
    },
    {
        "sprint_id": 4,
        "name": "Sprint 4: Polish + Feedback",
        "weeks": "Weeks 7–8",
        "theme": "Product Polish, Telemetry & User Feedback",
        "tasks": [
            {"task": "Trending endpoint + UI", "status": "Done", "completed": True, "owner": "Fullstack", "deliverable": "/trending page"},
            {"task": "Favorites (localStorage)", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "Save/remove memes"},
            {"task": "Feedback voting (👍/👎)", "status": "Done", "completed": True, "owner": "Fullstack", "deliverable": "Vote UI + API"},
            {"task": "Loading states + skeletons", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "Shimmer animations"},
            {"task": "Error states + fallbacks", "status": "Done", "completed": True, "owner": "Frontend", "deliverable": "Error boundaries"},
            {"task": "UptimeRobot monitoring", "status": "Done", "completed": True, "owner": "DevOps", "deliverable": "Health pings"},
            {"task": "Sentry error tracking", "status": "Done", "completed": True, "owner": "DevOps", "deliverable": "Exception capture"},
            {"task": "Documentation v1", "status": "Done", "completed": True, "owner": "Docs", "deliverable": "This knowledge base"},
        ],
    },
]


def get_all_sprints() -> Dict[str, Any]:
    """Return all 4 sprint roadmaps with task completion stats."""
    total_tasks = sum(len(s["tasks"]) for s in SPRINT_BREAKDOWN)
    completed_tasks = sum(sum(1 for t in s["tasks"] if t["completed"]) for s in SPRINT_BREAKDOWN)
    
    return {
        "total_sprints": len(SPRINT_BREAKDOWN),
        "total_weeks": 8,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": f"{round((completed_tasks / total_tasks) * 100, 1)}%",
        "sprints": SPRINT_BREAKDOWN,
    }


def get_sprint_by_id(sprint_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve detailed sprint task breakdown by sprint number (1 to 4)."""
    sprint = next((s for s in SPRINT_BREAKDOWN if s["sprint_id"] == sprint_id), None)
    if not sprint:
        return None

    total = len(sprint["tasks"])
    done = sum(1 for t in sprint["tasks"] if t["completed"])

    return {
        **sprint,
        "total_tasks": total,
        "completed_tasks": done,
        "progress_percentage": round((done / total) * 100, 1),
    }


# ── 2. Definition of Done (DoD) Criteria ──────────────────────────────────────

DOD_CRITERIA = [
    {
        "id": "merged_develop",
        "title": "Code is merged to develop",
        "description": "All feature branch PRs reviewed and merged into main integration branch.",
    },
    {
        "id": "tests_pass",
        "title": "All tests pass (lint + build + unit)",
        "description": "Ruff, pytest, ESLint, and Next.js/Vite builds pass with zero failures.",
    },
    {
        "id": "no_critical_bugs",
        "title": "No critical bugs",
        "description": "Zero P0/P1 blocking issues or unhandled 500 runtime exceptions.",
    },
    {
        "id": "code_reviewed",
        "title": "Code reviewed by at least 1 person",
        "description": "Pull request approved with architectural and security sign-off.",
    },
    {
        "id": "documentation_updated",
        "title": "Documentation updated if needed",
        "description": "Architecture, API specs, and Markdown knowledge bases synchronized.",
    },
    {
        "id": "staging_verified",
        "title": "Deployed to staging and manually verified",
        "description": "Smoke tests pass on staging environment prior to production release.",
    },
]


def get_definition_of_done() -> Dict[str, Any]:
    """Return the 6 standard Definition of Done checklist criteria."""
    return {
        "total_criteria": len(DOD_CRITERIA),
        "criteria": DOD_CRITERIA,
    }


def evaluate_dod_readiness(checks: Dict[str, bool]) -> Dict[str, Any]:
    """Evaluate whether a feature or task satisfies all 6 DoD criteria."""
    missing = []
    satisfied = []

    for item in DOD_CRITERIA:
        cid = item["id"]
        val = checks.get(cid, False)
        if val:
            satisfied.append(item["title"])
        else:
            missing.append(item["title"])

    all_passed = len(missing) == 0

    return {
        "is_done": all_passed,
        "status": "APPROVED_FOR_RELEASE" if all_passed else "INCOMPLETE_DOD",
        "total_criteria": len(DOD_CRITERIA),
        "passed_count": len(satisfied),
        "missing_count": len(missing),
        "satisfied_criteria": satisfied,
        "missing_criteria": missing,
    }


# ── 3. MVP Completion & Milestone Summary ──────────────────────────────────────

def get_mvp_completion_summary() -> Dict[str, Any]:
    """Return high-level milestone and velocity summary across all MVP phases."""
    sprints = SPRINT_BREAKDOWN
    total_tasks = sum(len(s["tasks"]) for s in sprints)
    completed_tasks = sum(sum(1 for t in s["tasks"] if t["completed"]) for s in sprints)

    return {
        "project": "MemeGPT MVP",
        "total_duration": "8 Weeks (4 Sprints)",
        "overall_status": "MVP_COMPLETE",
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": f"{round((completed_tasks / total_tasks) * 100, 1)}%",
        "owners_breakdown": {
            "Backend": sum(sum(1 for t in s["tasks"] if t["owner"] == "Backend") for s in sprints),
            "ML": sum(sum(1 for t in s["tasks"] if t["owner"] == "ML") for s in sprints),
            "Frontend": sum(sum(1 for t in s["tasks"] if t["owner"] == "Frontend") for s in sprints),
            "DevOps": sum(sum(1 for t in s["tasks"] if t["owner"] == "DevOps") for s in sprints),
            "Fullstack": sum(sum(1 for t in s["tasks"] if t["owner"] == "Fullstack") for s in sprints),
            "Docs": sum(sum(1 for t in s["tasks"] if t["owner"] == "Docs") for s in sprints),
        },
        "milestones": [
            {"sprint": 1, "milestone": "Backend Foundation & Search API", "status": "COMPLETED"},
            {"sprint": 2, "milestone": "AI Semantic Search & Emotion ML", "status": "COMPLETED"},
            {"sprint": 3, "milestone": "Frontend UI & Multi-Cloud Deployment", "status": "COMPLETED"},
            {"sprint": 4, "milestone": "Telemetry, Sentry, Trending & Documentation", "status": "COMPLETED"},
        ],
    }
