from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BUNDLE_DIR = PROJECT_ROOT / "dist" / "final_alte_widget_upload"
ZIP_PATH = PROJECT_ROOT / "dist" / "final_alte_widget_upload.zip"
MANIFEST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_FINAL_UPLOAD_BUNDLE_MANIFEST.md"
SMOKE_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_REAL_DOMAIN_SMOKE_CHECKLIST.md"
ROLLBACK_PLAN = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_REAL_SITE_ROLLBACK_PLAN.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_FINAL_UPLOAD_BUNDLE_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
REQUIRED_ZIP_FILES = {
    "alte-ai-chat-widget.js",
    "alte-ai-chat-widget.html",
    "variants/pro-v2-chat.jsx",
    "variants/pro-v2-icons.jsx",
    "variants/pro-v2-modals.jsx",
    "variants/pro-v2-page.jsx",
    "variants/pro-v2-strings.jsx",
    "variants/tweaks-panel.jsx",
}
FORBIDDEN_FRONTEND = [
    "api.anthropic.com",
    "ANTHROPIC_API_KEY",
    "sk-ant",
    "/api/chat",
    "127.0.0.1",
    "localhost",
    "nimble-croissant",
    "netlify",
]
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]
MOJIBAKE_MARKER = "\u00e1\u0192"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def zip_entries() -> set[str]:
    with zipfile.ZipFile(ZIP_PATH) as archive:
        return {info.filename.replace("\\", "/").rstrip("/") for info in archive.infolist() if not info.is_dir()}


def bundle_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in BUNDLE_DIR.rglob("*") if path.is_file())


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    manifest = read(MANIFEST) if MANIFEST.exists() else ""
    smoke = read(SMOKE_CHECKLIST) if SMOKE_CHECKLIST.exists() else ""
    rollback = read(ROLLBACK_PLAN) if ROLLBACK_PLAN.exists() else ""
    result = read(RESULT_DOC) if RESULT_DOC.exists() else ""
    public = read(PUBLIC_LAUNCH).lower() if PUBLIC_LAUNCH.exists() else ""
    docs_text = "\n".join([manifest, smoke, rollback, result])
    frontend = bundle_text() if BUNDLE_DIR.exists() else ""
    entries = zip_entries() if ZIP_PATH.exists() else set()
    tracked = tracked_files()
    return [
        check("upload bundle directory exists", BUNDLE_DIR.exists(), str(BUNDLE_DIR)),
        check("ZIP exists", ZIP_PATH.exists(), str(ZIP_PATH)),
        check("ZIP root contains required files exactly", entries == REQUIRED_ZIP_FILES, ", ".join(sorted(entries))),
        check("manifest exists", MANIFEST.exists(), str(MANIFEST)),
        check("smoke checklist exists", SMOKE_CHECKLIST.exists(), str(SMOKE_CHECKLIST)),
        check("rollback plan exists", ROLLBACK_PLAN.exists(), str(ROLLBACK_PLAN)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public and "no-go" in public),
        check("upload not marked executed", "ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in result),
        check("embed not marked executed", "STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in result),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in result and "JOIN_ALTE_SITE_MODIFIED=NO" in result),
        check("privacy URL pending unless provided", "PRIVACY_URL_STATUS=PENDING" in result or "PRIVACY_URL_STATUS=PROVIDED_PENDING_APPROVAL" in result),
        check("contact-flow not approved", "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in result),
        check("frontend files do not expose API keys or forbidden calls", all(value not in frontend for value in FORBIDDEN_FRONTEND)),
        check("Cloud Run backend remains configured", "https://alte-ai-crm-backend-226875230147.europe-west1.run.app" in frontend),
        check("Georgian mojibake absent", MOJIBAKE_MARKER not in frontend + docs_text),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("no secrets in docs", all(pattern not in docs_text for pattern in SECRET_PATTERNS)),
        check("real-domain smoke not executed", "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED" in result),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
