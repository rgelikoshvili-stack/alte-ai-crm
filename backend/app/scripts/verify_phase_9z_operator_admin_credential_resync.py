from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = ROOT / "docs" / "deployment" / "PHASE_9Z_OPERATOR_ADMIN_CREDENTIAL_RESYNC_RESULT.md"
LOGIN_SMOKE = ROOT / "backend" / "app" / "scripts" / "production_operator_login_smoke.py"
PUBLIC_DECISION_DOC = ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

SECRET_PATTERNS = [
    re.compile(r"(?i)\bpassword\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bpassword_hash\b"),
    re.compile(r"(?i)\bdatabase_url\s*[:=]\s*\S+"),
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


def main() -> None:
    if not RESULT_DOC.exists():
        raise AssertionError("Phase 9Z result doc is missing")
    if not LOGIN_SMOKE.exists():
        raise AssertionError("Production operator login smoke script is missing")

    assert_not_tracked(".local-secrets", ".env")
    assert_no_secret_like_content(RESULT_DOC)

    result_text = read(RESULT_DOC)
    public_text = read(PUBLIC_DECISION_DOC) if PUBLIC_DECISION_DOC.exists() else ""
    combined_status_text = f"{result_text}\n{public_text}"
    if "PUBLIC_LAUNCH_DECISION=GO" in combined_status_text or "PUBLIC_LAUNCH_STATUS=COMPLETE" in combined_status_text:
        raise AssertionError("Public launch must not be marked complete")
    if "NO-GO" not in combined_status_text:
        raise AssertionError("Public launch NO-GO state must remain documented")
    if "Real Alte site modified: NO" not in result_text:
        raise AssertionError("Real Alte site safety line is missing")
    if "Migration run: NO" not in result_text:
        raise AssertionError("Migration safety line is missing")
    if "Seed run: NO" not in result_text:
        raise AssertionError("Seed safety line is missing")
    if "Migration run: YES" in result_text or "Seed run: YES" in result_text:
        raise AssertionError("Result doc must not say migration or seed was executed")

    print("PHASE_9Z_OPERATOR_ADMIN_CREDENTIAL_RESYNC_VERIFIER=PASS")


if __name__ == "__main__":
    main()
