"""
MemeGPT — Batch Meme Image Processing Script
Matches specifications from 05_AI_System/Image_Analysis.md
"""

import json
import os
import sys
from pathlib import Path

# Add backend to path for imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.services.image_analysis_service import process_meme


def process_images(
    manifest_path: str = "data/raw/dataset_manifest.json",
    output_path: str = "data/processed/memes_analyzed.json",
    limit: int = 10,
):
    in_file = Path(manifest_path)
    if not in_file.exists():
        print(f"⚠️ Manifest not found at {manifest_path}")
        return []

    with open(in_file, "r", encoding="utf-8") as f:
        memes = json.load(f)

    processed_results = []
    print(f"Starting image analysis for {min(len(memes), limit)} memes...")

    for i, meme in enumerate(memes[:limit], 1):
        name = meme.get("name", f"Meme {i}")
        img_path = meme.get("image_path", "")
        print(f"[{i}/{min(len(memes), limit)}] Processing '{name}'...")
        result = process_meme(img_path, name)
        processed_results.append({
            **meme,
            **result,
        })

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(processed_results, f, indent=2)

    print(f"✓ Completed image analysis. Saved to {output_path}")
    return processed_results


if __name__ == "__main__":
    process_images()
