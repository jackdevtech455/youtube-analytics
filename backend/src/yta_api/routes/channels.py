from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from yta_api.schemas_channels import ChannelMeta
from yta_api.settings import ApiSettings
from yta_core.youtube.client import YouTubeClient

router = APIRouter(prefix="/channels", tags=["channels"])

_channel_meta_cache: dict[str, tuple[datetime, ChannelMeta]] = {}
_cache_ttl = timedelta(hours=6)

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _normalize_handle(custom_url: str | None) -> str | None:
    if not custom_url:
        return None
    stripped = custom_url.strip()
    if not stripped:
        return None
    return stripped if stripped.startswith("@") else f"@{stripped}"

@router.get("/meta", response_model=list[ChannelMeta])
def get_channels_meta(ids: str) -> list[ChannelMeta]:
    channel_ids = [channel_id.strip() for channel_id in ids.split(",") if channel_id.strip()]
    if not channel_ids:
        raise HTTPException(status_code=400, detail="ids must be a comma-separated list of channel ids")

    now = _utc_now()

    cached_results: list[ChannelMeta] = []
    missing_channel_ids: list[str] = []

    for channel_id in channel_ids:
        cached = _channel_meta_cache.get(channel_id)
        if cached and cached[0] > now:
            cached_results.append(cached[1])
        else:
            missing_channel_ids.append(channel_id)

    fetched_results: list[ChannelMeta] = []
    if missing_channel_ids:
        api_settings = ApiSettings()
        youtube_client = YouTubeClient(api_settings.youtube_api_key)

        for batch_start in range(0, len(missing_channel_ids), 50):
            batch_ids = missing_channel_ids[batch_start : batch_start + 50]
            items = youtube_client.get_channels_metadata(batch_ids)

            returned_ids: set[str] = set()

            for item in items:
                channel_id = item.get("id")
                snippet = item.get("snippet") or {}

                if not isinstance(channel_id, str):
                    continue

                thumbnails = snippet.get("thumbnails") or {}
                default_thumb = thumbnails.get("default") or {}
                thumbnail_url = default_thumb.get("url")

                meta = ChannelMeta(
                    channel_id=channel_id,
                    title=snippet.get("title"),
                    handle=_normalize_handle(snippet.get("customUrl")),
                    thumbnail_url=thumbnail_url if isinstance(thumbnail_url, str) else None,
                )

                _channel_meta_cache[channel_id] = (now + _cache_ttl, meta)
                fetched_results.append(meta)
                returned_ids.add(channel_id)

            for channel_id in batch_ids:
                if channel_id not in returned_ids:
                    meta = ChannelMeta(channel_id=channel_id)
                    _channel_meta_cache[channel_id] = (now + timedelta(minutes=30), meta)
                    fetched_results.append(meta)

    all_results = {meta.channel_id: meta for meta in (cached_results + fetched_results)}
    return [all_results[channel_id] for channel_id in channel_ids if channel_id in all_results]
