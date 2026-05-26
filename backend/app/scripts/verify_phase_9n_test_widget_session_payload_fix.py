from __future__ import annotations

import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "test_site_session_payload_smoke.py"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEST_WIDGET_SESSION_PAYLOAD_FIX_RESULT.md"
HOSTED_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
TEST_WIDGET_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_WIDGET_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

STATUS = "PHASE_9N_TEST_WIDGET_SESSION_PAYLOAD_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY"
DECISION_STATE = "BACKEND_DEPLOYED_TEST_WIDGET_SESSION_PAYLOAD_FIX_READY_PENDING_NETLIFY_REDEPLOY"

FORBIDDEN_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL\s*=", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files_exist() -> list[Check]:
    files = [SMOKE_SCRIPT, RESULT_DOC, TEST_WIDGET_JS, TEST_WIDGET_HTML, ZIP_PATH]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_status_recorded() -> Check:
    return Check("Result records session payload fix status", STATUS in read(RESULT_DOC))


def widget_js_contains_markers() -> Check:
    text = read(TEST_WIDGET_JS)
    required = ["source_domain", "language", "channel", "widget_variant", "/chat/session/start", "/chat/message"]
    missing = [item for item in required if item not in text]
    return Check("Test-site JS contains backend-compatible session markers and endpoints", not missing, ", ".join(missing))


def widget_html_payload_is_compatible() -> Check:
    text = read(TEST_WIDGET_HTML)
    required = ['source_domain: cfg.sourceDomain', "language: lang", 'channel: "website_chat"']
    missing = [item for item in required if item not in text]
    forbidden = ['channel: "website",']
    found_forbidden = [item for item in forbidden if item in text]
    return Check(
        "Test-site widget HTML sends backend-compatible session payload",
        not missing and not found_forbidden,
        f"missing={missing}; forbidden={found_forbidden}",
    )


def zip_contains_updated_js_and_html() -> Check:
    if not ZIP_PATH.exists():
        return Check("Deploy ZIP exists and contains updated widget files", False, "missing zip")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = set(archive.namelist())
        required = {"alte-ai-chat-widget.js", "alte-ai-chat-widget.html"}
        missing = required - names
        js = archive.read("alte-ai-chat-widget.js").decode("utf-8", errors="ignore") if "alte-ai-chat-widget.js" in names else ""
        html = archive.read("alte-ai-chat-widget.html").decode("utf-8", errors="ignore") if "alte-ai-chat-widget.html" in names else ""
    passed = not missing and "sessionStartPayloadFields" in js and 'channel: "website_chat"' in html
    detail = f"missing={sorted(missing)}"
    return Check("Deploy ZIP contains updated widget JS and HTML", passed, detail)


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    scan_paths = [TEST_WIDGET_JS, TEST_WIDGET_HTML, RESULT_DOC, HOSTED_SMOKE, SMOKE_SCRIPT]
    for path in scan_paths:
        text = read(path)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    if ZIP_PATH.exists():
        with zipfile.ZipFile(ZIP_PATH) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                text = archive.read(info).decode("utf-8", errors="ignore")
                for pattern in FORBIDDEN_PATTERNS:
                    if pattern.search(text):
                        findings.append(f"zip:{info.filename}:{pattern.pattern}")
    return Check("No forbidden provider/key/secret patterns", not findings, ", ".join(findings))


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in [README, NEXT_PHASES, RESULT_DOC])
    return Check("Docs record session payload fix decision state", DECISION_STATE in text)


def browser_smoke_not_passed() -> Check:
    text = "\n".join(read(path).lower() for path in [HOSTED_SMOKE, RESULT_DOC, README, NEXT_PHASES])
    bad = [
        phrase
        for phrase in ["hosted_browser_smoke_status=passed", "browser smoke passed: yes", "hosted browser smoke: passed"]
        if phrase in text
    ]
    return Check("Browser smoke not marked passed", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [PUBLIC_LAUNCH, README, NEXT_PHASES, RESULT_DOC])
    bad = [
        phrase
        for phrase in ["public launch complete", "public_launch_decision=go", "public launch: complete"]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def actual_alte_embed_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [README, NEXT_PHASES, RESULT_DOC])
    bad = [
        phrase
        for phrase in ["actual alte embed complete", "actual site embed executed: yes", "actual site embed completed"]
        if phrase in text
    ]
    return Check("Actual Alte embed not marked complete", not bad, ", ".join(bad))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets are not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        result_status_recorded(),
        widget_js_contains_markers(),
        widget_html_payload_is_compatible(),
        zip_contains_updated_js_and_html(),
        no_forbidden_patterns(),
        docs_record_decision_state(),
        browser_smoke_not_passed(),
        public_launch_not_complete(),
        actual_alte_embed_not_complete(),
        env_not_tracked(),
        local_secrets_not_tracked(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
