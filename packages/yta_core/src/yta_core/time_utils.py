from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hour_bucket(datetime_value: datetime) -> datetime:
    return datetime_value.replace(minute=0, second=0, microsecond=0)
