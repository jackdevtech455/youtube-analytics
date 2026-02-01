"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-30
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])

    op.create_table(
        "trackers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "owner_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("type", sa.Enum("channel", "search", name="trackertype"), nullable=False),
        sa.Column("channel_id", sa.String(length=64), nullable=True),
        sa.Column("search_query", sa.String(length=255), nullable=True),
        sa.Column("top_n", sa.Integer(), nullable=False),
        sa.Column("candidate_pool_size", sa.Integer(), nullable=False),
        sa.Column(
            "ranking_metric",
            sa.Enum(
                "views",
                "likes",
                "comments",
                "views_delta",
                "views_velocity",
                "likes_delta",
                "comments_delta",
                name="rankingmetric",
            ),
            nullable=False,
        ),
        sa.Column("ranking_window_hours", sa.Integer(), nullable=True),
        sa.Column("discovery_interval_hours", sa.Integer(), nullable=False),
        sa.Column("snapshot_interval_hours", sa.Integer(), nullable=False),
        sa.Column("next_discovery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_snapshot_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "videos",
        sa.Column("video_id", sa.String(length=32), primary_key=True),
        sa.Column("channel_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_iso", sa.String(length=32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "tracker_candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "tracker_id", sa.Integer(), sa.ForeignKey("trackers.id"), nullable=False
        ),
        sa.Column(
            "video_id",
            sa.String(length=32),
            sa.ForeignKey("videos.video_id"),
            nullable=False,
        ),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("source_rank", sa.Integer(), nullable=True),
        sa.UniqueConstraint("tracker_id", "video_id", name="uq_tracker_video"),
    )
    op.create_index("ix_candidates_tracker", "tracker_candidates", ["tracker_id"])
    op.create_index("ix_candidates_video", "tracker_candidates", ["video_id"])

    op.create_table(
        "video_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "video_id",
            sa.String(length=32),
            sa.ForeignKey("videos.video_id"),
            nullable=False,
        ),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=True),
        sa.Column("comment_count", sa.Integer(), nullable=True),
        sa.UniqueConstraint("video_id", "captured_at", name="uq_video_captured"),
    )
    op.create_index(
        "ix_snapshots_video_time", "video_snapshots", ["video_id", "captured_at"]
    )
    op.create_index("ix_snapshots_time", "video_snapshots", ["captured_at"])


def downgrade() -> None:
    op.drop_index("ix_snapshots_time", table_name="video_snapshots")
    op.drop_index("ix_snapshots_video_time", table_name="video_snapshots")
    op.drop_table("video_snapshots")

    op.drop_index("ix_candidates_video", table_name="tracker_candidates")
    op.drop_index("ix_candidates_tracker", table_name="tracker_candidates")
    op.drop_table("tracker_candidates")

    op.drop_table("videos")
    op.drop_table("trackers")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS rankingmetric")
    op.execute("DROP TYPE IF EXISTS trackertype")
