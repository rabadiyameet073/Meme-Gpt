#!/usr/bin/env python3
"""
Generate sentence-transformer embeddings for all memes using all-MiniLM-L6-v2.
Run: pip install sentence-transformers && python scripts/generate_embeddings.py
Output: server/data/embeddings.json
"""

import json
import sqlite3
import sys
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Install: pip install sentence-transformers")
    sys.exit(1)

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "prisma" / "dev.db"
OUTPUT = ROOT / "server" / "data" / "embeddings.json"
MODEL_NAME = "all-MiniLM-L6-v2"


def get_combined_embedding(
    text_emb: list[float],
    image_emb: list[float],
    text_weight: float = 0.65,
    image_weight: float = 0.35,
) -> list[float]:
    """
    Weighted combination: text contributes 65%, image 35%.
    Text gets higher weight because meme search is primarily semantic.
    Combined dimension: 384 + 512 = 896.
    """
    text_arr = np.array(text_emb) * text_weight
    image_arr = np.array(image_emb) * image_weight
    combined = np.concatenate([text_arr, image_arr])
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    return combined.tolist()


def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run: npm run db:setup")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, dialogue, explanation, keywords FROM Meme"
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No memes in database. Run: npm run db:seed")
        sys.exit(1)

    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    embeddings = []
    for row in rows:
        meme_id, name, dialogue, explanation, keywords_json = row
        keywords = json.loads(keywords_json) if keywords_json else []
        text = f"{name}. {dialogue}. {explanation}. {' '.join(keywords)}"
        vector = model.encode(text, normalize_embeddings=True).tolist()
        embeddings.append({"id": meme_id, "vector": vector})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(embeddings, f)

    print(f"Generated {len(embeddings)} embeddings -> {OUTPUT}")


if __name__ == "__main__":
    main()
