"""
MemeGPT — Preprocessing & Metadata Enrichment Script
Matches specifications from 05_AI_System/AI_Pipeline.md
"""

import json
from pathlib import Path


def compose_meme_text(meme: dict) -> str:
    """Combine all meme metadata fields into a single rich text

    optimized for MiniLM embedding.
    """
    parts = []
    if meme.get("name"):
        parts.append(f"Meme: {meme['name']}.")
    if meme.get("blip_caption") or meme.get("caption"):
        parts.append(f"Shows: {meme.get('blip_caption') or meme.get('caption')}.")
    if meme.get("ocr_text") and len(meme["ocr_text"].strip()) > 3:
        parts.append(f"Text in image: {meme['ocr_text']}.")
    if meme.get("emotions"):
        parts.append(f"Emotions: {', '.join(meme['emotions']) if isinstance(meme['emotions'], list) else str(meme['emotions'])}.")
    if meme.get("situations"):
        sits = meme['situations'][:5] if isinstance(meme['situations'], list) else [str(meme['situations'])]
        parts.append(f"Used when: {', '.join(sits)}.")
    if meme.get("categories"):
        cats = meme['categories'] if isinstance(meme['categories'], list) else [str(meme['categories'])]
        parts.append(f"Categories: {', '.join(cats)}.")
    if meme.get("keywords"):
        kws = meme['keywords'][:10] if isinstance(meme['keywords'], list) else [str(meme['keywords'])]
        parts.append(f"Keywords: {', '.join(kws)}.")

    composed = " ".join(parts)
    return composed[:2048]


def build_meme_text_description(meme: dict, tags: dict | None = None) -> str:
    """Build comprehensive text for MiniLM embedding."""
    if tags:
        merged = {**meme, **tags}
        return compose_meme_text(merged)
    return compose_meme_text(meme)


def preprocess_manifest(input_path: str = "data/raw/dataset_manifest.json", output_path: str = "data/processed/memes_processed.json"):
    in_file = Path(input_path)
    if not in_file.exists():
        print(f"⚠️ Input manifest {input_path} not found")
        return []

    with open(in_file, "r", encoding="utf-8") as f:
        memes = json.load(f)

    processed = []
    for m in memes:
        desc = build_meme_text_description(m, m.get("tags", {}))
        processed.append({
            **m,
            "rich_description": desc,
        })

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    print(f"✓ Preprocessed {len(processed)} memes saved to {output_path}")
    return processed


if __name__ == "__main__":
    preprocess_manifest()
