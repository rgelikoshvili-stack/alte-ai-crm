from pathlib import Path

from app.scripts import verify_phase_8p_api_smoke_docs


def test_phase_8p_verifier_importable_and_files_exist():
    checks = verify_phase_8p_api_smoke_docs.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8p_smoke_result_doc_exists_and_records_no_contact_flow():
    assert verify_phase_8p_api_smoke_docs.smoke_result_documents_safety().passed is True


def test_phase_8p_approval_gate_pending():
    assert verify_phase_8p_api_smoke_docs.approval_gate_pending().passed is True


def test_phase_8p_decision_state_documented():
    assert verify_phase_8p_api_smoke_docs.decision_state_documented().passed is True


def test_phase_8p_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8p_api_smoke_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8p_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8p_api_smoke_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8p_all_repo_checks_pass():
    checks = verify_phase_8p_api_smoke_docs.run_checks()

    assert all(check.passed for check in checks)
