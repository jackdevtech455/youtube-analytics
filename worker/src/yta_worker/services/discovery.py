from sqlalchemy.orm import Session
from yta_core.db.models import Tracker, TrackerType
from yta_core.youtube.client import YouTubeClient
from yta_worker.services.candidates import upsert_tracker_candidates

def run_tracker_discovery(database_session: Session, youtube_client: YouTubeClient, tracker: Tracker) -> None:
    if tracker.type == TrackerType.channel:
        if not tracker.channel_id:
            return
        uploads_playlist_id = youtube_client.get_uploads_playlist_id(tracker.channel_id)
        if not uploads_playlist_id:
            return
        candidate_video_ids = youtube_client.list_playlist_video_ids(uploads_playlist_id, tracker.candidate_pool_size)
        upsert_tracker_candidates(database_session, tracker, candidate_video_ids)
        return

    if tracker.type == TrackerType.search:
        if not tracker.search_query:
            return
        candidate_video_ids = youtube_client.search_video_ids(tracker.search_query, tracker.candidate_pool_size)
        upsert_tracker_candidates(database_session, tracker, candidate_video_ids)
