from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from yta_api.db import get_database_session
from yta_api.schemas import TimeSeriesPoint
from yta_core.db.models import VideoSnapshot
from yta_core.time_utils import utc_now

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/{video_id}/timeseries", response_model=list[TimeSeriesPoint])
def get_timeseries(
    video_id: str,
    metric: str = "view_count",
    days: int = 7,
    database_session: Session = Depends(get_database_session),
) -> list[TimeSeriesPoint]:
    allowed_metrics = {"view_count", "like_count", "comment_count"}
    if metric not in allowed_metrics:
        raise HTTPException(status_code=400, detail="metric must be view_count|like_count|comment_count")

    since_time = utc_now() - timedelta(days=days)
    metric_column = getattr(VideoSnapshot, metric)

    rows = database_session.execute(
        select(VideoSnapshot.captured_at, metric_column)
        .where(VideoSnapshot.video_id == video_id)
        .where(VideoSnapshot.captured_at >= since_time)
        .order_by(VideoSnapshot.captured_at.asc())
    ).all()

    return [TimeSeriesPoint(captured_at=row[0], value=row[1]) for row in rows]
