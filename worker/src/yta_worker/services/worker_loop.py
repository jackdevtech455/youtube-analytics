import time
from sqlalchemy import select
from sqlalchemy.orm import Session

from yta_core.db.session import SessionFactory
from yta_core.db.models import Tracker, TrackerType, VideoSnapshot
from yta_core.time_utils import hour_bucket, utc_now
from yta_core.youtube.client import YouTubeClient
from yta_worker.settings import WorkerSettings
from yta_worker.services.discovery import run_tracker_discovery
from yta_worker.services.scheduling import (
    is_due,
    next_time_for_interval,
    stagger_daily_discovery,
)
from yta_worker.services.snapshots import snapshot_all_candidate_videos


def ensure_tracker_schedule_fields(database_session: Session, tracker: Tracker) -> None:
    current_time = utc_now()

    if tracker.next_snapshot_at is None:
        tracker.next_snapshot_at = hour_bucket(current_time)

    if tracker.next_discovery_at is None:
        tracker.next_discovery_at = (
            stagger_daily_discovery(tracker.id, current_time)
            if tracker.type == TrackerType.search
            else hour_bucket(current_time)
        )

    database_session.add(tracker)


def should_run_hourly_snapshot(database_session: Session) -> bool:
    current_bucket = hour_bucket(utc_now())
    latest_snapshot_time = database_session.execute(
        select(VideoSnapshot.captured_at)
        .order_by(VideoSnapshot.captured_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    return latest_snapshot_time is None or latest_snapshot_time < current_bucket


def run_worker_loop(worker_settings: WorkerSettings) -> None:
    youtube_client = YouTubeClient(worker_settings.youtube_api_key)

    while True:
        try:
            with SessionFactory() as database_session:
                active_trackers = (
                    database_session.execute(
                        select(Tracker).where(Tracker.is_active.is_(True))
                    )
                    .scalars()
                    .all()
                )

                for tracker in active_trackers:
                    ensure_tracker_schedule_fields(database_session, tracker)

                database_session.commit()

            with SessionFactory() as database_session:
                current_time = utc_now()
                active_trackers = (
                    database_session.execute(
                        select(Tracker).where(Tracker.is_active.is_(True))
                    )
                    .scalars()
                    .all()
                )

                for tracker in active_trackers:
                    if not is_due(current_time, tracker.next_discovery_at):
                        continue

                    run_tracker_discovery(database_session, youtube_client, tracker)

                    interval_minutes = (
                        worker_settings.search_discovery_interval_minutes
                        if tracker.type == TrackerType.search
                        else worker_settings.channel_discovery_interval_minutes
                    )
                    tracker.next_discovery_at = next_time_for_interval(
                        current_time, interval_minutes
                    )
                    database_session.add(tracker)

                database_session.commit()

            with SessionFactory() as database_session:
                if should_run_hourly_snapshot(database_session):
                    snapshot_all_candidate_videos(database_session, youtube_client)
                    database_session.commit()

        except Exception as error:
            print(f"[worker] tick error: {error}", flush=True)

        time.sleep(worker_settings.poll_interval_seconds)
