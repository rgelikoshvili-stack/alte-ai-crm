from pathlib import Path

from app.scripts import verify_release_checkpoint


def test_verify_release_checkpoint_checks_are_importable():
    checks = verify_release_checkpoint.run_checks()

    names = {check.name for check in checks}
    assert "README.md exists" in names
    assert "FastAPI app imports" in names
    assert "diagnostics route registered" in names


def test_verify_release_checkpoint_file_exists_helper(tmp_path):
    target = tmp_path / "README.md"
    missing = verify_release_checkpoint.file_exists(target, "tmp readme")
    target.write_text("ok", encoding="utf-8")
    present = verify_release_checkpoint.file_exists(target, "tmp readme")

    assert missing.passed is False
    assert present.passed is True


def test_verify_release_checkpoint_env_not_tracked():
    result = verify_release_checkpoint.env_not_tracked(Path(r"C:\tmp\alte-ai-crm"))

    assert result.passed is True
    assert ".env" not in result.detail
