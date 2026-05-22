from app.core.config import get_settings
from app.scripts import ai_direct_dry_run, claude_live_smoke


def test_ai_diagnostics_does_not_expose_secrets(client):
    response = client.get("/diagnostics/ai")

    assert response.status_code == 200
    data = response.json()
    assert "has_anthropic_key" in data
    assert "anthropic_key_is_placeholder" in data
    assert "test-anthropic-key" not in str(data)
    assert "ANTHROPIC_API_KEY" not in str(data)


def test_ai_diagnostics_reports_placeholder_key(client):
    response = client.get("/diagnostics/ai")

    assert response.status_code == 200
    data = response.json()
    assert data["has_anthropic_key"] is True
    assert data["anthropic_key_is_placeholder"] is True
    assert data["mock_mode"] is True
    assert data["claude_enabled"] is False


def test_claude_live_smoke_refuses_mock_mode():
    allowed, reason = claude_live_smoke.validate_claude_live_settings()

    assert allowed is False
    assert "AI_PROVIDER must be claude" in reason


def test_claude_live_smoke_refuses_placeholder_key(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "local-placeholder")
    get_settings.cache_clear()
    try:
        allowed, reason = claude_live_smoke.validate_claude_live_settings()
    finally:
        get_settings.cache_clear()

    assert allowed is False
    assert "placeholder" in reason


def test_ai_direct_dry_run_works_in_mock_mode(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    get_settings.cache_clear()
    try:
        result = ai_direct_dry_run.run_dry_run()
    finally:
        get_settings.cache_clear()

    assert result["passed"] is True
    assert result["provider"] == "mock"
    assert "reply_preview" in result
