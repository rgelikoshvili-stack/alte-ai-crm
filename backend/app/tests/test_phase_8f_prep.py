from pathlib import Path

from app.scripts import verify_phase_8f_prep


def test_phase_8f_verifier_importable_and_required_docs_exist():
    checks = verify_phase_8f_prep.required_docs_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8f_records_pilot_approval():
    check = verify_phase_8f_prep.cloud_sql_pilot_approved()

    assert check.passed is True


def test_phase_8f_recommendation_exists_and_no_exact_price():
    assert verify_phase_8f_prep.cloud_sql_recommendation_exists().passed is True
    assert verify_phase_8f_prep.cloud_sql_has_no_exact_final_price().passed is True


def test_phase_8f_secret_pattern_detection(tmp_path: Path):
    docs = tmp_path / "deployment"
    docs.mkdir()
    for name in verify_phase_8f_prep.REQUIRED_DOCS:
        content = "NO-GO_FOR_ACTUAL_DEPLOYMENT\nAPPROVED_FOR_PILOT\nproject-1e145fd0-c30e-4aac-a34\nhttps://alte.edu.ge\nhttps://join.alte.edu.ge\n"
        if name == "SECRET_PREPARATION_CHECKLIST.md":
            content += "ANTHROPIC_API_KEY=sk-ant-example\n"
        (docs / name).write_text(content, encoding="utf-8")

    check = verify_phase_8f_prep.no_secret_patterns(docs)

    assert check.passed is False


def test_phase_8f_exact_price_detection(tmp_path: Path):
    docs = tmp_path / "deployment"
    docs.mkdir()
    form = docs / "CLOUD_SQL_COST_APPROVAL_FORM.md"
    form.write_text("Low-cost pilot production tier\nAPPROVED_FOR_PILOT\nEstimated monthly cost: $123", encoding="utf-8")

    check = verify_phase_8f_prep.cloud_sql_has_no_exact_final_price(docs)

    assert check.passed is False


def test_phase_8f_decision_remains_no_go():
    assert verify_phase_8f_prep.decision_remains_no_go().passed is True


def test_phase_8f_all_repo_checks_pass():
    checks = verify_phase_8f_prep.run_checks()

    assert all(check.passed for check in checks)
