from pathlib import Path

from app.scripts import standalone_chatbot_api_smoke, verify_phase_8o_standalone_chatbot


def test_phase_8o_verifier_importable_and_files_exist():
    checks = verify_phase_8o_standalone_chatbot.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8o_seed_json_valid():
    assert verify_phase_8o_standalone_chatbot.seed_json_valid().passed is True


def test_phase_8o_standalone_page_valid():
    assert verify_phase_8o_standalone_chatbot.standalone_page_valid().passed is True


def test_phase_8o_smoke_script_importable_and_valid():
    assert standalone_chatbot_api_smoke.DEFAULT_BASE_URL == verify_phase_8o_standalone_chatbot.BACKEND_URL
    assert verify_phase_8o_standalone_chatbot.smoke_script_valid().passed is True


def test_phase_8o_runbooks_documented():
    assert verify_phase_8o_standalone_chatbot.runbooks_documented().passed is True


def test_phase_8o_decision_state_exists():
    assert verify_phase_8o_standalone_chatbot.decision_state_documented().passed is True


def test_phase_8o_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8o_standalone_chatbot.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8o_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8o_standalone_chatbot.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8o_all_repo_checks_pass():
    checks = verify_phase_8o_standalone_chatbot.run_checks()

    assert all(check.passed for check in checks)
