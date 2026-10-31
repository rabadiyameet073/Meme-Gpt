"""Repository-root resolution shared by the test suite.

Several legacy tests addressed fixtures through literal Windows paths such as
``Path("d:/Meme GPT/frontend/vercel.json")``. Those tests could never run on a
different machine, a CI runner, or even a differently-named clone, and were the
single largest cause of the suite's failures (AUDIT-REPORT D-6). Every test now
resolves paths relative to this module instead.
"""

from pathlib import Path

# backend/tests/paths.py -> backend/tests -> backend -> <repo root>
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
FRONTEND_ROOT = REPO_ROOT / "frontend"
APPS_ROOT = REPO_ROOT / "apps"
WORKFLOWS_ROOT = REPO_ROOT / ".github" / "workflows"

__all__ = [
    "REPO_ROOT",
    "BACKEND_ROOT",
    "FRONTEND_ROOT",
    "APPS_ROOT",
    "WORKFLOWS_ROOT",
]
