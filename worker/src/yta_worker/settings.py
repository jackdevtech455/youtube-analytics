from pydantic import Field
from pydantic_settings import SettingsConfigDict
from yta_core.settings import CoreSettings


class WorkerSettings(CoreSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    snapshot_interval_minutes: int = Field(
        default=60, alias="SNAPSHOT_INTERVAL_MINUTES"
    )
    channel_discovery_interval_minutes: int = Field(
        default=60, alias="CHANNEL_DISCOVERY_INTERVAL_MINUTES"
    )
    search_discovery_interval_minutes: int = Field(
        default=1440, alias="SEARCH_DISCOVERY_INTERVAL_MINUTES"
    )

    poll_interval_seconds: int = 30
