-- Migration: 20260301_add_indexes
-- Specification: 06_Database/Migrations.md

-- B-tree Indexes on Memes
CREATE INDEX IF NOT EXISTS "idx_memes_usage_count" ON "memes"("usage_count");
CREATE INDEX IF NOT EXISTS "idx_memes_viral_score" ON "memes"("viral_score");
CREATE INDEX IF NOT EXISTS "idx_memes_popularity_score" ON "memes"("popularity_score");
CREATE INDEX IF NOT EXISTS "idx_memes_category" ON "memes"("category");
CREATE INDEX IF NOT EXISTS "idx_memes_name" ON "memes"("name");

-- Foreign Key & Activity Indexes
CREATE INDEX IF NOT EXISTS "idx_feedback_meme_id" ON "feedback"("meme_id");
CREATE INDEX IF NOT EXISTS "idx_feedback_action" ON "feedback"("action");
CREATE INDEX IF NOT EXISTS "idx_feedback_created_at" ON "feedback"("created_at");
CREATE INDEX IF NOT EXISTS "idx_saved_memes_user_id" ON "saved_memes"("user_id");
CREATE INDEX IF NOT EXISTS "idx_search_logs_created" ON "search_logs"("created_at");
CREATE INDEX IF NOT EXISTS "idx_search_logs_query_hash" ON "search_logs"("query_hash");
