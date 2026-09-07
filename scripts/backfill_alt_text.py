"""Backfill alt_text for memes that don't have one."""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal, Meme

db = SessionLocal()
memes = db.query(Meme).filter((Meme.alt_text == None) | (Meme.alt_text == "")).all()

for meme in memes:
    parts = [f"Meme titled {meme.name}"]
    if meme.emotions_list():
        parts.append(f"expressing {', '.join(meme.emotions_list())}")
    if meme.categories_list():
        parts.append(f"about {', '.join(meme.categories_list())}")
    if meme.dialogue:
        parts.append(f"with text: {meme.dialogue[:100]}")
    meme.alt_text = ". ".join(parts)

db.commit()
print(f"[SUCCESS] Backfilled alt_text for {len(memes)} memes")
db.close()
