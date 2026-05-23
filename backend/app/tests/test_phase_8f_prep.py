from pathlib import Path

from app.scripts import verify_phase_8f_prep


def test_phase_8f_verifier_importable_and_required_docs_exist():
    checks = verify_phase_8f_prep.required_docs_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_phase_8f_requires_pending_approval():
    check = verify_phase_8f_prep.cloud_sql_pending_approval()

    assert check.passed is True


def test_phase_8f_secret_pattern_detection(tmp_path: Path):
    docs = tmp_path / "deployment"
    docs.mkdir()
    for name in verify_phase_8f_prep.REQUIRED_DOCS:
        content = "NO-GO_FOR_ACTUAL_DEPLOYMENT\nPENDING_APPROVAL\nproject-1e145fd0-c30e-4aac-a34\nhttps://alte.edu.ge\nhttps://join.alte.edu.ge\n"
        if name == "SECRET_PREPARATION_CHECKLIST.md":
            content += "ANTHROPIC_API_KEY=sk-ant-example\n"
        (docs / name).write_text(content, encoding="utf-8")

    check = verify_phase_8f_prep.no_secret_patterns(docs)

    assert check.passed is False


def test_phase_8f_all_repo_checks_pass():
    checks = verify_phase_8f_prep.run_checks()

    assert all(check.passed for check in checks)
