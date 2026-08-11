"""
MemeGPT — Automated Developer Setup & Onboarding Script
Verifies system prerequisites, environment variables, seeds database, and generates embeddings.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
ENV_FILE = ROOT_DIR / ".env"
ENV_EXAMPLE = ROOT_DIR / ".env.example"


def print_step(title: str):
    print("\n" + "="*60)
    print(f" [STEP] {title}")
    print("="*60)


def check_prerequisites():
    print_step("Step 1: Checking System Prerequisites")

    # Python version check
    py_ver = sys.version_info
    print(f"  * Python Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver.major < 3 or (py_ver.major == 3 and py_ver.minor < 11):
        print("  [FAIL] Python 3.11 or higher is required.")
        sys.exit(1)
    print("  [OK] Python version is compatible.")

    # Node.js check
    try:
        node_ver = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"  * Node.js Version: {node_ver}")
        print("  [OK] Node.js is installed.")
    except Exception:
        print("  [WARN] Node.js not found in PATH. Make sure Node.js v18+ is installed for frontend.")

    # NPM check
    try:
        npm_ver = subprocess.check_output(["npm", "--version"], text=True).strip()
        print(f"  * NPM Version: {npm_ver}")
        print("  [OK] NPM is installed.")
    except Exception:
        print("  [WARN] NPM not found in PATH.")


def setup_environment():
    print_step("Step 2: Checking Environment Configuration")

    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            print(f"  [OK] Copied {ENV_EXAMPLE.name} -> {ENV_FILE.name}")
        else:
            print("  [WARN] Neither .env nor .env.example found. Creating basic .env...")
            ENV_FILE.write_text("ENVIRONMENT=development\nLOG_LEVEL=INFO\nAPI_PORT=8000\n", encoding="utf-8")
    else:
        print(f"  [OK] Environment file {ENV_FILE.name} already exists.")


def seed_database_and_embeddings():
    print_step("Step 3: Database Seeding & Vector Pre-computation")

    # Run seed.py
    print("  * Seeding database with memes...")
    seed_script = BACKEND_DIR / "seed.py"
    try:
        res = subprocess.run([sys.executable, str(seed_script)], cwd=str(BACKEND_DIR), check=True, text=True, capture_output=True)
        print(f"  [OK] Database seeded: {res.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] Seeding failed: {e.stderr}")
        sys.exit(1)

    # Run generate_embeddings.py
    print("  * Generating vector embeddings...")
    embed_script = BACKEND_DIR / "generate_embeddings.py"
    try:
        res = subprocess.run([sys.executable, str(embed_script)], cwd=str(BACKEND_DIR), check=True, text=True, capture_output=True)
        print(f"  [OK] Embeddings generated: {res.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  [WARN] Vector embedding pre-computation: {e.stderr or e.stdout}")


def check_frontend_readiness():
    print_step("Step 4: Frontend Readiness Check")

    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("  * Installing frontend dependencies via npm...")
        try:
            subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)
            print("  [OK] Frontend dependencies installed successfully.")
        except Exception as e:
            print(f"  [WARN] Run 'cd frontend && npm install' manually: {e}")
    else:
        print("  [OK] Frontend node_modules already installed.")


def main():
    print("=== MemeGPT Setup & Onboarding Wizard ===")
    check_prerequisites()
    setup_environment()
    seed_database_and_embeddings()
    check_frontend_readiness()

    print_step("Setup Complete!")
    print("  To start MemeGPT in development mode:")
    print("    npm run dev")
    print("\n  Services will be available at:")
    print("    * Web Frontend: http://localhost:5173")
    print("    * Backend API:  http://localhost:8000")
    print("    * API Docs:     http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
