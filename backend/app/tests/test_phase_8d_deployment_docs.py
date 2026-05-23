from pathlib import Path

from app.scripts import verify_deployment_docs


def test_verify_deployment_docs_required_docs_detection():
    checks = verify_deployment_docs.required_docs_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_verify_deployment_docs_forbidden_sk_ant_detection(tmp_path: Path):
    docs = tmp_path / "deployment"
    docs.mkdir()
    (docs / "sample.md").write_text("ANTHROPIC_API_KEY=sk-ant-example", encoding="utf-8")

    checks = verify_deployment_docs.scan_for_forbidden_patterns(docs)

    assert len(checks) == 1
    assert checks[0].passed is False


def test_verify_deployment_docs_all_checks_pass_for_repo_docs():
    checks = verify_deployment_docs.run_checks()

    assert all(check.passed for check in checks)
