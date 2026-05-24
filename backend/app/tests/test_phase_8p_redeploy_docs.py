from pathlib import Path

from app.scripts import verify_phase_8p_redeploy_docs


def test_phase_8p_redeploy_verifier_importable():
    checks = verify_phase_8p_redeploy_docs.run_checks()

    assert checks


def test_phase_8p_redeploy_image_tag_recorded():
    assert verify_phase_8p_redeploy_docs.image_tag_recorded().passed is True


def test_phase_8p_redeploy_status_recorded():
    assert verify_phase_8p_redeploy_docs.redeploy_status_recorded().passed is True


def test_phase_8p_redeploy_contact_flow_not_run():
    assert verify_phase_8p_redeploy_docs.contact_flow_not_run_recorded().passed is True


def test_phase_8p_redeploy_decision_state_documented():
    assert verify_phase_8p_redeploy_docs.decision_state_documented().passed is True


def test_phase_8p_redeploy_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8p_redeploy_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8p_redeploy_database_url_secret_detection(tmp_path: Path):
    sample = tmp_path / "bad-url.md"
    sample.write_text("postgresql+asyncpg://alte_app:secret@example.com/db", encoding="utf-8")

    check = verify_phase_8p_redeploy_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8p_redeploy_all_repo_checks_pass():
    checks = verify_phase_8p_redeploy_docs.run_checks()

    assert all(check.passed for check in checks)
