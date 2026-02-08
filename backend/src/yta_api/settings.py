from pydantic import Field
from pydantic_settings import SettingsConfigDict
from yta_core.settings import CoreSettings


class ApiSettings(CoreSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])
