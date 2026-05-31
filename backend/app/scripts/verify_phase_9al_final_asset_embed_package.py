from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSET_MANIFEST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AL_FINAL_ASSET_MANIFEST.md"
EMBED_PACKAGE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AL_STAGED_EMBED_APPROVAL_PACKAGE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AL_FINAL_ASSET_AND_STAGED_EMBED_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
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
    manifest = read(ASSET_MANIFEST) if ASSET_MANIFEST.exists() else ""
    embed = read(EMBED_PACKAGE) if EMBED_PACKAGE.exists() else ""
    result = read(RESULT_DOC) if RESULT_DOC.exists() else ""
    public = read(PUBLIC_LAUNCH).lower() if PUBLIC_LAUNCH.exists() else ""
    all_docs = "\n".join([manifest, embed, result])
    tracked = tracked_files()
    return [
        check("asset manifest exists", ASSET_MANIFEST.exists(), str(ASSET_MANIFEST)),
        check("staged embed package exists", EMBED_PACKAGE.exists(), str(EMBED_PACKAGE)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public and "no-go" in public),
        check("real Alte site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in result and "JOIN_ALTE_SITE_MODIFIED=NO" in result),
        check("asset upload not executed", "ASSET_UPLOAD_EXECUTED=NO" in result and "ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in result),
        check("embed not executed", "STAGED_EMBED_EXECUTED=NO" in result and "STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in result),
        check("privacy URL pending unless provided", "PRIVACY_URL_STATUS=PENDING" in result or "PRIVACY_URL_STATUS=PROVIDED_PENDING_APPROVAL" in result),
        check("contact-flow not approved", "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in result),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("no secrets in 9AL docs", all(pattern not in all_docs for pattern in SECRET_PATTERNS)),
        check("proposed final asset URL documented", "https://alte.edu.ge/assets/alte-ai-chat-widget.js" in all_docs),
        check("full upload package documented", all(value in manifest for value in ["alte-ai-chat-widget.js", "alte-ai-chat-widget.html", "variants/pro-v2-chat.jsx"])),
        check("staged pages documented", "join.alte.edu.ge" in embed and "admissions/program-related page" in embed),
        check("real-domain smoke pending", "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_PENDING_APPROVED_EMBED" in result),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
