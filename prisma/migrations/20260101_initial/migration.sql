-- Migration: 20260101_initial
-- Specification: 06_Database/Migrations.md

-- CreateTable
CREATE TABLE IF NOT EXISTS "memes" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "category" TEXT NOT NULL DEFAULT 'general',
    "dialogue" TEXT NOT NULL DEFAULT '',
    "explanation" TEXT NOT NULL DEFAULT '',
    "keywords" TEXT NOT NULL DEFAULT '[]',
    "emotions" TEXT NOT NULL DEFAULT '[]',
    "image_url" TEXT,
    "gif_url" TEXT,
    "mp4_url" TEXT,
    "thumb_url" TEXT,
    "video_ref" TEXT,
    "gif_ref" TEXT,
    "source" TEXT NOT NULL DEFAULT 'manual',
    "nsfw" BOOLEAN NOT NULL DEFAULT false,
    "viral_score" REAL NOT NULL DEFAULT 0.0,
    "usage_count" INTEGER NOT NULL DEFAULT 0,
    "upvotes" INTEGER NOT NULL DEFAULT 0,
    "downvotes" INTEGER NOT NULL DEFAULT 0,
    "download_count" INTEGER NOT NULL DEFAULT 0,
    "popularity_score" REAL NOT NULL DEFAULT 0.0,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "meme_votes" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "meme_id" TEXT NOT NULL,
    "vote" INTEGER NOT NULL,
    "session_id" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "meme_votes_meme_id_fkey" FOREIGN KEY ("meme_id") REFERENCES "memes" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "meme_usage" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "meme_id" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    "score" REAL NOT NULL,
    "session_id" TEXT NOT NULL DEFAULT 'anonymous',
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "meme_usage_meme_id_fkey" FOREIGN KEY ("meme_id") REFERENCES "memes" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "feedback" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "session_id" TEXT,
    "meme_id" TEXT NOT NULL,
    "query_text" TEXT,
    "query_id" TEXT,
    "action" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "feedback_meme_id_fkey" FOREIGN KEY ("meme_id") REFERENCES "memes" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "saved_memes" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "user_id" TEXT NOT NULL,
    "meme_id" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "saved_memes_meme_id_fkey" FOREIGN KEY ("meme_id") REFERENCES "memes" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "search_logs" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "query" TEXT NOT NULL,
    "query_hash" TEXT NOT NULL,
    "session_id" TEXT NOT NULL,
    "match_count" INTEGER NOT NULL DEFAULT 0,
    "latency_ms" REAL NOT NULL DEFAULT 0.0,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "api_keys" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "key_hash" TEXT NOT NULL,
    "name" TEXT NOT NULL DEFAULT 'Default API Key',
    "prefix" TEXT NOT NULL,
    "tier" TEXT NOT NULL DEFAULT 'free',
    "rate_limit" INTEGER NOT NULL DEFAULT 120,
    "user_id" TEXT,
    "revoked" BOOLEAN NOT NULL DEFAULT false,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "memes_slug_key" ON "memes"("slug");
CREATE UNIQUE INDEX IF NOT EXISTS "meme_votes_meme_id_session_id_key" ON "meme_votes"("meme_id", "session_id");
CREATE UNIQUE INDEX IF NOT EXISTS "api_keys_key_hash_key" ON "api_keys"("key_hash");
