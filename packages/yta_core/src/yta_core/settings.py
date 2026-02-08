from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    youtube_api_key: str = Field(default="", alias="YOUTUBE_API_KEY")
