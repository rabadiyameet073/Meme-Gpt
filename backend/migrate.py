#!/usr/bin/env python3
"""
MemeGPT Database Migration — Adds missing columns per Gap Analysis.
Specification: 02_Database_Schema_Migration.md (Step 4)

Run once: python migrate.py
"""
import os
import sqlite3
import sys

# Ensure UTF-8 output across all consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "memegpt.db")

MIGRATIONS = [
    # Meme table additions
    "ALTER TABLE memes ADD COLUMN emotions TEXT DEFAULT '[]'",
    "ALTER TABLE memes ADD COLUMN nsfw INTEGER DEFAULT 0",
    "ALTER TABLE memes ADD COLUMN thumb_url TEXT",
    "ALTER TABLE memes ADD COLUMN webp_url TEXT",
    "ALTER TABLE memes ADD COLUMN image_url TEXT",
    "ALTER TABLE memes ADD COLUMN gif_url TEXT",
    "ALTER TABLE memes ADD COLUMN mp4_url TEXT",
    "ALTER TABLE memes ADD COLUMN source TEXT DEFAULT 'manual'",
    "ALTER TABLE memes ADD COLUMN view_count INTEGER DEFAULT 0",
    "ALTER TABLE memes ADD COLUMN download_count INTEGER DEFAULT 0",
    "ALTER TABLE memes ADD COLUMN popularity_score REAL DEFAULT 0.0",
    "ALTER TABLE memes ADD COLUMN indexed_at TEXT",
    "ALTER TABLE memes ADD COLUMN categories TEXT DEFAULT '[]'",

    # User table additions
    "ALTER TABLE users ADD COLUMN name TEXT",
    "ALTER TABLE users ADD COLUMN avatar_url TEXT",
    "ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}'",

    # SearchLog table — rename and add columns
    "ALTER TABLE search_logs ADD COLUMN query_hash TEXT",
    "ALTER TABLE search_logs ADD COLUMN top_meme_id TEXT",
    "ALTER TABLE search_logs ADD COLUMN cache_hit INTEGER DEFAULT 0",
    "ALTER TABLE search_logs ADD COLUMN model_used TEXT",
    "ALTER TABLE search_logs ADD COLUMN emotion_detected TEXT",

    # Migrate existing category string → categories JSON array (if category column exists)
    "UPDATE memes SET categories = '[\"' || category || '\"]' WHERE categories IS NULL OR categories = '[]'",

    # Copy existing image refs to new URL columns
    "UPDATE memes SET image_url = image_ref WHERE image_url IS NULL AND image_ref IS NOT NULL",
    "UPDATE memes SET gif_url = gif_ref WHERE gif_url IS NULL AND gif_ref IS NOT NULL",
    "UPDATE memes SET mp4_url = video_ref WHERE mp4_url IS NULL AND video_ref IS NOT NULL",

    # Anonymize existing raw query text in search_logs
    # WARNING: This overwrites raw text with hash — GDPR compliance
    "UPDATE search_logs SET query_hash = 'migrated', query = NULL WHERE query IS NOT NULL",

    # Clean any orphan foreign key records for referential integrity
    "DELETE FROM meme_votes WHERE meme_id NOT IN (SELECT id FROM memes)",
    "DELETE FROM meme_usage WHERE meme_id NOT IN (SELECT id FROM memes)",
    "DELETE FROM feedback WHERE meme_id NOT IN (SELECT id FROM memes)",
    "DELETE FROM saved_memes WHERE meme_id NOT IN (SELECT id FROM memes)",
]


def run_migration(db_path: str = DB_PATH) -> dict:
    """Run all schema migrations against target database."""
    # Ensure database directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    # First, make sure tables exist using SQLAlchemy metadata
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    success = 0
    skipped = 0
    for sql in MIGRATIONS:
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"  [OK] {sql[:60]}...")
            success += 1
        except sqlite3.OperationalError as e:
            err_msg = str(e).lower()
            if "duplicate column" in err_msg or "no such column" in err_msg:
                print(f"  [SKIP] Handled / Column state: {sql[:60]}... ({e})")
                skipped += 1
            else:
                print(f"  [WARN] Notice: {e} -> SQL: {sql}")
                skipped += 1
        except Exception as e:
            print(f"  [ERROR] {e} -> SQL: {sql}")
            skipped += 1

    conn.close()
    print(f"\n[DONE] Migration complete: {success} applied, {skipped} skipped/handled.")
    return {"applied": success, "skipped": skipped}


if __name__ == "__main__":
    print(f"Running migration on: {DB_PATH}")
    run_migration()
