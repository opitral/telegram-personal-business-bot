from typing import Set, List

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    BOT_API_TOKEN: SecretStr
    ADMINS_TELEGRAM_ID: List[int] = {}


settings = Settings()
