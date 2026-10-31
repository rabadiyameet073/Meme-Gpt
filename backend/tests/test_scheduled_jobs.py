"""
MemeGPT — Tests for the documented GitHub Actions scheduled jobs.

Specification: 03_Backend/Background_Jobs.md § Scheduled Jobs:

    | Analytics aggregation | Daily 3:00 UTC | Aggregate search logs |
    | Popularity update     | Daily 4:00 UTC | Recalculate popularity_scores |
    | Cache warm-up         | Daily 5:00 UTC | Pre-cache top queries |

Each job here used to either reference a file that did not exist or write into a
namespace nothing read, so "scheduled" was true on paper only. These tests pin
the behaviour the workflows in `.github/workflows/cron.yml` depend on.
"""

import sys
from pathlib import Path

workspace_root = str(Path(__file__).resolve().parent.parent.parent)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from app.core.cache import cache_get, make_cache_key  # noqa: E402
from app.core.jobs import warm_up_cache_task  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.services.trending_service import get_trending_catalog  # noqa: E402
from scripts import refresh_trending, run_maintenance_job, sync_popularity_scores  # noqa: E402


def test_warm_up_cache_writes_the_keys_search_reads():
    """The warm-up job must populate `search:{md5}`, not a private namespace."""
    result = warm_up_cache_task(["deploy to production on a friday"])

    assert result["status"] == "success"
    assert result["warmed_queries"] >= 1

    cached = cache_get(make_cache_key("deploy to production on a friday", "gif", False))
    assert cached is not None
    assert cached["cached"] is True


def test_warm_up_cache_defaults_to_the_suggestion_chip_corpus():
    """Without explicit queries it warms what the UI actually offers."""
    result = warm_up_cache_task()

    assert result["status"] == "success"
    # The static chip catalog alone has eight entries.
    assert result["warmed_queries"] >= 5


def test_refresh_trending_warms_the_shared_cache():
    """`refresh_trending.py` must publish the keys GET /api/v1/trending reads."""
    assert refresh_trending.run_trending_refresh() == 0

    stored = cache_get("trending:all:24h:0:20")
    assert isinstance(stored, dict)
    assert stored["data"]["category"] == "all"
    # Rankings come from the seeded corpus, not a hardcoded sample list.
    assert stored["data"]["meta"]["total_results"] >= 1
    assert stored["results"]

    # A subsequent API call is served from that warm entry.
    db = SessionLocal()
    try:
        payload = get_trending_catalog(db, category="all", period="24h", limit=20, offset=0)
    finally:
        db.close()
    assert payload["cached"] is True
    assert payload["data"]["meta"]["cached"] is True


def test_sync_popularity_scores_script_reports_success():
    """The popularity workflow invokes this entry point directly."""
    assert sync_popularity_scores.main(["--window-days", "30"]) == 0


def test_maintenance_dispatcher_rejects_unknown_job(capsys):
    assert run_maintenance_job.main(["definitely-not-a-job"]) == 2
    assert "usage:" in capsys.readouterr().err


def test_maintenance_dispatcher_runs_analytics():
    assert run_maintenance_job.main(["analytics"]) == 0
