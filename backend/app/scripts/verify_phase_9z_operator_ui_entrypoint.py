from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DIAGNOSIS_DOC = ROOT / "docs" / "deployment" / "PHASE_9Z_OPERATOR_UI_LOCAL_ENTRYPOINT_DIAGNOSIS.md"
RETEST_DOC = ROOT / "docs" / "deployment" / "PHASE_9Z_BROWSER_OPERATOR_LOGIN_RETEST_RESULT.md"
START_SCRIPT = ROOT / "scripts" / "start_operator_ui.ps1"
FRONTEND_INDEX = ROOT / "frontend" / "index.html"
PUBLIC_DECISION_DOC = ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

ALLOWED_STATUSES = {
    "READY_FOR_MANUAL_BROWSER_LOGIN",
    "PASSED",
    "BLOCKED_OPERATOR_UI_ENTRYPOINT_MISSING",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)\bpassword\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bpassword_hash\b"),
    re.compile(r"(?i)\bdatabase_url\b"),
    re.compile(r"(?i)\bpostgres(?:ql)?://"),
    re.compile(r"\bpbkdf2_sha256\$"),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]+"),
    re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git_ls_files(*paths: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--", *paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def assert_not_tracked(*paths: str) -> None:
    tracked = git_ls_files(*paths)
    if tracked:
        raise AssertionError(f"Forbidden tracked local secret files: {tracked}")


def assert_no_secret_like_content(path: Path) -> None:
    text = read(path)
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise AssertionError(f"Secret-like content found in {path.relative_to(ROOT)}")


def retest_status(text: str) -> str:
    match = re.search(r"PHASE_9Z_BROWSER_OPERATOR_LOGIN_RETEST_STATUS=([A-Z0-9_]+)", text)
    if not match:
        raise AssertionError("Retest status is missing")
    return match.group(1)


def main() -> None:
    for path in [DIAGNOSIS_DOC, RETEST_DOC]:
        if not path.exists():
            raise AssertionError(f"Missing required doc: {path.relative_to(ROOT)}")

    retest_text = read(RETEST_DOC)
    diagnosis_text = read(DIAGNOSIS_DOC)
    status = retest_status(retest_text)
    if status not in ALLOWED_STATUSES:
        raise AssertionError(f"Unexpected retest status: {status}")

    if status != "BLOCKED_OPERATOR_UI_ENTRYPOINT_MISSING":
        if not START_SCRIPT.exists():
            raise AssertionError("Operator UI start script is missing")
        if not FRONTEND_INDEX.exists():
            raise AssertionError("Operator UI frontend/index.html is missing")
        if "scripts\\start_operator_ui.ps1" not in diagnosis_text and "start_operator_ui.ps1" not in retest_text:
            raise AssertionError("Start script command is not documented")
    elif "files needed to restore" not in diagnosis_text.lower():
        raise AssertionError("Missing-state diagnosis must document restore requirements")

    assert_not_tracked(".local-secrets", ".env")
    assert_no_secret_like_content(DIAGNOSIS_DOC)
    assert_no_secret_like_content(RETEST_DOC)

    combined_status_text = retest_text + "\n" + diagnosis_text
    if PUBLIC_DECISION_DOC.exists():
        combined_status_text += "\n" + read(PUBLIC_DECISION_DOC)
    if "PUBLIC_LAUNCH_DECISION=GO" in combined_status_text or "PUBLIC_LAUNCH_STATUS=COMPLETE" in combined_status_text:
        raise AssertionError("Public launch must not be marked complete")
    if "NO-GO" not in combined_status_text:
        raise AssertionError("Public launch NO-GO state must remain documented")
    if "Real Alte site modified: YES" in combined_status_text:
        raise AssertionError("Real Alte site must not be marked modified")

    print("PHASE_9Z_OPERATOR_UI_ENTRYPOINT_VERIFIER=PASS")


if __name__ == "__main__":
    main()
