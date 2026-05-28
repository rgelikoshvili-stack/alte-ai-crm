from __future__ import annotations

import json
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
DIST_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
SAFE_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
SMOKE_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_netlify_pro_v2_cors_smoke.py"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9S_PRO_V2_MESSAGE_ENDPOINT_CORS_FIX_RESULT.md"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def is_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def run_checks() -> list[Check]:
    checks: list[Check] = []
    paths = [TEST_JS, DIST_JS, TEST_HTML, DIST_HTML, SAFE_WIDGET, SMOKE_SCRIPT, RESULT_DOC, ZIP_PATH]
    for path in paths:
        checks.append(Check(f"{path.name}_exists", path.exists(), str(path)))

    frontend_text = "\n".join(read(path) for path in [TEST_JS, DIST_JS, TEST_HTML, DIST_HTML, SAFE_WIDGET] if path.exists())
    for required in [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
    ]:
        checks.append(Check(f"frontend_contains_{required}", required in frontend_text))
    for forbidden in [
        "/chat/messages",
        "/api/chat",
        "api.anthropic.com",
        "ANTHROPIC_API_KEY",
        "sk-ant-",
    ]:
        checks.append(Check(f"frontend_absent_{forbidden}", forbidden not in frontend_text))

    smoke_text = read(SMOKE_SCRIPT) if SMOKE_SCRIPT.exists() else ""
    checks.append(Check("cors_smoke_checks_netlify_origin", "https://nimble-croissant-2f66e8.netlify.app" in smoke_text))
    checks.append(Check("cors_smoke_checks_session_endpoint", "/chat/session/start" in smoke_text))
    checks.append(Check("cors_smoke_checks_message_endpoint", "/chat/message" in smoke_text))

    result_text = read(RESULT_DOC) if RESULT_DOC.exists() else ""
    checks.append(
        Check(
            "result_status_recorded",
            "PHASE_9S_PRO_V2_MESSAGE_ENDPOINT_CORS_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST" in result_text,
        )
    )
    checks.append(Check("browser_smoke_not_passed", "HOSTED_BROWSER_SMOKE_STATUS=PASSED" not in result_text))
    checks.append(Check("public_launch_no_go", "public launch: NO" in result_text or "Public launch: NO" in result_text))

    if ZIP_PATH.exists():
        with zipfile.ZipFile(ZIP_PATH) as archive:
            names = set(archive.namelist())
        for expected in {
            "index.html",
            "join.html",
            "alte-ai-chat-widget.js",
            "alte-ai-chat-widget.html",
            "_redirects",
            "README_GEO.md",
            "NETLIFY_DEPLOY_README_GEO.md",
        }:
            checks.append(Check(f"zip_contains_{expected}", expected in names, ",".join(sorted(names))))
        checks.append(Check("zip_not_nested_under_test_site", not any(name.startswith("test_site/") for name in names)))

    checks.append(Check("env_not_tracked", not is_tracked(".env")))
    checks.append(Check("local_secrets_not_tracked", not is_tracked(".local-secrets")))
    return checks


def main() -> None:
    checks = run_checks()
    failures = [check for check in checks if not check.passed]
    print(
        json.dumps(
            {
                "status": "PASS" if not failures else "FAIL",
                "total": len(checks),
                "passed": len(checks) - len(failures),
                "failed": len(failures),
                "failures": [failure.__dict__ for failure in failures],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
