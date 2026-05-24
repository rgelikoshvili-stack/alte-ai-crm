from pathlib import Path

from app.scripts import production_knowledge_smoke_after_study_docs
from app.scripts import verify_phase_8w_production_knowledge_smoke


def test_phase_8w_scripts_importable():
    assert production_knowledge_smoke_after_study_docs.PRODUCTION_BACKEND_URL.startswith("https://")
    assert verify_phase_8w_production_knowledge_smoke.RESULT_DOC.name.endswith("_RESULT.md")


def test_phase_8w_required_files_exist():
    checks = verify_phase_8w_production_knowledge_smoke.required_files_exist()

    assert all(check.passed for check in checks)


def test_phase_8w_result_records_import_summary_and_status():
    assert verify_phase_8w_production_knowledge_smoke.import_summary_recorded().passed is True
    assert verify_phase_8w_production_knowledge_smoke.smoke_status_recorded().passed is True


def test_phase_8w_result_records_no_contact_flow_or_intentional_leads():
    assert verify_phase_8w_production_knowledge_smoke.safety_flags_recorded().passed is True


def test_phase_8w_decision_state_exists_and_public_launch_not_complete():
    assert verify_phase_8w_production_knowledge_smoke.decision_state_documented().passed is True
    assert verify_phase_8w_production_knowledge_smoke.public_launch_not_complete().passed is True


def test_phase_8w_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8w_production_knowledge_smoke.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8w_no_forbidden_secret_patterns():
    assert verify_phase_8w_production_knowledge_smoke.no_forbidden_patterns().passed is True
