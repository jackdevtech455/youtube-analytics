from sqlalchemy import select
from sqlalchemy.orm import Session
from yta_core.db.models import Tracker, TrackerCandidate, Video
from yta_core.time_utils import utc_now

def ensure_video_rows_exist(database_session: Session, video_ids: list[str]) -> None:
    for video_id in video_ids:
        if database_session.get(Video, video_id) is None:
            database_session.add(Video(video_id=video_id))
    database_session.flush()

def upsert_tracker_candidates(database_session: Session, tracker: Tracker, candidate_video_ids: list[str]) -> None:
    current_time = utc_now()
    ensure_video_rows_exist(database_session, candidate_video_ids)

    for index, video_id in enumerate(candidate_video_ids):
        existing_candidate = database_session.execute(
            select(TrackerCandidate).where(
                TrackerCandidate.tracker_id == tracker.id,
                TrackerCandidate.video_id == video_id,
            )
        ).scalar_one_or_none()

        if existing_candidate is None:
            database_session.add(
                TrackerCandidate(
                    tracker_id=tracker.id,
                    video_id=video_id,
                    source_rank=index + 1,
                    first_seen_at=current_time,
                    last_seen_at=current_time,
                )
            )
        else:
            existing_candidate.last_seen_at = current_time
            existing_candidate.source_rank = index + 1
            database_session.add(existing_candidate)

    candidates_sorted_by_recency = database_session.execute(
        select(TrackerCandidate)
        .where(TrackerCandidate.tracker_id == tracker.id)
        .order_by(TrackerCandidate.last_seen_at.desc())
    ).scalars().all()

    if len(candidates_sorted_by_recency) > tracker.candidate_pool_size:
        for candidate_to_remove in candidates_sorted_by_recency[tracker.candidate_pool_size :]:
            database_session.delete(candidate_to_remove)
