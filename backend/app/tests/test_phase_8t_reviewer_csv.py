from pathlib import Path

import pytest

from app.scripts import apply_official_content_review
from app.scripts import prepare_reviewer_decision_csv
from app.scripts import verify_phase_8t_reviewer_csv


def test_phase_8t_scripts_importable():
    assert prepare_reviewer_decision_csv.OUTPUT_PATH.name == "knowledge_review_queue_for_review.csv"
    assert verify_phase_8t_reviewer_csv.DECISION_STATE


def test_phase_8t_output_csv_exists():
    assert verify_phase_8t_reviewer_csv.reviewer_csv_exists().passed is True


def test_phase_8t_required_reviewer_columns_exist():
    assert verify_phase_8t_reviewer_csv.reviewer_columns_present().passed is True


def test_phase_8t_decision_column_not_prefilled_from_recommended_action():
    assert verify_phase_8t_reviewer_csv.recommended_action_not_copied_to_decision().passed is True


def test_phase_8t_apply_script_chooses_reviewer_csv_if_present():
    assert apply_official_content_review.select_review_csv_path() in {
        apply_official_content_review.REVIEWER_CSV_PATH,
        apply_official_content_review.FULL_LOCAL_KB_REVIEWER_CSV_PATH,
    }
    assert verify_phase_8t_reviewer_csv.apply_script_prefers_reviewer_csv().passed is True


def test_phase_8t_allowed_decision_validation():
    for decision in apply_official_content_review.ALLOWED_DECISIONS:
        assert apply_official_content_review.normalize_decision(decision) == decision

    with pytest.raises(ValueError):
        apply_official_content_review.normalize_decision("AUTO_APPROVE")


def test_phase_8t_prepare_csv_leaves_decision_empty(tmp_path: Path):
    source = tmp_path / "source.csv"
    output = tmp_path / "for_review.csv"
    source.write_text(
        "source_key,title,category,status,review_required,recommended_action\n"
        "source-1,Finance guidance,finance,review_required,true,APPROVE\n",
        encoding="utf-8",
    )

    summary = prepare_reviewer_decision_csv.prepare_reviewer_csv(source, output)
    headers, rows = verify_phase_8t_reviewer_csv.load_reviewer_rows(output)

    assert summary["rows_written"] == 1
    assert "decision" in headers
    assert rows[0]["recommended_action"] == "APPROVE"
    assert rows[0]["decision"] == ""
    assert "NEEDS_OFFICIAL_SOURCE" in rows[0]["decision_guidance"]


def test_phase_8t_no_forbidden_secret_patterns(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8t_reviewer_csv.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8t_decision_state_documented():
    assert verify_phase_8t_reviewer_csv.decision_state_documented().passed is True


def test_phase_8t_all_repo_checks_pass():
    checks = verify_phase_8t_reviewer_csv.run_checks()

    assert all(check.passed for check in checks)
