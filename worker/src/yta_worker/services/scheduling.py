from datetime import datetime, timedelta
from yta_core.time_utils import hour_bucket

def is_due(current_time: datetime, scheduled_time: datetime | None) -> bool:
    return scheduled_time is not None and scheduled_time <= current_time

def next_time_for_interval(current_time: datetime, interval_minutes: int) -> datetime:
    return hour_bucket(current_time) + timedelta(minutes=interval_minutes)

def stagger_daily_discovery(tracker_id: int, current_time: datetime) -> datetime:
    hour_offset = tracker_id % 24
    return hour_bucket(current_time) + timedelta(hours=hour_offset)
