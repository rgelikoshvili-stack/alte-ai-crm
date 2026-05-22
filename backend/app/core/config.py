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
    AI_PROVIDER: str = "mock"
    AI_MODEL: str = "claude-sonnet-4-20250514"
    AI_TIMEOUT_SECONDS: int = 20
    AI_CONFIDENCE_THRESHOLD: float = 0.70
    AI_MAX_TOKENS: int = 1200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
