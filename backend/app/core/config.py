from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ANTHROPIC_API_KEY: str
    ENVIRONMENT: str = "development"
    APP_VERSION: str = "0.1.0"
    AUTH_REQUIRED: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
