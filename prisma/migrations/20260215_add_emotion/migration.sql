-- Migration: 20260215_add_emotion
-- Specification: 06_Database/Migrations.md

-- Step 1: Add emotion_score column as nullable (Safe, zero downtime)
ALTER TABLE "memes" ADD COLUMN "emotion_score" REAL;

-- Step 2: Backfill data in batches (simulated batch update)
UPDATE "memes" SET "emotion_score" = 0.5 WHERE "emotion_score" IS NULL;

-- Step 3: Set column NOT NULL in SQLite / PostgreSQL compatible syntax
-- In PostgreSQL: ALTER TABLE memes ALTER COLUMN emotion_score SET NOT NULL;
