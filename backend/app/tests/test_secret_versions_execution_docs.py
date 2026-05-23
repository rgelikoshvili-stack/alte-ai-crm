from pathlib import Path

from app.scripts import verify_secret_versions_execution_docs


def test_secret_versions_execution_verifier_importable():
    checks = verify_secret_versions_execution_docs.run_checks()

    assert checks


def test_secret_versions_execution_statuses_documented():
    assert verify_secret_versions_execution_docs.secret_version_statuses_documented().passed is True


def test_secret_versions_execution_database_url_pending():
    assert verify_secret_versions_execution_docs.database_url_pending_until_cloud_sql().passed is True


def test_secret_versions_execution_decision_remains_no_go():
    assert verify_secret_versions_execution_docs.decision_remains_no_go().passed is True


def test_secret_versions_execution_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_secret_versions_execution_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_secret_versions_execution_local_secrets_not_tracked():
    assert verify_secret_versions_execution_docs.local_secrets_not_tracked().passed is True


def test_secret_versions_execution_all_repo_checks_pass():
    checks = verify_secret_versions_execution_docs.run_checks()

    assert all(check.passed for check in checks)
