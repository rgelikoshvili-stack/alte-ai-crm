from pathlib import Path

from app.scripts import verify_cloud_run_deployment_docs


def test_cloud_run_deployment_verifier_importable():
    checks = verify_cloud_run_deployment_docs.run_checks()

    assert checks


def test_cloud_run_deployment_status_documented():
    assert verify_cloud_run_deployment_docs.cloud_run_deployment_documented().passed is True


def test_cloud_run_endpoint_results_documented():
    assert verify_cloud_run_deployment_docs.endpoint_results_documented().passed is True


def test_cloud_run_website_privacy_still_pending():
    assert verify_cloud_run_deployment_docs.website_privacy_pending().passed is True


def test_cloud_run_secret_pattern_detection(tmp_path: Path):
    sample = tmp_path / "bad.md"
    sample.write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    check = verify_cloud_run_deployment_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_cloud_run_database_url_detection(tmp_path: Path):
    sample = tmp_path / "bad-db.md"
    sample.write_text(
        "postgresql+asyncpg://alte_app:realpassword@db.example.com:5432/alte_ai_crm",
        encoding="utf-8",
    )

    check = verify_cloud_run_deployment_docs.no_secret_patterns([sample])

    assert check.passed is False


def test_cloud_run_all_repo_checks_pass():
    checks = verify_cloud_run_deployment_docs.run_checks()

    assert all(check.passed for check in checks)
