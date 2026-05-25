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
    AI_MODEL: str = "claude-sonnet-4-5-20250929"
    AI_TIMEOUT_SECONDS: int = 20
    AI_CONFIDENCE_THRESHOLD: float = 0.70
    AI_MAX_TOKENS: int = 1200
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5500,http://127.0.0.1:5500"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def validate_security_settings(settings: Settings) -> None:
    if settings.ENVIRONMENT.lower().strip() == "production" and not settings.AUTH_REQUIRED:
        raise RuntimeError("AUTH_REQUIRED must be true when ENVIRONMENT=production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
