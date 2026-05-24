from pathlib import Path

from app.scripts import export_knowledge_review_queue
from app.scripts import verify_phase_8r_official_content_review


def test_phase_8r_verifier_importable_and_files_exist():
    checks = verify_phase_8r_official_content_review.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8r_public_answer_policy_contains_conservative_rules():
    assert verify_phase_8r_official_content_review.public_answer_policy_conservative().passed is True


def test_phase_8r_review_status_pending():
    assert verify_phase_8r_official_content_review.review_status_pending().passed is True


def test_phase_8r_decision_state_documented():
    assert verify_phase_8r_official_content_review.decision_state_documented().passed is True


def test_phase_8r_export_script_importable():
    assert export_knowledge_review_queue.REPORT_PATH.name == "knowledge_review_queue.csv"
    assert export_knowledge_review_queue.preview("a " * 200, limit=10) == "a a a a a "


def test_phase_8r_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8r_official_content_review.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8r_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8r_official_content_review.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8r_all_repo_checks_pass():
    checks = verify_phase_8r_official_content_review.run_checks()

    assert all(check.passed for check in checks)
