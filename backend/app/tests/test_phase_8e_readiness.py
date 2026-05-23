from pathlib import Path

from app.scripts import verify_phase_8e_readiness


def test_phase_8e_verifier_importable_and_required_docs_exist():
    checks = verify_phase_8e_readiness.required_docs_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8e_secret_pattern_detection(tmp_path: Path):
    docs = tmp_path / "deployment"
    docs.mkdir()
    for name in verify_phase_8e_readiness.REQUIRED_DOCS:
        content = "NO-GO_FOR_ACTUAL_DEPLOYMENT\nproject-1e145fd0-c30e-4aac-a34\n"
        if name == "SECRET_VALUES_RUNBOOK.md":
            content += "ANTHROPIC_API_KEY=sk-ant-example\n"
        (docs / name).write_text(content, encoding="utf-8")

    check = verify_phase_8e_readiness.scan_secret_patterns(docs)

    assert check.passed is False


def test_phase_8e_decision_remains_no_go_and_project_id_present():
    checks = {
        check.name: check
        for check in [
            verify_phase_8e_readiness.decision_remains_no_go(),
            verify_phase_8e_readiness.variables_include_project_id(),
        ]
    }

    assert checks["Decision remains NO-GO"].passed is True
    assert checks["Deployment variables include PROJECT_ID"].passed is True


def test_phase_8e_all_repo_checks_pass():
    checks = verify_phase_8e_readiness.run_checks()

    assert all(check.passed for check in checks)
