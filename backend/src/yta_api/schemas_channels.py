from pydantic import BaseModel


class ChannelMeta(BaseModel):
    channel_id: str
    title: str | None = None
    handle: str | None = None
    thumbnail_url: str | None = None
