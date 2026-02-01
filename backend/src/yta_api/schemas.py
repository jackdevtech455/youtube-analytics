from datetime import datetime
from pydantic import BaseModel, Field
from yta_core.db.models import RankingMetric, TrackerType

class TrackerCreate(BaseModel):
    type: TrackerType
    channel_id: str | None = None
    search_query: str | None = None
    top_n: int = Field(default=20, ge=1, le=200)
    candidate_pool_size: int = Field(default=200, ge=20, le=1000)
    ranking_metric: RankingMetric = RankingMetric.views
    ranking_window_hours: int | None = Field(default=None, ge=1, le=24 * 90)

class TrackerPatch(BaseModel):
    top_n: int | None = Field(default=None, ge=1, le=200)
    candidate_pool_size: int | None = Field(default=None, ge=20, le=1000)
    ranking_metric: RankingMetric | None = None
    ranking_window_hours: int | None = Field(default=None, ge=1, le=24 * 90)
    is_active: bool | None = None

class TrackerOut(BaseModel):
    id: int
    owner_user_id: int
    type: TrackerType
    channel_id: str | None
    search_query: str | None
    top_n: int
    candidate_pool_size: int
    ranking_metric: RankingMetric
    ranking_window_hours: int | None
    is_active: bool
    created_at: datetime

class VideoTopItem(BaseModel):
    video_id: str
    title: str | None
    channel_id: str | None
    published_at: datetime | None
    score: float
    latest_view_count: int | None
    latest_like_count: int | None
    latest_comment_count: int | None

class TimeSeriesPoint(BaseModel):
    captured_at: datetime
    value: int | None
