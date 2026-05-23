from app.core.config import get_settings
from app.scripts import startup_check


def test_startup_check_does_not_expose_database_url_or_secrets(monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:super-secret-pass@db:5432/alte_ai_crm")
    monkeypatch.setenv("JWT_SECRET", "very-secret-jwt")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-secret-value")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CORS_ORIGINS", "https://alte.edu.ge,https://join.alte.edu.ge")
    get_settings.cache_clear()
    try:
        result = startup_check.validate_startup()
        startup_check.main()
        output = capsys.readouterr().out
    finally:
        get_settings.cache_clear()

    serialized = f"{result} {output}"
    assert "super-secret-pass" not in serialized
    assert "very-secret-jwt" not in serialized
    assert "sk-test-secret-value" not in serialized
    assert "postgresql+asyncpg://" not in serialized
    assert "database_type=postgresql" in output


def test_startup_check_fails_placeholder_claude_key_in_production(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/alte_ai_crm")
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "local-placeholder")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CORS_ORIGINS", "https://alte.edu.ge")
    get_settings.cache_clear()
    try:
        result = startup_check.validate_startup()
    finally:
        get_settings.cache_clear()

    assert result["passed"] is False
    assert any(check["name"] == "ANTHROPIC_API_KEY valid for Claude" and not check["passed"] for check in result["checks"])


def test_startup_check_passes_with_mocked_production_safe_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/alte_ai_crm")
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CORS_ORIGINS", "https://alte.edu.ge,https://join.alte.edu.ge")
    get_settings.cache_clear()
    try:
        result = startup_check.validate_startup()
    finally:
        get_settings.cache_clear()

    assert result["passed"] is True
    assert result["database_type"] == "postgresql"
