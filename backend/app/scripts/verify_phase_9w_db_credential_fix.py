from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"


REAL_DB_URL = re.compile(r"postgres(?:ql)?(?:\+asyncpg)?://[^<\s]+:[^<\s]+@", re.IGNORECASE)
PASSWORD_ASSIGNMENT = re.compile(r"password\s*[:=]\s*['\"]?[^<\s]{8,}", re.IGNORECASE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def check(condition: bool, message: str, failures: list[str]) -> None:
    print(("PASS " if condition else "FAIL ") + message)
    if not condition:
        failures.append(message)


def tracked(path: str) -> bool:
    return subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def main() -> int:
    failures: list[str] = []
    root_doc = ROOT / "docs" / "deployment" / "PHASE_9W_DB_CREDENTIAL_FIX_ROOT_CAUSE.md"
    result_doc = ROOT / "docs" / "deployment" / "PHASE_9W_DB_CREDENTIAL_FIX_RESULT.md"
    smoke = BACKEND / "app" / "scripts" / "production_db_credential_smoke.py"
    test_js = read(ROOT / "test_site" / "alte-ai-chat-widget.js")
    dist_js = read(ROOT / "dist" / "widget" / "alte-ai-chat-widget.js")
    docs = "\n".join(read(path) for path in [root_doc, result_doc, ROOT / "README.md", ROOT / "docs" / "NEXT_PHASES.md"] if path.exists())

    check(root_doc.exists(), "root cause doc exists", failures)
    check(result_doc.exists(), "result doc exists", failures)
    check(smoke.exists(), "production DB credential smoke exists", failures)
    check("PHASE_9W_DB_CREDENTIAL_FIX_STATUS=FIXED_PENDING_BROWSER_RETEST" in docs, "result records fixed status", failures)
    check("BACKEND_DEPLOYED_DB_CREDENTIAL_FIXED_CHAT_READY_PENDING_BROWSER_RETEST" in docs, "docs contain fixed decision state", failures)
    for text, name in [(docs, "docs"), (read(smoke), "smoke script") if smoke.exists() else ("", "smoke script")]:
        check(not REAL_DB_URL.search(text), f"{name} contain no raw DATABASE_URL value", failures)
        check(not PASSWORD_ASSIGNMENT.search(text), f"{name} contain no obvious password value", failures)
    for forbidden in ["ANTHROPIC_API_KEY", "api.anthropic.com", "sk-ant-", "/api/chat"]:
        check(forbidden not in test_js and forbidden not in dist_js, f"frontend excludes {forbidden}", failures)
    for marker in ["/chat/session/start", "/chat/message"]:
        check(marker in test_js and marker in dist_js, f"frontend uses {marker}", failures)
    lowered = docs.lower()
    check("public launch: no" in lowered or "public launch remains no-go" in lowered, "public launch remains NO-GO", failures)
    check("actual alte embed complete" not in lowered, "real Alte embed not marked complete", failures)
    check(not tracked(".env"), ".env not tracked", failures)
    check(not tracked(".local-secrets"), ".local-secrets not tracked", failures)

    if failures:
        print("verify_phase_9w_db_credential_fix=FAIL")
        return 1
    print("verify_phase_9w_db_credential_fix=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
