from typing import Set

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    BOT_API_TOKEN: SecretStr
    ADMINS_TELEGRAM_ID: Set[int] = {}


settings = Settings()
