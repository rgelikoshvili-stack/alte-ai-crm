from pathlib import Path

from app.scripts import verify_phase_8j_widget_embed_docs


def test_phase_8j_required_files_exist():
    checks = verify_phase_8j_widget_embed_docs.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8j_embed_docs_record_backend_and_domains():
    assert verify_phase_8j_widget_embed_docs.embed_docs_record_backend_and_domains().passed is True


def test_phase_8j_smoke_and_rollback_documented():
    assert verify_phase_8j_widget_embed_docs.smoke_and_rollback_documented().passed is True


def test_phase_8j_website_privacy_remains_pending():
    assert verify_phase_8j_widget_embed_docs.website_privacy_pending().passed is True


def test_phase_8j_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_phase_8j_widget_embed_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_phase_8j_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text(
        "postgresql+asyncpg://alte_app:realpassword@db.example.com:5432/alte_ai_crm",
        encoding="utf-8",
    )

    check = verify_phase_8j_widget_embed_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_phase_8j_all_repo_checks_pass():
    checks = verify_phase_8j_widget_embed_docs.run_checks()

    assert all(check.passed for check in checks)
