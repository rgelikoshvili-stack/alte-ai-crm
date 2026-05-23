from pathlib import Path

from app.scripts import verify_cloud_sql_execution_docs


def test_cloud_sql_execution_verifier_importable():
    checks = verify_cloud_sql_execution_docs.run_checks()

    assert checks


def test_cloud_sql_execution_status_documented():
    assert verify_cloud_sql_execution_docs.cloud_sql_status_documented().passed is True


def test_cloud_sql_execution_no_go_remains():
    assert verify_cloud_sql_execution_docs.decision_remains_no_go().passed is True


def test_cloud_sql_execution_no_enterprise_plus_selected():
    assert verify_cloud_sql_execution_docs.no_enterprise_plus_selected().passed is True


def test_cloud_sql_execution_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_cloud_sql_execution_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_cloud_sql_execution_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text(
        "DATABASE_URL=postgresql+asyncpg://alte_app:realpassword@db.example.com:5432/alte_ai_crm",
        encoding="utf-8",
    )

    check = verify_cloud_sql_execution_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_cloud_sql_execution_all_repo_checks_pass():
    checks = verify_cloud_sql_execution_docs.run_checks()

    assert all(check.passed for check in checks)
