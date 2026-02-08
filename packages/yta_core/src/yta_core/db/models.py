import enum
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from yta_core.db.base import Base


class TrackerType(str, enum.Enum):
    channel = "channel"
    search = "search"


class RankingMetric(str, enum.Enum):
    views = "views"
    likes = "likes"
    comments = "comments"
    views_delta = "views_delta"
    views_velocity = "views_velocity"
    likes_delta = "likes_delta"
    comments_delta = "comments_delta"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    trackers: Mapped[list["Tracker"]] = relationship(back_populates="owner")


class Tracker(Base):
    __tablename__ = "trackers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    type: Mapped[TrackerType] = mapped_column(Enum(TrackerType), nullable=False)
    channel_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    search_query: Mapped[str | None] = mapped_column(String(255), nullable=True)

    top_n: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    candidate_pool_size: Mapped[int] = mapped_column(
        Integer, default=200, nullable=False
    )

    ranking_metric: Mapped[RankingMetric] = mapped_column(
        Enum(RankingMetric), default=RankingMetric.views, nullable=False
    )
    ranking_window_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)

    discovery_interval_hours: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    snapshot_interval_hours: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )

    next_discovery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_snapshot_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="trackers")
    candidates: Mapped[list["TrackerCandidate"]] = relationship(
        back_populates="tracker", cascade="all, delete-orphan"
    )


class Video(Base):
    __tablename__ = "videos"

    video_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    channel_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_iso: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TrackerCandidate(Base):
    __tablename__ = "tracker_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tracker_id: Mapped[int] = mapped_column(ForeignKey("trackers.id"), nullable=False)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.video_id"), nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tracker: Mapped["Tracker"] = relationship(back_populates="candidates")
    video: Mapped["Video"] = relationship()

    __table_args__ = (
        UniqueConstraint("tracker_id", "video_id", name="uq_tracker_video"),
        Index("ix_candidates_tracker", "tracker_id"),
        Index("ix_candidates_video", "video_id"),
    )


class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.video_id"), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    view_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    like_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("video_id", "captured_at", name="uq_video_captured"),
        Index("ix_snapshots_video_time", "video_id", "captured_at"),
        Index("ix_snapshots_time", "captured_at"),
    )
