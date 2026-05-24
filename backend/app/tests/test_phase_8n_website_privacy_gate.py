from pathlib import Path

from app.scripts import verify_phase_8n_website_privacy_gate


def test_phase_8n_verifier_importable_and_files_exist():
    checks = verify_phase_8n_website_privacy_gate.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8n_privacy_and_website_statuses_pending():
    assert verify_phase_8n_website_privacy_gate.approval_statuses_pending().passed is True


def test_phase_8n_no_go_for_actual_site_embed_exists():
    assert verify_phase_8n_website_privacy_gate.no_go_documented().passed is True


def test_phase_8n_decision_state_exists():
    assert verify_phase_8n_website_privacy_gate.decision_state_documented().passed is True


def test_phase_8n_consent_text_exists():
    assert verify_phase_8n_website_privacy_gate.consent_text_documented().passed is True


def test_phase_8n_required_approval_phrase_exists():
    assert verify_phase_8n_website_privacy_gate.required_phrase_documented().passed is True


def test_phase_8n_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8n_website_privacy_gate.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8n_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8n_website_privacy_gate.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8n_all_repo_checks_pass():
    checks = verify_phase_8n_website_privacy_gate.run_checks()

    assert all(check.passed for check in checks)
