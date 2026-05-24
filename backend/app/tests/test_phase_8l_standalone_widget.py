from pathlib import Path

from app.scripts import verify_phase_8l_standalone_widget


def test_phase_8l_standalone_verifier_importable_and_files_exist():
    checks = verify_phase_8l_standalone_widget.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8l_standalone_demo_content_valid():
    assert verify_phase_8l_standalone_widget.standalone_demo_content_valid().passed is True


def test_phase_8l_transfer_package_documented():
    assert verify_phase_8l_standalone_widget.transfer_package_documented().passed is True


def test_phase_8l_decision_state_pending_actual_site_embed():
    assert verify_phase_8l_standalone_widget.decision_state_documented().passed is True


def test_phase_8l_standalone_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8l_standalone_widget.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8l_standalone_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8l_standalone_widget.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8l_standalone_all_repo_checks_pass():
    checks = verify_phase_8l_standalone_widget.run_checks()

    assert all(check.passed for check in checks)
