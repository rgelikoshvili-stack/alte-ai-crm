import csv

from app.scripts import prepare_conservative_content_decisions
from app.scripts import validate_phase_9f_content_decisions
from app.scripts import verify_phase_9f_content_approval


def test_phase_9f_scripts_importable():
    assert prepare_conservative_content_decisions.OUTPUT_PATH.name == "alte_kb_conservative_decisions_for_approval.csv"
    assert validate_phase_9f_content_decisions.ALLOWED_DECISIONS
    assert verify_phase_9f_content_approval.STATUS.startswith("PHASE_9F_CONTENT_APPROVAL_STATUS")


def test_conservative_decision_csv_exists():
    assert verify_phase_9f_content_approval.CONSERVATIVE_CSV.exists()


def test_conservative_decisions_are_allowed():
    with verify_phase_9f_content_approval.CONSERVATIVE_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        decisions = {(row.get("decision") or "").strip().upper() for row in reader}

    assert decisions <= validate_phase_9f_content_decisions.ALLOWED_DECISIONS


def test_high_sensitivity_not_auto_approved():
    assert verify_phase_9f_content_approval.high_sensitivity_not_public_approved_by_system().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9f_content_approval.public_launch_not_complete().passed is True


def test_official_approval_still_pending():
    assert verify_phase_9f_content_approval.official_human_approval_not_complete().passed is True


def test_phase_9f_decision_state_exists():
    assert verify_phase_9f_content_approval.decision_state_documented().passed is True


def test_phase_9f_no_forbidden_secret_patterns():
    assert verify_phase_9f_content_approval.no_forbidden_patterns().passed is True


def test_phase_9f_verifier_all_checks_pass():
    checks = verify_phase_9f_content_approval.run_checks()

    assert all(check.passed for check in checks)
