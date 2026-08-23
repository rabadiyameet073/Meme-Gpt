"""Risk Register & Mitigation Matrix Service for MemeGPT.
Specification: 13_Project_Management/Risk_Register.md

Covers:
- 12 Active Project, Technical, and Operational Risks
- Probability, Impact, Severity Score, and Mitigation Actions
- 4-Quadrant Risk Matrix Classification (Critical - Act Now, Monitor Closely, Mitigate, Accept)
- Severity Filtering and Live Mitigation Audit Engine
"""

from typing import Any, Dict, List, Optional


# ── 1. 12 Active Risks Catalog ─────────────────────────────────────────────────

RISK_REGISTER = [
    {
        "id": "R1",
        "risk": "Groq API becomes paid/deprecated",
        "category": "Third-Party Dependency",
        "probability": "Low",
        "probability_score": 0.2,
        "impact": "High",
        "impact_score": 0.8,
        "severity": "Medium",
        "status": "Open",
        "mitigation": "Maintain Ollama fallback, evaluate Gemini API",
        "quadrant": "Monitor Closely",
    },
    {
        "id": "R2",
        "risk": "Free tier limits exceeded",
        "category": "Infrastructure & Cost",
        "probability": "Medium",
        "probability_score": 0.5,
        "impact": "Medium",
        "impact_score": 0.5,
        "severity": "Medium",
        "status": "Open",
        "mitigation": "Usage dashboard, graceful degradation, upgrade path",
        "quadrant": "Mitigate",
    },
    {
        "id": "R3",
        "risk": "Low search quality at launch",
        "category": "AI / Core Product",
        "probability": "Medium",
        "probability_score": 0.5,
        "impact": "High",
        "impact_score": 0.8,
        "severity": "High",
        "status": "Mitigating",
        "mitigation": "Manual curation of 1K memes, test dataset, weekly evals",
        "quadrant": "Critical - Act Now",
    },
    {
        "id": "R4",
        "risk": "App store rejection",
        "category": "Compliance & Distribution",
        "probability": "Low",
        "probability_score": 0.2,
        "impact": "Medium",
        "impact_score": 0.4,
        "severity": "Low",
        "status": "Open",
        "mitigation": "Follow guidelines, no NSFW default, proper permissions",
        "quadrant": "Accept",
    },
    {
        "id": "R5",
        "risk": "Copyright/DMCA complaints",
        "category": "Legal & IP",
        "probability": "Medium",
        "probability_score": 0.5,
        "impact": "Medium",
        "impact_score": 0.5,
        "severity": "Medium",
        "status": "Open",
        "mitigation": "DMCA process, attribution, 48-hr takedown SLA",
        "quadrant": "Mitigate",
    },
    {
        "id": "R6",
        "risk": "Qdrant Cloud free tier removed",
        "category": "Third-Party Dependency",
        "probability": "Low",
        "probability_score": 0.2,
        "impact": "High",
        "impact_score": 0.7,
        "severity": "Medium",
        "status": "Open",
        "mitigation": "Docker self-hosted backup, export snapshots",
        "quadrant": "Monitor Closely",
    },
    {
        "id": "R7",
        "risk": "Poor SEO performance",
        "category": "Growth & Acquisition",
        "probability": "Medium",
        "probability_score": 0.5,
        "impact": "Low",
        "impact_score": 0.3,
        "severity": "Low",
        "status": "Open",
        "mitigation": "10K+ pages, long-tail targeting, Schema.org",
        "quadrant": "Accept",
    },
    {
        "id": "R8",
        "risk": "User data breach",
        "category": "Security & Privacy",
        "probability": "Very Low",
        "probability_score": 0.1,
        "impact": "Very High",
        "impact_score": 0.9,
        "severity": "Medium",
        "status": "Mitigated",
        "mitigation": "No PII stored, anonymous by default, HTTPS only",
        "quadrant": "Monitor Closely",
    },
    {
        "id": "R9",
        "risk": "Competitor launches similar product",
        "category": "Market & Business",
        "probability": "Medium",
        "probability_score": 0.5,
        "impact": "Medium",
        "impact_score": 0.5,
        "severity": "Medium",
        "status": "Open",
        "mitigation": "Superior AI quality, free tier, speed, developer API",
        "quadrant": "Mitigate",
    },
    {
        "id": "R10",
        "risk": "ML model accuracy degrades over time",
        "category": "AI / Core Product",
        "probability": "Low",
        "probability_score": 0.3,
        "impact": "Medium",
        "impact_score": 0.4,
        "severity": "Low",
        "status": "Open",
        "mitigation": "Weekly offline eval, A/B testing, feedback loop",
        "quadrant": "Accept",
    },
    {
        "id": "R11",
        "risk": "Render free tier cold start latency",
        "category": "Infrastructure & Hosting",
        "probability": "High",
        "probability_score": 0.7,
        "impact": "Low",
        "impact_score": 0.3,
        "severity": "Medium",
        "status": "Mitigated",
        "mitigation": "UptimeRobot pings every 5 min",
        "quadrant": "Mitigate",
    },
    {
        "id": "R12",
        "risk": "HuggingFace model downloads blocked",
        "category": "CI/CD & Deployment",
        "probability": "Low",
        "probability_score": 0.2,
        "impact": "High",
        "impact_score": 0.8,
        "severity": "Medium",
        "status": "Open",
        "mitigation": "Pre-download in Docker build, cache in CI",
        "quadrant": "Monitor Closely",
    },
]


