"""
Weekly Re-ranker Calibration Job
================================

Specification: completion_fixes/15_Non_Functional_Requirements.md §4 Model
Retraining Pipeline — "Leveraging user clicks and thumbs up/down to
continuously optimize ranking."

The learning loop is closed in two halves:

1. `scripts/sync_popularity_scores.py` (daily) folds the trailing `feedback`
   rows into `memes.popularity_score` through
   `rerank_service.calculate_popularity_score`.
2. This job (weekly) *measures* whether that closed loop actually ranks the way
   users vote. It pairs memes that collected net thumbs-up against memes that
   collected net thumbs-down, then counts how often the stored ranking puts the
   liked meme first. Below 50% concordance the score is anti-correlated with
   user preference and the job fails the workflow so the regression is visible.

The previous version overwrote `memes.popularity_score` with a Laplace-smoothed
upvote ratio. That raced the daily job for the same column with a different
formula, so whichever ran last silently won. This job no longer writes scores —
it reports on them.

Exit codes: 0 = healthy or not enough votes yet, 1 = anti-correlated ranking.
"""

import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database import Feedback, Meme, SessionLocal  # noqa: E402
from app.services.rerank_service import COMPOSITE_WEIGHTS  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.jobs.rerank_calibration")

# Fewer than this many decisive votes and concordance is noise, not a signal.
MIN_DECISIVE_VOTES = 10
REPORT_PATH = ROOT_DIR / "data" / "reports" / "rerank_calibration.json"


def _vote_tally(db, window_days: int) -> dict[str, dict[str, int]]:
    """Count thumbs-up / thumbs-down per meme inside the window."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    rows = (
        db.query(Feedback.meme_id, Feedback.action)
        .filter(
            Feedback.created_at >= cutoff,
            Feedback.action.in_(("thumbs_up", "thumbs_down")),
        )
        .all()
    )
    tally: dict[str, dict[str, int]] = {}
    for meme_id, action in rows:
        entry = tally.setdefault(meme_id, {"up": 0, "down": 0})
        entry["up" if action == "thumbs_up" else "down"] += 1
    return tally


def _concordance(liked: list[float], disliked: list[float]) -> tuple[int, int]:
    """Count how often `liked` outranks `disliked`, pair by pair.

    Pairs where both sides score identically carry no information and are
    skipped, so the denominator only counts decisive comparisons.
    """
    correct = 0
    decisive = 0
    for good in liked:
        for bad in disliked:
            if good == bad:
                continue
            decisive += 1
            if good > bad:
                correct += 1
    return correct, decisive


def calibrate(window_days: int = 7) -> dict:
    db = SessionLocal()
    try:
        tally = _vote_tally(db, window_days)
        if not tally:
            return {
                "status": "insufficient_signal",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "window_days": window_days,
                "voted_memes": 0,
                "liked_memes": 0,
                "disliked_memes": 0,
                "decisive_pairs": 0,
                "correct_pairs": 0,
                "concordance": None,
                "composite_weights": dict(COMPOSITE_WEIGHTS),
                "message": "no thumbs-up/thumbs-down feedback in window",
            }

        memes = db.query(Meme).filter(Meme.id.in_(list(tally.keys()))).all()
        liked: list[float] = []
        disliked: list[float] = []
        for meme in memes:
            counts = tally[meme.id]
            net = counts["up"] - counts["down"]
            if net > 0:
                liked.append(float(meme.popularity_score or 0.0))
            elif net < 0:
                disliked.append(float(meme.popularity_score or 0.0))

        correct, decisive = _concordance(liked, disliked)
        concordance = round(correct / decisive, 4) if decisive else None

        report = {
            "status": "ok",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "window_days": window_days,
            "voted_memes": len(tally),
            "liked_memes": len(liked),
            "disliked_memes": len(disliked),
            "decisive_pairs": decisive,
            "correct_pairs": correct,
            "concordance": concordance,
            "composite_weights": dict(COMPOSITE_WEIGHTS),
        }

        if decisive < MIN_DECISIVE_VOTES:
            report["status"] = "insufficient_signal"
            report["message"] = (
                f"{decisive} decisive pairs, need {MIN_DECISIVE_VOTES} to judge"
            )
        elif concordance is not None and concordance < 0.5:
            report["status"] = "anti_correlated"
            report["message"] = (
                "stored popularity_score ranks disliked memes above liked ones; "
                "the feedback loop is inverted"
            )

        return report
    finally:
        db.close()


def main(argv=None) -> int:
    window_days = 7
    if argv:
        for i, arg in enumerate(argv):
            if arg == "--window-days" and i + 1 < len(argv):
                window_days = int(argv[i + 1])

    window_days = max(1, window_days)

    try:
        report = calibrate(window_days=window_days)
    except Exception as exc:  # noqa: BLE001 - a cron step must report, not traceback
        # A missing/unmigrated schema (fresh checkout, stale memegpt.db) used to
        # escape as a raw SQLAlchemy traceback, which GitHub Actions renders as
        # an opaque "Process completed with exit code 1". Report the same shape
        # the sibling jobs use so the workflow log names the actual cause.
        logger.error("rerank_calibration_error: %s", exc)
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": str(exc),
                    "window_days": window_days,
                    "hint": (
                        "the feedback table is unreadable — start the API once "
                        "(Base.metadata.create_all) or run the migrations "
                        "before scheduling this job"
                    ),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT_DIR)}")
    print(json.dumps(report, indent=2))

    if report["status"] == "anti_correlated":
        logger.error("rerank_calibration_failed: %s", report["message"])
        return 1
    if report["status"] == "insufficient_signal":
        logger.info("rerank_calibration_skipped: %s", report["message"])
        return 0

    logger.info("rerank_calibration_ok: concordance=%s", report["concordance"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
