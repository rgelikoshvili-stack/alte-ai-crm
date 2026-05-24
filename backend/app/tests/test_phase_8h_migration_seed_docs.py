from pathlib import Path

from app.scripts import verify_phase_8h_migration_seed_docs


def test_phase_8h_verifier_importable():
    checks = verify_phase_8h_migration_seed_docs.run_checks()

    assert checks


def test_phase_8h_docs_record_migration_and_seed_status():
    assert verify_phase_8h_migration_seed_docs.migration_seed_status_documented().passed is True


def test_phase_8h_no_go_remains():
    assert verify_phase_8h_migration_seed_docs.decision_remains_no_go().passed is True


def test_phase_8h_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_phase_8h_migration_seed_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_phase_8h_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text(
        "postgresql+asyncpg://alte_app:realpassword@db.example.com:5432/alte_ai_crm",
        encoding="utf-8",
    )

    check = verify_phase_8h_migration_seed_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_phase_8h_all_repo_checks_pass():
    checks = verify_phase_8h_migration_seed_docs.run_checks()

    assert all(check.passed for check in checks)
