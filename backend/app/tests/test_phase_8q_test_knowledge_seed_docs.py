from pathlib import Path

from app.scripts import verify_phase_8q_test_knowledge_seed_docs
from app.scripts import verify_required_test_knowledge_seed


def test_phase_8q_verifier_importable_and_files_exist():
    checks = verify_phase_8q_test_knowledge_seed_docs.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8q_approval_gate_executed():
    assert verify_phase_8q_test_knowledge_seed_docs.approval_gate_executed().passed is True


def test_phase_8q_result_records_idempotency_and_safe_smoke():
    assert verify_phase_8q_test_knowledge_seed_docs.result_records_seed_and_smoke().passed is True


def test_phase_8q_decision_state_documented():
    assert verify_phase_8q_test_knowledge_seed_docs.decision_state_documented().passed is True


def test_phase_8q_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("sk-ant-example", encoding="utf-8")

    check = verify_phase_8q_test_knowledge_seed_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_phase_8q_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text("DATABASE_URL=postgresql+asyncpg://user:pass@example/db", encoding="utf-8")

    check = verify_phase_8q_test_knowledge_seed_docs.no_forbidden_patterns([sample])

    assert check.passed is False


def test_required_test_knowledge_seed_verifier_importable():
    assert verify_required_test_knowledge_seed.REQUIRED_SOURCE_GROUPS["finance"] == ["alte_test_finance_v1"]


def test_phase_8q_all_repo_checks_pass():
    checks = verify_phase_8q_test_knowledge_seed_docs.run_checks()

    assert all(check.passed for check in checks)
