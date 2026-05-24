from app.scripts import validate_human_reviewer_decisions
from app.scripts import verify_phase_9a_reviewer_package


def test_phase_9a_scripts_importable():
    assert validate_human_reviewer_decisions.REVIEW_CSV.name == "alte_kb_human_review_decisions.csv"
    assert verify_phase_9a_reviewer_package.DECISION_STATE


def test_reviewer_package_files_exist():
    for check in verify_phase_9a_reviewer_package.required_files_exist():
        assert check.passed, check.detail


def test_decision_column_exists():
    headers, rows = verify_phase_9a_reviewer_package.read_decision_rows()
    assert rows
    assert "decision" in headers


def test_decision_not_prefilled_from_recommended_action():
    checks = verify_phase_9a_reviewer_package.reviewer_csv_valid()
    copied_check = next(check for check in checks if check.name == "recommended_review_action not copied into decision")
    assert copied_check.passed is True


def test_validation_passes_with_empty_decisions_as_pending():
    result = validate_human_reviewer_decisions.validate()
    assert result.status == "PENDING_HUMAN_DECISIONS"
    assert result.empty_decisions == result.total_rows
    assert not result.has_errors


def test_phase_9a_decision_state_exists():
    assert verify_phase_9a_reviewer_package.decision_state_documented().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9a_reviewer_package.public_launch_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9a_reviewer_package.no_forbidden_patterns().passed is True


def test_phase_9a_all_checks_pass():
    checks = verify_phase_9a_reviewer_package.run_checks()

    assert all(check.passed for check in checks)
