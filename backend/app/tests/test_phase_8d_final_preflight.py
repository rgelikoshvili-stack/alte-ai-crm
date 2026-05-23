from pathlib import Path

from app.scripts import verify_final_preflight


def test_verify_final_preflight_importable_and_required_docs_exist():
    checks = verify_final_preflight.required_docs_exist()

    assert checks
    assert all(check.passed for check in checks)


def test_verify_final_preflight_detects_project_id_and_cors_values():
    checks = verify_final_preflight.content_checks()
    by_name = {check.name: check for check in checks}

    assert by_name["PROJECT_ID is filled"].passed is True
    assert by_name["GITHUB_REMOTE_URL exists"].passed is True
    assert by_name["CORS includes alte.edu.ge"].passed is True
    assert by_name["CORS includes join.alte.edu.ge"].passed is True
    assert by_name["Decision remains NO-GO"].passed is True


def test_verify_final_preflight_rejects_forbidden_secret_pattern(tmp_path: Path):
    docs = tmp_path / "deployment"
    docs.mkdir()
    for name in verify_final_preflight.REQUIRED_DOCS:
        content = "NO-GO_FOR_ACTUAL_DEPLOYMENT\nproject-1e145fd0-c30e-4aac-a34\nhttps://alte.edu.ge\nhttps://join.alte.edu.ge\nhttps://github.com/rgelikoshvili-stack/alte-ai-crm\n"
        if name == "SECRET_MANAGER.md":
            content += "ANTHROPIC_API_KEY=sk-ant-example\n"
        (docs / name).write_text(content, encoding="utf-8")

    checks = verify_final_preflight.content_checks(docs)

    assert any(check.name == "No forbidden secret patterns" and not check.passed for check in checks)


def test_verify_final_preflight_all_repo_checks_pass():
    checks = verify_final_preflight.run_checks()

    assert all(check.passed for check in checks)
