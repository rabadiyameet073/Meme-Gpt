"""Daily maintenance jobs for MemeGPT.

Specification: 03_Backend/Background_Jobs.md § Scheduled Jobs (GitHub Actions Cron):

    | Analytics aggregation | Daily 3:00 UTC | ~2 min | Aggregate search logs |
    | Cache warm-up         | Daily 5:00 UTC | ~5 min | Pre-cache top queries |

Both callables already live in `app.core.jobs`, but they were only reachable
from the admin endpoints in `api/v1/auth.py`. The documented GitHub Actions
schedules therefore had nothing to invoke, so neither job ever ran on a timer.

Usage:
    python scripts/run_maintenance_job.py analytics
    python scripts/run_maintenance_job.py warm-cache
"""

import json
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.jobs import aggregate_analytics_task, warm_up_cache_task  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.cron.maintenance")

JOBS = {
    "analytics": aggregate_analytics_task,
    "warm-cache": warm_up_cache_task,
}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in JOBS:
        print(f"usage: {Path(__file__).name} {{{'|'.join(JOBS)}}}", file=sys.stderr)
        return 2

    name = argv[0]
    logger.info("maintenance_job_started: %s", name)
    result = JOBS[name]()

    print(f"[{name}] " + json.dumps(result, indent=2, default=str))

    if isinstance(result, dict) and result.get("status") == "error":
        logger.error("maintenance_job_failed: %s error=%s", name, result.get("message"))
        return 1

    logger.info("maintenance_job_completed: %s", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
