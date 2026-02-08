from typing import Iterable
from urllib.parse import urlparse

import requests

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY must be set.")
        self._api_key = api_key

    def _get(self, path: str, params: dict[str, str | int | None]) -> dict:
        request_params: dict[str, str | int] = {
            k: v for k, v in params.items() if v is not None
        }
        request_params["key"] = self._api_key
        response = requests.get(
            f"{YOUTUBE_API_BASE_URL}/{path}", params=request_params, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def resolve_channel_id(self, channel_identifier: str) -> str | None:
        """Resolve a channel identifier into a UC... channel ID.

        Accepts:
        - UC... channel id
        - @handle
        - handle without @
        - youtube URLs (/@handle, /channel/UC..., etc.)
        Returns UC... channel id or None.
        """
        raw_value = channel_identifier.strip()
        if not raw_value:
            return None

        if raw_value.startswith("UC") and len(raw_value) >= 10:
            return raw_value

        if raw_value.startswith("http://") or raw_value.startswith("https://"):
            parsed_url = urlparse(raw_value)
            path = (parsed_url.path or "").strip("/")

            if path.startswith("channel/"):
                possible_id = path.split("/", 1)[1]
                if possible_id.startswith("UC"):
                    return possible_id

            if path.startswith("@"):
                raw_value = path
            elif path:
                raw_value = path.split("/")[-1]

        handle_value = raw_value if raw_value.startswith("@") else f"@{raw_value}"

        payload = self._get(
            "channels", {"part": "id", "forHandle": handle_value, "maxResults": 1}
        )
        items = payload.get("items", [])
        if not items:
            return None

        channel_id = items[0].get("id")
        return channel_id if isinstance(channel_id, str) else None

    def get_uploads_playlist_id(self, channel_id: str) -> str | None:
        payload = self._get(
            "channels", {"part": "contentDetails", "id": channel_id, "maxResults": 1}
        )
        items = payload.get("items", [])
        if not items:
            return None
        related_playlists = (
            items[0].get("contentDetails", {}).get("relatedPlaylists", {})
        )
        return related_playlists.get("uploads")

    def list_playlist_video_ids(self, playlist_id: str, limit: int) -> list[str]:
        collected_video_ids: list[str] = []
        next_page_token: str | None = None

        while len(collected_video_ids) < limit:
            payload = self._get(
                "playlistItems",
                {
                    "part": "contentDetails",
                    "playlistId": playlist_id,
                    "maxResults": 50,
                    "pageToken": next_page_token,
                },
            )
            for item in payload.get("items", []):
                video_id = item.get("contentDetails", {}).get("videoId")
                if video_id:
                    collected_video_ids.append(video_id)
                if len(collected_video_ids) >= limit:
                    break

            next_page_token = payload.get("nextPageToken")
            if not next_page_token:
                break

        return collected_video_ids

    def search_video_ids(self, query: str, limit: int) -> list[str]:
        collected_video_ids: list[str] = []
        next_page_token: str | None = None

        while len(collected_video_ids) < limit:
            payload = self._get(
                "search",
                {
                    "part": "id",
                    "q": query,
                    "type": "video",
                    "maxResults": 50,
                    "pageToken": next_page_token,
                    "order": "viewCount",
                },
            )
            for item in payload.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                if video_id:
                    collected_video_ids.append(video_id)
                if len(collected_video_ids) >= limit:
                    break

            next_page_token = payload.get("nextPageToken")
            if not next_page_token:
                break

        return collected_video_ids

    def get_videos_details(self, video_ids: Iterable[str]) -> dict:
        video_id_list = list(video_ids)
        if not video_id_list:
            return {"items": []}

        return self._get(
            "videos",
            {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(video_id_list[:50]),
                "maxResults": 50,
            },
        )

    def get_channels_metadata(self, channel_ids: Iterable[str]) -> list[dict]:
        channel_id_list = [
            channel_id.strip()
            for channel_id in channel_ids
            if channel_id and channel_id.strip()
        ]
        if not channel_id_list:
            return []

        payload = self._get(
            "channels",
            {"part": "snippet", "id": ",".join(channel_id_list[:50]), "maxResults": 50},
        )
        items = payload.get("items", [])
        return items if isinstance(items, list) else []
