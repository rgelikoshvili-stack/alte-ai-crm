from pathlib import Path

from app.scripts import verify_local_secret_values_prep


def test_local_secret_values_prep_verifier_importable_and_required_files_exist():
    checks = verify_local_secret_values_prep.required_files_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_local_secret_values_prep_gitignore_includes_secret_patterns():
    assert verify_local_secret_values_prep.gitignore_includes_local_secret_patterns().passed is True


def test_local_secret_values_prep_decision_remains_no_go():
    assert verify_local_secret_values_prep.decision_remains_no_go().passed is True


def test_local_secret_values_prep_approval_gate_recorded():
    assert verify_local_secret_values_prep.approval_gate_recorded().passed is True


def test_local_secret_values_prep_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_local_secret_values_prep.no_secret_patterns([sample])

    assert check.passed is False


def test_local_secret_values_prep_all_repo_checks_pass():
    checks = verify_local_secret_values_prep.run_checks()

    assert all(check.passed for check in checks)
