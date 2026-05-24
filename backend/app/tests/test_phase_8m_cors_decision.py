from pathlib import Path

from app.scripts import verify_phase_8m_cors_decision


def test_phase_8m_verifier_importable_and_files_exist():
    checks = verify_phase_8m_cors_decision.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8m_cors_decision_doc_exists_and_is_valid():
    assert verify_phase_8m_cors_decision.cors_decision_doc_valid().passed is True


def test_phase_8m_allowed_domains_and_localhost_blocked_recorded():
    assert verify_phase_8m_cors_decision.smoke_results_documented().passed is True


def test_phase_8m_decision_state_pending_real_domain_smoke():
    assert verify_phase_8m_cors_decision.decision_state_documented().passed is True


def test_phase_8m_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8m_cors_decision.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8m_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8m_cors_decision.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8m_all_repo_checks_pass():
    checks = verify_phase_8m_cors_decision.run_checks()

    assert all(check.passed for check in checks)
