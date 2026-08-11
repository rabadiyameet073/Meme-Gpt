"""
Step 2 of ML Pipeline — Preprocess memes.
For each meme: OCR text extraction, BLIP captioning, Groq LLM tag generation,
then build rich text_description for embedding.

Usage:
  python scripts/preprocess_memes.py
  python scripts/preprocess_memes.py --batch-size 10
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ── OCR: extract text from meme image ────────────────────────────────────────

def extract_text_ocr(image_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image, ImageFilter
        img = Image.open(image_path).convert("L")
        img = img.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")
        return text.strip()
    except Exception as e:
        return ""


# ── BLIP: generate caption from meme image ───────────────────────────────────

_blip_model = None
_blip_processor = None


def get_blip():
    global _blip_model, _blip_processor
    if _blip_model is None:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            _blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            _blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            print("  BLIP captioning model loaded.")
        except Exception as e:
            print(f"  BLIP unavailable: {e}")
    return _blip_model, _blip_processor


def generate_caption_blip(image_path: str) -> str:
    model, processor = get_blip()
    if model is None:
        return ""
    try:
        import torch
        from PIL import Image
        img = Image.open(image_path).convert("RGB")
        inputs = processor(img, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=60)
        return processor.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        return ""


# ── Groq: generate rich semantic tags ────────────────────────────────────────

_groq_client = None


def get_groq():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            try:
                from groq import Groq
                _groq_client = Groq(api_key=api_key)
            except Exception as e:
                print(f"  Groq unavailable: {e}")
    return _groq_client


def generate_meme_tags(name: str, ocr_text: str, caption: str) -> dict:
    client = get_groq()
    if not client:
        return {"emotions": [], "situations": [], "tone": "neutral",
                "keywords": [name.lower()], "meme_type": "reaction", "best_for": []}

    prompt = f"""Meme name: {name}
Text visible in meme: {ocr_text}
Image description: {caption}

Generate meme metadata. Return ONLY this JSON (no explanation):
{{
  "emotions": ["joy", "surprise"],
  "situations": ["winning unexpected", "software bug fixed"],
  "tone": "humorous",
  "keywords": ["victory", "celebration"],
  "cultural_refs": [],
  "meme_type": "reaction",
  "best_for": ["when something finally works", "unexpected success"]
}}"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300,
        )
        import re, json as _json
        raw = resp.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return _json.loads(match.group())
    except Exception as e:
        print(f"    Groq tag error for '{name}': {e}")
    return {"emotions": [], "situations": [], "tone": "neutral",
            "keywords": [name.lower()], "meme_type": "reaction", "best_for": []}


# ── Build rich text description for embedding ─────────────────────────────────

def build_text_description(meme: dict, tags: dict) -> str:
    parts = [
        f"Meme: {meme['name']}",
        f"Description: {meme.get('caption', '')}",
        f"Text on image: {meme.get('ocr_text', '')}",
        f"Emotions: {', '.join(tags.get('emotions', []))}",
        f"Situations: {', '.join(tags.get('situations', []))}",
        f"Keywords: {', '.join(tags.get('keywords', []))}",
        f"Best used for: {', '.join(tags.get('best_for', []))}",
        f"Meme type: {tags.get('meme_type', '')}",
    ]
    return "\n".join(p for p in parts if p.split(": ", 1)[-1].strip())


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=50)
    args = parser.parse_args()

    raw_file = RAW_DIR / "memes_master.json"
    if not raw_file.exists():
        print(f"✗ No raw data found at {raw_file}")
        print("  Run: python scripts/download_datasets.py first")
        sys.exit(1)

    with open(raw_file, "r", encoding="utf-8") as f:
        raw_memes = json.load(f)

    print(f"Processing {len(raw_memes)} memes (batch_size={args.batch_size})...")
    processed = []

    for i, meme in enumerate(raw_memes):
        print(f"  [{i+1}/{len(raw_memes)}] {meme['name']}")

        image_path = meme.get("image_path", "")
        ocr_text = extract_text_ocr(image_path) if image_path and Path(image_path).exists() else ""
        caption = generate_caption_blip(image_path) if image_path and Path(image_path).exists() else ""
        tags = generate_meme_tags(meme["name"], ocr_text, caption)
        text_description = build_text_description({**meme, "ocr_text": ocr_text, "caption": caption}, tags)

        processed.append({
            **meme,
            "ocr_text": ocr_text,
            "caption": caption,
            "tags": tags,
            "text_description": text_description,
            "emotions": tags.get("emotions", []),
            "situations": tags.get("situations", []),
            "keywords": tags.get("keywords", []),
            "meme_type": tags.get("meme_type", "reaction"),
        })

        if (i + 1) % args.batch_size == 0:
            time.sleep(0.1)  # Groq rate limit courtesy pause

    out = PROCESSED_DIR / "memes_processed.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Preprocessed {len(processed)} memes → {out}")


if __name__ == "__main__":
    main()
