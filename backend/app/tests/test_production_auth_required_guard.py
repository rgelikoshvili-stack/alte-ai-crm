import pytest

from app.core.config import Settings, validate_security_settings


def make_settings(environment: str, auth_required: bool) -> Settings:
    return Settings(
        DATABASE_URL="sqlite+aiosqlite://",
        JWT_SECRET="test-secret",
        ANTHROPIC_API_KEY="test-anthropic-key",
        ENVIRONMENT=environment,
        AUTH_REQUIRED=auth_required,
    )


def test_production_requires_auth_enabled():
    with pytest.raises(RuntimeError, match="AUTH_REQUIRED must be true"):
        validate_security_settings(make_settings("production", False))


def test_production_with_auth_enabled_passes():
    validate_security_settings(make_settings("production", True))


def test_test_environment_can_keep_auth_disabled():
    validate_security_settings(make_settings("test", False))