def get_all_risks(severity: Optional[str] = None) -> Dict[str, Any]:
    """Return all 12 tracked risks, optionally filtered by severity."""
    risks = RISK_REGISTER
    if severity:
        sev_clean = severity.strip().capitalize()
        risks = [r for r in risks if r["severity"].capitalize() == sev_clean]

    return {
        "total_risks": len(risks),
        "risks": risks,
    }


def get_risk_by_id(risk_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve detailed metadata and mitigation plan for a specific risk ID (e.g. R1)."""
    normalized = risk_id.strip().upper()
    return next((r for r in RISK_REGISTER if r["id"] == normalized), None)


# ── 2. Risk Matrix & Quadrant Classification ───────────────────────────────────

def get_risk_matrix_quadrants() -> Dict[str, Any]:
    """Return risk items classified across the 4 quadrant evaluation matrix."""
    quadrants: Dict[str, List[Dict[str, Any]]] = {
        "Critical - Act Now": [],
        "Monitor Closely": [],
        "Mitigate": [],
        "Accept": [],
    }

    for r in RISK_REGISTER:
        q = r.get("quadrant", "Accept")
        if q in quadrants:
            quadrants[q].append({
                "id": r["id"],
                "risk": r["risk"],
                "coordinates": [r["probability_score"], r["impact_score"]],
                "severity": r["severity"],
                "status": r["status"],
            })

    return {
        "title": "Risk Assessment Quadrant Matrix",
        "x_axis": "Low Probability (0.0) -> High Probability (1.0)",
        "y_axis": "Low Impact (0.0) -> High Impact (1.0)",
        "quadrants": quadrants,
    }


# ── 3. Risk Summary & Mitigation Audit ─────────────────────────────────────────

def get_risk_summary_stats() -> Dict[str, Any]:
    """Return statistical distribution across risk severities and resolution statuses."""
    total = len(RISK_REGISTER)
    high_count = sum(1 for r in RISK_REGISTER if r["severity"] == "High")
    med_count = sum(1 for r in RISK_REGISTER if r["severity"] == "Medium")
    low_count = sum(1 for r in RISK_REGISTER if r["severity"] == "Low")

    mitigated = sum(1 for r in RISK_REGISTER if r["status"] == "Mitigated")
    mitigating = sum(1 for r in RISK_REGISTER if r["status"] == "Mitigating")
    open_risks = sum(1 for r in RISK_REGISTER if r["status"] == "Open")

    return {
        "total_risks": total,
        "by_severity": {
            "High": high_count,
            "Medium": med_count,
            "Low": low_count,
        },
        "by_status": {
            "Open": open_risks,
            "Mitigating": mitigating,
            "Mitigated": mitigated,
        },
        "critical_risks": [r["risk"] for r in RISK_REGISTER if r["severity"] == "High"],
    }


def audit_risk_mitigation_health() -> Dict[str, Any]:
    """Audit mitigation health across all 12 tracked risk vectors."""
    unmitigated = [r for r in RISK_REGISTER if not r.get("mitigation")]

    return {
        "status": "HEALTHY" if len(unmitigated) == 0 else "ACTION_REQUIRED",
        "total_risks_audited": len(RISK_REGISTER),
        "all_risks_have_mitigation_plan": len(unmitigated) == 0,
        "unmitigated_count": len(unmitigated),
        "active_mitigations_in_progress": sum(1 for r in RISK_REGISTER if r["status"] == "Mitigating"),
        "fully_mitigated_risks": sum(1 for r in RISK_REGISTER if r["status"] == "Mitigated"),
    }
