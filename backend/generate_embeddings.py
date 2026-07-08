"""Generate all-MiniLM-L6-v2 embeddings for memes."""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import BACKEND_DIR, DATA_DIR

DB_PATH = BACKEND_DIR / "memegpt.db"
OUTPUT = DATA_DIR / "embeddings.json"


def main():
    if not DB_PATH.exists():
        print("Run: python seed.py first")
        sys.exit(1)

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("pip install sentence-transformers")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, dialogue, explanation, keywords FROM memes"
    ).fetchall()
    conn.close()

    if not rows:
        print("No memes found.")
        sys.exit(1)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    out = []
    for meme_id, name, dialogue, explanation, keywords_json in rows:
        keywords = json.loads(keywords_json or "[]")
        text = f"{name}. {dialogue}. {explanation}. {' '.join(keywords)}"
        vector = model.encode(text, normalize_embeddings=True).tolist()
        out.append({"id": meme_id, "vector": vector})

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out), encoding="utf-8")
    print(f"Saved {len(out)} embeddings to {OUTPUT}")


if __name__ == "__main__":
    main()
