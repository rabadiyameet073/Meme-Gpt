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
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, category, dialogue, explanation, keywords, image_ref, video_ref, gif_ref, viral_score, usage_count, upvotes, downvotes FROM memes"
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No memes found.")
        sys.exit(1)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    out = []
    for meme_id, name, category, dialogue, explanation, keywords_json, image_ref, video_ref, gif_ref, viral_score, usage_count, upvotes, downvotes in rows:
        keywords = json.loads(keywords_json or "[]")
        text = f"{name}. Category: {category}. Dialogue: {dialogue}. Explanation: {explanation}. Tags: {' '.join(keywords)}"
        vector = model.encode(text, normalize_embeddings=True).tolist()
        payload = {
            "id": meme_id,
            "name": name,
            "category": category,
            "dialogue": dialogue,
            "explanation": explanation,
            "keywords": keywords,
            "imageRef": image_ref,
            "videoRef": video_ref,
            "gifRef": gif_ref,
            "viralScore": viral_score,
            "usageCount": usage_count,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "has_gif": bool(gif_ref),
            "has_video": bool(video_ref),
        }
        out.append({"id": meme_id, "vector": vector, "payload": payload})

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out), encoding="utf-8")
    print(f"Saved {len(out)} embeddings with full payload to {OUTPUT}")


if __name__ == "__main__":
    main()
