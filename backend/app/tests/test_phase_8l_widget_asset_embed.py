from pathlib import Path

from app.scripts import verify_phase_8l_widget_asset_embed


def test_phase_8l_verifier_importable_and_required_files_exist():
    checks = verify_phase_8l_widget_asset_embed.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8l_backend_url_present():
    assert verify_phase_8l_widget_asset_embed.production_backend_url_present().passed is True


def test_phase_8l_snippets_have_correct_domains_and_languages():
    assert verify_phase_8l_widget_asset_embed.snippets_have_correct_domains().passed is True


def test_phase_8l_actual_embed_remains_blocked():
    assert verify_phase_8l_widget_asset_embed.actual_embed_blocked_unless_approved().passed is True


def test_phase_8l_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_phase_8l_widget_asset_embed.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8l_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8l_widget_asset_embed.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8l_all_repo_checks_pass():
    checks = verify_phase_8l_widget_asset_embed.run_checks()

    assert all(check.passed for check in checks)
