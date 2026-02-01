from datetime import datetime
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from yta_core.db.models import Tracker, TrackerCandidate, Video, VideoSnapshot
from yta_core.time_utils import hour_bucket, utc_now
from yta_core.youtube.client import YouTubeClient

def _parse_int(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return None

def snapshot_all_candidate_videos(database_session: Session, youtube_client: YouTubeClient) -> int:
    distinct_video_ids = database_session.execute(
        select(distinct(TrackerCandidate.video_id))
        .join(Tracker, Tracker.id == TrackerCandidate.tracker_id)
        .where(Tracker.is_active.is_(True))
    ).scalars().all()

    captured_at_bucket = hour_bucket(utc_now())
    created_snapshots_count = 0

    for batch_start in range(0, len(distinct_video_ids), 50):
        batch_video_ids = distinct_video_ids[batch_start : batch_start + 50]
        payload = youtube_client.get_videos_details(batch_video_ids)

        for item in payload.get("items", []):
            video_id = item.get("id")
            if not video_id:
                continue

            video_row = database_session.get(Video, video_id) or Video(video_id=video_id)
            snippet = item.get("snippet") or {}
            statistics = item.get("statistics") or {}
            content_details = item.get("contentDetails") or {}

            video_row.title = snippet.get("title")
            video_row.channel_id = snippet.get("channelId")
            video_row.duration_iso = content_details.get("duration")

            published_at_string = snippet.get("publishedAt")
            if isinstance(published_at_string, str):
                try:
                    video_row.published_at = datetime.fromisoformat(published_at_string.replace("Z", "+00:00"))
                except Exception:
                    pass

            database_session.add(video_row)

            snapshot_exists = database_session.execute(
                select(VideoSnapshot).where(
                    VideoSnapshot.video_id == video_id,
                    VideoSnapshot.captured_at == captured_at_bucket,
                )
            ).scalar_one_or_none()

            if snapshot_exists is not None:
                continue

            database_session.add(
                VideoSnapshot(
                    video_id=video_id,
                    captured_at=captured_at_bucket,
                    view_count=_parse_int(statistics.get("viewCount")),
                    like_count=_parse_int(statistics.get("likeCount")),
                    comment_count=_parse_int(statistics.get("commentCount")),
                )
            )
            created_snapshots_count += 1

    return created_snapshots_count
