from pathlib import Path

from app.scripts import verify_phase_8p_no_contact_guard_docs


def test_phase_8p_no_contact_guard_verifier_importable():
    checks = verify_phase_8p_no_contact_guard_docs.run_checks()

    assert checks


def test_phase_8p_no_contact_guard_docs_record_issue_fix_and_redeploy():
    check = verify_phase_8p_no_contact_guard_docs.docs_record_issue_fix_and_redeploy()

    assert check.passed is True


def test_phase_8p_no_contact_guard_decision_state_documented():
    check = verify_phase_8p_no_contact_guard_docs.decision_state_documented()

    assert check.passed is True


def test_phase_8p_no_contact_guard_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8p_no_contact_guard_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8p_no_contact_guard_database_url_secret_detection(tmp_path: Path):
    sample = tmp_path / "bad-url.md"
    sample.write_text("postgresql+asyncpg://alte_app:secret@example.com/db", encoding="utf-8")

    check = verify_phase_8p_no_contact_guard_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8p_no_contact_guard_all_repo_checks_pass():
    checks = verify_phase_8p_no_contact_guard_docs.run_checks()

    assert all(check.passed for check in checks)
