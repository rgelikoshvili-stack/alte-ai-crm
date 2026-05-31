from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
HANDOFF_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AN_OWNER_APPROVAL_HANDOFF.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AN_OWNER_APPROVAL_HANDOFF_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
ZIP_PATH = "dist/final_alte_widget_upload.zip"
ZIP_SHA256 = "EEE750AA2E960BECC71E840C75C57D58C4E02CECAE63AAD8C72769A87F32FE2A"
EMBED_SNIPPET = '<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>'
REQUIRED_ASSET_PATHS = [
    "/assets/alte-ai-chat-widget.js",
    "/assets/alte-ai-chat-widget.html",
    "/assets/variants/pro-v2-chat.jsx",
    "/assets/variants/pro-v2-icons.jsx",
    "/assets/variants/pro-v2-modals.jsx",
    "/assets/variants/pro-v2-page.jsx",
    "/assets/variants/pro-v2-strings.jsx",
    "/assets/variants/tweaks-panel.jsx",
]
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    handoff = read(HANDOFF_DOC) if HANDOFF_DOC.exists() else ""
    result = read(RESULT_DOC) if RESULT_DOC.exists() else ""
    public = read(PUBLIC_LAUNCH).lower() if PUBLIC_LAUNCH.exists() else ""
    combined = "\n".join([handoff, result])
    tracked = tracked_files()
    return [
        check("handoff doc exists", HANDOFF_DOC.exists(), str(HANDOFF_DOC)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("upload ZIP path mentioned", ZIP_PATH in combined, ZIP_PATH),
        check("ZIP hash mentioned", ZIP_SHA256 in combined),
        check("required asset paths mentioned", all(path in combined for path in REQUIRED_ASSET_PATHS)),
        check("embed snippet mentioned", EMBED_SNIPPET in combined),
        check("staged pages mentioned", "join.alte.edu.ge" in combined and "admissions/program-related page" in combined),
        check("privacy URL remains pending", "PRIVACY_URL_STATUS=PENDING" in combined),
        check("contact-flow remains not approved", "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in combined),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public and "no-go" in public and "PUBLIC_LAUNCH_STATUS=NO_GO" in combined),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in combined and "JOIN_ALTE_SITE_MODIFIED=NO" in combined),
        check("asset upload not marked executed", "ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in combined and "ASSET_UPLOAD_EXECUTED=YES" not in combined),
        check("embed not marked executed", "STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in combined and "STAGED_EMBED_EXECUTED=YES" not in combined),
        check("no secrets in docs", all(pattern not in combined for pattern in SECRET_PATTERNS)),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())

