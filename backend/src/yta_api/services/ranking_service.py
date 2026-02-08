from datetime import timedelta
from sqlalchemy import and_, func, select, Float
from sqlalchemy.orm import Session
from yta_core.db.models import (
    RankingMetric,
    Tracker,
    TrackerCandidate,
    Video,
    VideoSnapshot,
)
from yta_core.time_utils import hour_bucket, utc_now


def _latest_snapshot_time_subquery():
    return (
        select(
            VideoSnapshot.video_id.label("video_id"),
            func.max(VideoSnapshot.captured_at).label("latest_captured_at"),
        )
        .group_by(VideoSnapshot.video_id)
        .subquery()
    )


def _snapshot_at_or_before_subquery(snapshot_time):
    return (
        select(
            VideoSnapshot.video_id.label("video_id"),
            func.max(VideoSnapshot.captured_at).label("captured_at"),
        )
        .where(VideoSnapshot.captured_at <= snapshot_time)
        .group_by(VideoSnapshot.video_id)
        .subquery()
    )


def compute_top_videos(database_session: Session, tracker_id: int) -> list[dict]:
    tracker: Tracker | None = database_session.get(Tracker, tracker_id)
    if tracker is None or not tracker.is_active:
        return []

    ranking_metric = tracker.ranking_metric
    window_hours = tracker.ranking_window_hours or 24

    current_time = utc_now()
    current_bucket = hour_bucket(current_time)
    window_start_bucket = current_bucket - timedelta(hours=window_hours)

    candidate_video_ids = (
        select(TrackerCandidate.video_id)
        .where(TrackerCandidate.tracker_id == tracker_id)
        .subquery()
    )

    latest_snapshot_time = _latest_snapshot_time_subquery()
    latest_snapshot = (
        select(VideoSnapshot)
        .join(
            latest_snapshot_time,
            and_(
                VideoSnapshot.video_id == latest_snapshot_time.c.video_id,
                VideoSnapshot.captured_at == latest_snapshot_time.c.latest_captured_at,
            ),
        )
        .subquery()
    )

    latest_video_stats = (
        select(
            Video.video_id.label("video_id"),
            Video.title.label("title"),
            Video.channel_id.label("channel_id"),
            Video.published_at.label("published_at"),
            latest_snapshot.c.view_count.label("view_count"),
            latest_snapshot.c.like_count.label("like_count"),
            latest_snapshot.c.comment_count.label("comment_count"),
        )
        .join(latest_snapshot, latest_snapshot.c.video_id == Video.video_id)
        .where(Video.video_id.in_(select(candidate_video_ids.c.video_id)))
        .subquery()
    )

    if ranking_metric in (
        RankingMetric.views,
        RankingMetric.likes,
        RankingMetric.comments,
    ):
        score_column = {
            RankingMetric.views: latest_video_stats.c.view_count,
            RankingMetric.likes: latest_video_stats.c.like_count,
            RankingMetric.comments: latest_video_stats.c.comment_count,
        }[ranking_metric]

        query = (
            select(
                latest_video_stats.c.video_id,
                latest_video_stats.c.title,
                latest_video_stats.c.channel_id,
                latest_video_stats.c.published_at,
                func.coalesce(score_column, 0).cast(Float).label("score"),
                latest_video_stats.c.view_count,
                latest_video_stats.c.like_count,
                latest_video_stats.c.comment_count,
            )
            .order_by(func.coalesce(score_column, 0).desc())
            .limit(tracker.top_n)
        )
        rows = database_session.execute(query).all()
        return [dict(row._mapping) for row in rows]

    start_snapshot_time = _snapshot_at_or_before_subquery(window_start_bucket)
    start_snapshot = (
        select(VideoSnapshot)
        .join(
            start_snapshot_time,
            and_(
                VideoSnapshot.video_id == start_snapshot_time.c.video_id,
                VideoSnapshot.captured_at == start_snapshot_time.c.captured_at,
            ),
        )
        .subquery()
    )

    start_stats = select(
        start_snapshot.c.video_id.label("video_id"),
        start_snapshot.c.view_count.label("start_view_count"),
        start_snapshot.c.like_count.label("start_like_count"),
        start_snapshot.c.comment_count.label("start_comment_count"),
    ).subquery()

    joined = (
        select(
            latest_video_stats.c.video_id,
            latest_video_stats.c.title,
            latest_video_stats.c.channel_id,
            latest_video_stats.c.published_at,
            latest_video_stats.c.view_count,
            latest_video_stats.c.like_count,
            latest_video_stats.c.comment_count,
            start_stats.c.start_view_count,
            start_stats.c.start_like_count,
            start_stats.c.start_comment_count,
        )
        .outerjoin(start_stats, start_stats.c.video_id == latest_video_stats.c.video_id)
        .subquery()
    )

    if ranking_metric in (
        RankingMetric.views_delta,
        RankingMetric.likes_delta,
        RankingMetric.comments_delta,
    ):
        ending_column = {
            RankingMetric.views_delta: joined.c.view_count,
            RankingMetric.likes_delta: joined.c.like_count,
            RankingMetric.comments_delta: joined.c.comment_count,
        }[ranking_metric]
        starting_column = {
            RankingMetric.views_delta: joined.c.start_view_count,
            RankingMetric.likes_delta: joined.c.start_like_count,
            RankingMetric.comments_delta: joined.c.start_comment_count,
        }[ranking_metric]

        delta_score = func.coalesce(ending_column, 0) - func.coalesce(
            starting_column, 0
        )
        query = (
            select(
                joined.c.video_id,
                joined.c.title,
                joined.c.channel_id,
                joined.c.published_at,
                delta_score.cast(Float).label("score"),
                joined.c.view_count,
                joined.c.like_count,
                joined.c.comment_count,
            )
            .order_by(delta_score.desc())
            .limit(tracker.top_n)
        )
        rows = database_session.execute(query).all()
        return [dict(row._mapping) for row in rows]

    if ranking_metric == RankingMetric.views_velocity:
        delta_score = func.coalesce(joined.c.view_count, 0) - func.coalesce(
            joined.c.start_view_count, 0
        )
        velocity_score = delta_score / Float(window_hours)
        query = (
            select(
                joined.c.video_id,
                joined.c.title,
                joined.c.channel_id,
                joined.c.published_at,
                velocity_score.cast(Float).label("score"),
                joined.c.view_count,
                joined.c.like_count,
                joined.c.comment_count,
            )
            .order_by(velocity_score.desc())
            .limit(tracker.top_n)
        )
        rows = database_session.execute(query).all()
        return [dict(row._mapping) for row in rows]

    return []
