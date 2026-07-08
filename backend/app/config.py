"""MemeGPT FastAPI backend."""
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = BACKEND_DIR / "memegpt.db"
