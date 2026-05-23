from pathlib import Path

from app.scripts import verify_phase_8f_secrets_prep


def test_phase_8f_secrets_prep_verifier_importable_and_required_files_exist():
    checks = verify_phase_8f_secrets_prep.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8f_secrets_prep_approval_gate_pending():
    assert verify_phase_8f_secrets_prep.approval_gate_pending().passed is True


def test_phase_8f_secrets_prep_decision_remains_no_go():
    assert verify_phase_8f_secrets_prep.decision_remains_no_go().passed is True


def test_phase_8f_secrets_prep_secret_pattern_detection(tmp_path: Path):
    secret_file = tmp_path / "bad.md"
    secret_file.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_phase_8f_secrets_prep.no_secret_patterns([secret_file])

    assert check.passed is False


def test_phase_8f_secrets_prep_real_database_url_detection(tmp_path: Path):
    secret_file = tmp_path / "bad-db.md"
    secret_file.write_text(
        "DATABASE_URL=postgresql+asyncpg://alte_app:realpassword@db.example.com:5432/alte_ai_crm",
        encoding="utf-8",
    )

    check = verify_phase_8f_secrets_prep.no_secret_patterns([secret_file])

    assert check.passed is False


def test_phase_8f_secrets_prep_all_repo_checks_pass():
    checks = verify_phase_8f_secrets_prep.run_checks()

    assert all(check.passed for check in checks)
