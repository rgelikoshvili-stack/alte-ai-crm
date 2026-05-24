from pathlib import Path

import pytest

from app.scripts import apply_official_content_review
from app.scripts import verify_official_content_review_apply
from app.scripts import verify_phase_8s_content_review_apply_docs


def test_phase_8s_scripts_importable():
    assert apply_official_content_review.ALLOWED_DECISIONS
    assert verify_official_content_review_apply.SENSITIVE_SOURCE_KEYS
    assert verify_phase_8s_content_review_apply_docs.DECISION_STATES


def test_phase_8s_apply_plan_and_result_docs_exist():
    checks = verify_phase_8s_content_review_apply_docs.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8s_allowed_decisions_recognized():
    for decision in apply_official_content_review.ALLOWED_DECISIONS:
        assert apply_official_content_review.normalize_decision(decision.lower()) == decision


def test_phase_8s_invalid_decisions_rejected():
    with pytest.raises(ValueError):
        apply_official_content_review.normalize_decision("approve_all")


def test_phase_8s_missing_decision_normalizes_to_none():
    assert apply_official_content_review.normalize_decision("") is None
    assert apply_official_content_review.normalize_decision(None) is None


def test_phase_8s_apply_result_records_dry_run():
    assert verify_phase_8s_content_review_apply_docs.apply_result_records_dry_run().passed is True


def test_phase_8s_apply_result_records_apply_status():
    assert verify_phase_8s_content_review_apply_docs.apply_result_records_apply_status().passed is True


def test_phase_8s_decision_state_exists():
    assert verify_phase_8s_content_review_apply_docs.decision_state_documented().passed is True


def test_phase_8s_no_false_public_launch_complete():
    assert verify_phase_8s_content_review_apply_docs.public_launch_not_falsely_complete().passed is True


def test_phase_8s_forbidden_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8s_content_review_apply_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8s_database_url_secret_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("postgresql+asyncpg://user:password@example/db", encoding="utf-8")

    check = verify_phase_8s_content_review_apply_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8s_all_repo_checks_pass():
    checks = verify_phase_8s_content_review_apply_docs.run_checks()

    assert all(check.passed for check in checks)
