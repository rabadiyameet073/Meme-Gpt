"""
Full meme indexing pipeline:
1. Load raw meme data
2. Download images (if not local)
3. Process with BLIP (captions) + OCR (text) + CLIP (image embedding)
4. Generate text embeddings (MiniLM)
5. Generate combined embeddings (896-dim)
6. Upsert to Qdrant
7. Update database metadata
"""

import json
import os
import sys
import time
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.image_processing_service import (
    load_blip, load_clip,
    process_meme_image,
)
from app.services.embedding_service import embed_text, get_combined_embedding

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = RAW_DIR / "images"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

for d in [PROCESSED_DIR, IMAGES_DIR, EMBEDDINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def download_image(url: str, meme_id: str) -> str:
    """Download image to local disk if not already present."""
    ext = url.split(".")[-1].split("?")[0][:4]
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "jpg"
    path = IMAGES_DIR / f"{meme_id}.{ext}"
    if path.exists():
        return str(path)
    try:
        resp = requests.get(url, timeout=10, stream=True)
        if resp.status_code == 200:
            path.write_bytes(resp.content)
            return str(path)
    except Exception as e:
        print(f"  [WARN] Failed to download {url}: {e}")
    return ""


def run_pipeline():
    master_file = RAW_DIR / "memes_master.json"
    if not master_file.exists():
        # Fallback to DB or processed if raw master not generated yet
        db_dump = DATA_DIR / "processed" / "memes_processed.json"
        if db_dump.exists():
            master_file = db_dump
        else:
            print("[INFO] No memes_master.json found. Will export from database...")
            from app.database import SessionLocal, Meme
            db = SessionLocal()
            memes = [m.to_dict() for m in db.query(Meme).all()]
            db.close()
            with open(RAW_DIR / "memes_master.json", "w", encoding="utf-8") as f:
                json.dump(memes, f, indent=2)
            master_file = RAW_DIR / "memes_master.json"

    with open(master_file, encoding="utf-8") as f:
        memes = json.load(f)

    print(f"[INFO] Loaded {len(memes)} memes for processing")

    print("[INFO] Loading BLIP + CLIP models (if available)...")
    load_blip()
    load_clip()

    processed = []
    for i, meme in enumerate(memes):
        m_name = meme.get("name", "Unknown")
        m_id = str(meme.get("id") or f"meme_{i}")

        # 1. Download image if we only have a URL
        image_path = meme.get("image_path", "")
        if not image_path and meme.get("image_url"):
            image_path = download_image(meme["image_url"], m_id)
            meme["image_path"] = image_path

        # 2. Run image processing (BLIP + OCR + CLIP)
        img_result = process_meme_image(image_path)

        # 3. Build rich text description
        parts = [
            f"Meme: {m_name}",
            f"Caption: {img_result['caption']}" if img_result["caption"] else "",
            f"Text on image: {img_result['ocr_text']}" if img_result["ocr_text"] else "",
            f"Emotions: {', '.join(meme.get('emotions', []))}",
            f"Keywords: {', '.join(meme.get('keywords', []))}",
            f"Categories: {', '.join(meme.get('categories', []))}",
        ]
        text_description = "\n".join(p for p in parts if p)

        # 4. Generate text embedding
        text_embedding = embed_text(text_description[:512])

        # 5. Generate combined embedding (65% text + 35% image)
        combined_embedding = get_combined_embedding(
            text_embedding,
            img_result["image_embedding"],
            text_weight=0.65,
            image_weight=0.35,
        )

        processed.append({
            **meme,
            "id": m_id,
            "caption": img_result["caption"],
            "ocr_text": img_result["ocr_text"],
            "text_description": text_description,
            "text_embedding": text_embedding,
            "image_embedding": img_result["image_embedding"],
            "combined_embedding": combined_embedding,
        })

        if (i + 1) % 50 == 0 or (i + 1) == len(memes):
            print(f"  [PROGRESS] Processed {i+1}/{len(memes)}")

    # Save processed data
    output_file = EMBEDDINGS_DIR / "memes_with_full_embeddings.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)
    print(f"\n[SUCCESS] Saved {len(processed)} fully processed memes to {output_file}")

    # Index to Qdrant if configured
    print("\n[INFO] Checking Qdrant indexing...")
    try:
        from scripts.index_qdrant import index_memes_from_file
        index_memes_from_file(str(output_file))
        print("[SUCCESS] Qdrant indexing complete")
    except Exception as e:
        print(f"[INFO] Qdrant indexing skipped/deferred: {e}")


if __name__ == "__main__":
    start = time.time()
    run_pipeline()
    elapsed = time.time() - start
    print(f"\n[DONE] Total pipeline time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
