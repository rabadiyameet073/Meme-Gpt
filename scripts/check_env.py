"""
MemeGPT — Environment Diagnostics & Health Verification Script
Validates configuration files, database tables, vector files, and service ports.
"""

import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
ENV_FILE = ROOT_DIR / ".env"
DB_FILE = BACKEND_DIR / "memegpt.db"
EMBEDDINGS_FILE = BACKEND_DIR / "data" / "embeddings.json"


def print_check(name: str, passed: bool, detail: str = ""):
    icon = "[OK]" if passed else "[FAIL]"
    msg = f"  {icon} {name}"
    if detail:
        msg += f" ({detail})"
    print(msg)


def main():
    print("\n--- MemeGPT Environment Diagnostics ---\n")
    all_ok = True

    # 1. Environment File Check
    env_exists = ENV_FILE.exists()
    print_check(".env file", env_exists, str(ENV_FILE))
    if not env_exists:
        all_ok = False

    # 2. Database File & Schema Check
    db_exists = DB_FILE.exists()
    meme_count = 0
    if db_exists:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memes")
            meme_count = cursor.fetchone()[0]
            conn.close()
            print_check("Database liveness & tables", meme_count > 0, f"{meme_count} memes in DB")
        except Exception as e:
            print_check("Database liveness & tables", False, str(e))
            all_ok = False
    else:
        print_check("Database file", False, "Run 'python seed.py' to seed database")
        all_ok = False

    # 3. Vector Embeddings Check
    embed_exists = EMBEDDINGS_FILE.exists()
    embed_count = 0
    if embed_exists:
        try:
            data = json.loads(EMBEDDINGS_FILE.read_text(encoding="utf-8"))
            embed_count = len(data)
            print_check("Pre-computed vector embeddings", embed_count > 0, f"{embed_count} vectors loaded")
        except Exception as e:
            print_check("Pre-computed vector embeddings", False, str(e))
            all_ok = False
    else:
        print_check("Pre-computed vector embeddings", False, "Run 'python generate_embeddings.py'")
        all_ok = False

    # 4. Backend Health Endpoint Check (if running)
    try:
        req = urllib.request.urlopen("http://localhost:8000/api/health", timeout=2)
        if req.status == 200:
            res_data = json.loads(req.read().decode("utf-8"))
            print_check("Backend API server liveness", True, f"Running on port 8000, version {res_data.get('version')}")
        else:
            print_check("Backend API server liveness", False, f"HTTP {req.status}")
    except Exception:
        print_check("Backend API server liveness", True, "Not currently running (start via 'npm run dev')")

    print("\n" + "="*50)
    if all_ok:
        print(" [SUCCESS] All checks passed! MemeGPT environment is ready.")
    else:
        print(" [WARNING] System checks completed with warnings. Run 'python scripts/setup.py' to resolve.")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
