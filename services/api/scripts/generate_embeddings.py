"""
Step 3 of ML Pipeline — Generate text + image embeddings for all preprocessed memes.
Models used:
  - MiniLM-L6-v2 (80 MB) → 384-dim text embedding
  - CLIP ViT-B/32 (400 MB) → 512-dim image embedding (optional)
  - Combined 896-dim vector (text 65% + image 35%)

Usage:
  python scripts/generate_embeddings.py
  python scripts/generate_embeddings.py --text-only   # skip CLIP (faster)
  python scripts/generate_embeddings.py --new-only    # only process new memes
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


# ── Load models ───────────────────────────────────────────────────────────────

def load_text_model():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("  ✓ MiniLM-L6-v2 loaded (384-dim)")
    return model


def load_clip():
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model = model.half()  # float16 for 2× less RAM
        print("  ✓ CLIP ViT-B/32 loaded (512-dim)")
        return model, processor
    except Exception as e:
        print(f"  ✗ CLIP unavailable: {e} — image embeddings will be zero vectors")
        return None, None


# ── Embedding functions ───────────────────────────────────────────────────────

def get_text_embedding(model, text: str) -> list[float]:
    """384-dimensional normalised text embedding."""
    return model.encode(text, normalize_embeddings=True).tolist()


def get_image_embedding(clip_model, clip_processor, image_path: str) -> list[float]:
    """512-dimensional CLIP image embedding."""
    if clip_model is None:
        return [0.0] * 512
    try:
        import torch
        from PIL import Image
        img = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            features = clip_model.get_image_features(**inputs.to(next(clip_model.parameters()).device))
            features = features / features.norm(dim=-1, keepdim=True)
        return features[0].float().tolist()
    except Exception:
        return [0.0] * 512


def get_combined_embedding(
    text_emb: list[float],
    image_emb: list[float],
    text_weight: float = 0.65,
    image_weight: float = 0.35,
) -> list[float]:
    """
    896-dim weighted combination: text 65%, image 35%.
    Text gets higher weight because meme search is primarily semantic.
    """
    t = np.array(text_emb) * text_weight
    i = np.array(image_emb) * image_weight
    combined = np.concatenate([t, i])
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    return combined.tolist()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-only", action="store_true")
    parser.add_argument("--new-only", action="store_true")
    args = parser.parse_args()

    processed_file = PROCESSED_DIR / "memes_processed.json"
    if not processed_file.exists():
        print(f"✗ No processed data at {processed_file}")
        print("  Run: python scripts/preprocess_memes.py first")
        sys.exit(1)

    with open(processed_file, "r", encoding="utf-8") as f:
        memes = json.load(f)

    # Skip already-embedded if --new-only
    if args.new_only:
        existing_file = EMBEDDINGS_DIR / "memes_with_embeddings.json"
        if existing_file.exists():
            with open(existing_file, "r", encoding="utf-8") as f:
                existing = {m["id"] for m in json.load(f)}
            memes = [m for m in memes if m["id"] not in existing]
            print(f"Processing {len(memes)} new memes only.")

    print(f"Generating embeddings for {len(memes)} memes...")

    text_model = load_text_model()
    clip_model, clip_processor = (None, None) if args.text_only else load_clip()

    for i, meme in enumerate(memes):
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(memes)}] {meme['name']}")

        text_desc = meme.get("text_description") or meme.get("name", "")
        text_emb = get_text_embedding(text_model, text_desc)

        image_path = meme.get("image_path", "")
        image_emb = get_image_embedding(clip_model, clip_processor, image_path) \
            if image_path and Path(image_path).exists() and not args.text_only \
            else [0.0] * 512

        combined_emb = get_combined_embedding(text_emb, image_emb)

        meme["text_embedding"] = text_emb        # 384-dim
        meme["image_embedding"] = image_emb      # 512-dim
        meme["combined_embedding"] = combined_emb  # 896-dim normalised

    out = EMBEDDINGS_DIR / "memes_with_embeddings.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(memes, f)

    print(f"\n✅ Generated embeddings for {len(memes)} memes → {out}")


if __name__ == "__main__":
    main()
