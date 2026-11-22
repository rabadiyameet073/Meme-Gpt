"""Baseline schema migration for MemeGPT.

Revision ID: 0001_baseline_schema
Revises: 
Create Date: 2026-11-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_baseline_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('email', sa.String(length=255), unique=True, nullable=True),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('oauth_provider', sa.String(length=50), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('plan', sa.String(length=20), server_default='free'),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('rate_limit', sa.Integer(), server_default='120'),
        sa.Column('preferred_format', sa.String(length=20), server_default='gif'),
        sa.Column('theme', sa.String(length=20), server_default='dark'),
        sa.Column('nsfw_enabled', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('favourite_categories', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('is_admin', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_oauth', 'users', ['oauth_provider', 'oauth_id'])

    # 2. memes
    op.create_table(
        'memes',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), unique=True, nullable=True),
        sa.Column('categories', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('emotions', sa.JSON(), nullable=True),
        sa.Column('dialogue', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('gif_url', sa.String(length=500), nullable=True),
        sa.Column('mp4_url', sa.String(length=500), nullable=True),
        sa.Column('thumb_url', sa.String(length=500), nullable=True),
        sa.Column('webp_url', sa.String(length=500), nullable=True),
        sa.Column('image_ref', sa.String(length=255), nullable=True),
        sa.Column('video_ref', sa.String(length=255), nullable=True),
        sa.Column('gif_ref', sa.String(length=255), nullable=True),
        sa.Column('alt_text', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), server_default='manual'),
        sa.Column('nsfw', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('flag_count', sa.Integer(), server_default='0'),
        sa.Column('moderation_status', sa.String(length=20), server_default='approved'),
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('download_count', sa.Integer(), server_default='0'),
        sa.Column('usage_count', sa.Integer(), server_default='0'),
        sa.Column('upvotes', sa.Integer(), server_default='0'),
        sa.Column('downvotes', sa.Integer(), server_default='0'),
        sa.Column('viral_score', sa.Float(), server_default='0.0'),
        sa.Column('popularity_score', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('indexed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_memes_slug', 'memes', ['slug'])
    op.create_index('idx_memes_nsfw', 'memes', ['nsfw'])
    op.create_index('idx_memes_popularity', 'memes', ['popularity_score'])
    op.create_index('idx_memes_source', 'memes', ['source'])

    # 3. meme_votes
    op.create_table(
        'meme_votes',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('meme_id', sa.String(length=64), sa.ForeignKey('memes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('vote', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('meme_id', 'session_id', name='uq_meme_session_vote'),
    )
    op.create_index('idx_meme_votes_session', 'meme_votes', ['session_id'])

    # 4. meme_usage
    op.create_table(
        'meme_usage',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('meme_id', sa.String(length=64), sa.ForeignKey('memes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_meme_usage_meme_id', 'meme_usage', ['meme_id'])
    op.create_index('idx_meme_usage_session_id', 'meme_usage', ['session_id'])

    # 5. favourite_memes
    op.create_table(
        'favourite_memes',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('meme_id', sa.String(length=64), sa.ForeignKey('memes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('meme_id', 'session_id', name='uq_meme_session_fav'),
    )

    # 6. meme_flags
    op.create_table(
        'meme_flags',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('meme_id', sa.String(length=64), sa.ForeignKey('memes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reporter_ip', sa.String(length=45), nullable=True),
        sa.Column('reporter_user_id', sa.String(length=64), nullable=True),
        sa.Column('reason', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), server_default=''),
        sa.Column('status', sa.String(length=20), server_default='pending'),
        sa.Column('reviewed_by', sa.String(length=64), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_flags_meme_status', 'meme_flags', ['meme_id', 'status'])

    # 7. saved_memes
    op.create_table(
        'saved_memes',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meme_id', sa.String(length=64), sa.ForeignKey('memes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('collection_name', sa.String(length=100), server_default='Favorites'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # 8. feedback
    op.create_table(
        'feedback',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('session_id', sa.String(length=64), server_default='anonymous', nullable=True),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('meme_id', sa.String(length=64), sa.ForeignKey('memes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=True),
        sa.Column('query_id', sa.String(length=64), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('format', sa.String(length=20), server_default='image'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_feedback_meme_id', 'feedback', ['meme_id'])
    op.create_index('idx_feedback_action', 'feedback', ['action'])

    # 9. search_logs
    op.create_table(
        'search_logs',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('query_hash', sa.String(length=32), nullable=True),
        sa.Column('session_id', sa.String(length=64), nullable=True),
        sa.Column('result_count', sa.Integer(), server_default='0'),
        sa.Column('top_meme_id', sa.String(length=64), nullable=True),
        sa.Column('latency_ms', sa.Float(), server_default='0.0'),
        sa.Column('cache_hit', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('model_used', sa.String(length=50), nullable=True),
        sa.Column('emotion_detected', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_search_logs_created_at', 'search_logs', ['created_at'])
    op.create_index('idx_search_logs_query_hash', 'search_logs', ['query_hash'])

    # 10. api_keys
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=100), server_default='Default API Key'),
        sa.Column('key_hash', sa.String(length=64), unique=True, nullable=False),
        sa.Column('prefix', sa.String(length=32), nullable=False),
        sa.Column('tier', sa.String(length=20), server_default='free'),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('revoked', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
    )
    op.create_index('idx_api_keys_key_hash', 'api_keys', ['key_hash'])

    # 11. device_tokens
    op.create_table(
        'device_tokens',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('token', sa.String(length=255), unique=True, nullable=False),
        sa.Column('platform', sa.String(length=20), server_default='android'),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('app_version', sa.String(length=32), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_device_tokens_platform_active', 'device_tokens', ['platform', 'active'])


def downgrade() -> None:
    op.drop_table('device_tokens')
    op.drop_table('api_keys')
    op.drop_table('search_logs')
    op.drop_table('feedback')
    op.drop_table('saved_memes')
    op.drop_table('meme_flags')
    op.drop_table('favourite_memes')
    op.drop_table('meme_usage')
    op.drop_table('meme_votes')
    op.drop_table('memes')
    op.drop_table('users')
