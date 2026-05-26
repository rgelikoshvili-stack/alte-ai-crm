from __future__ import annotations

import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

EVIDENCE = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_pro_v2_widget" / "Alte_AI_Chat_Pro_v2_standalone.html"
AUDIT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PRO_V2_STANDALONE_UI_AUDIT.md"
PLAN_DOC = PROJECT_ROOT / "docs" / "deployment" / "PRO_V2_SAFE_BACKEND_ADAPTATION_PLAN.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9Q_PRO_V2_SAFE_WIDGET_ADAPTATION_RESULT.md"

FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
DIST_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
HOSTED_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"

STATUS = "PHASE_9Q_PRO_V2_ADAPTATION_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST"
DECISION = "BACKEND_DEPLOYED_PRO_V2_SAFE_WIDGET_READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST"

FORBIDDEN_ASSET_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile("DATABASE" + r"_URL", re.IGNORECASE),
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
    files = [EVIDENCE, AUDIT_DOC, PLAN_DOC, RESULT_DOC, FINAL_WIDGET, DIST_JS, DIST_HTML, TEST_JS, TEST_HTML, ZIP_PATH]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def js_backend_contract_present() -> Check:
    text = "\n".join(read(path) for path in [FINAL_WIDGET, DIST_JS, DIST_HTML, TEST_JS, TEST_HTML])
    required = [
        "/chat/session/start",
        "/chat/message",
        "source_domain",
        "language",
        "widget_variant",
        "selected_department",
        "selected_topic",
        "pro_v2_safe",
        "website_chat",
    ]
    missing = [item for item in required if item not in text]
    return Check("Safe widget contains backend contract markers", not missing, ", ".join(missing))


def widget_assets_are_safe() -> Check:
    findings: list[str] = []
    for path in [FINAL_WIDGET, DIST_JS, DIST_HTML, TEST_JS, TEST_HTML]:
        text = read(path)
        for pattern in FORBIDDEN_ASSET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    return Check("Widget assets contain no provider/key/DB patterns", not findings, ", ".join(findings))


def zip_rebuilt_and_contains_assets() -> Check:
    if not ZIP_PATH.exists():
        return Check("Netlify deploy ZIP exists", False, str(ZIP_PATH))
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {info.filename.replace("\\", "/") for info in archive.infolist()}
        missing = {
            "index.html",
            "join.html",
            "alte-ai-chat-widget.js",
            "alte-ai-chat-widget.html",
            "_redirects",
            "README_GEO.md",
            "NETLIFY_DEPLOY_README_GEO.md",
        } - names
        nested = [name for name in names if name.startswith("test_site/")]
    if missing or nested:
        return Check("Netlify deploy ZIP root is correct", False, f"missing={sorted(missing)} nested={nested}")
    return Check("Netlify deploy ZIP root is correct", True, str(ZIP_PATH))


def status_recorded() -> Check:
    return Check("Phase 9Q result status recorded", STATUS in read(RESULT_DOC))


def decision_recorded() -> Check:
    text = "\n".join(read(path) for path in [README, NEXT_PHASES, PUBLIC_LAUNCH, HOSTED_SMOKE, READINESS, FINAL_PREFLIGHT])
    return Check("Phase 9Q decision state recorded", DECISION in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [README, NEXT_PHASES, PUBLIC_LAUNCH, RESULT_DOC])
    bad = [
        phrase
        for phrase in [
            "public launch complete",
            "full production launch complete",
            "public launch: complete",
            "public_launch_decision=go",
        ]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def browser_smoke_not_passed() -> Check:
    text = "\n".join(read(path).lower() for path in [HOSTED_SMOKE, RESULT_DOC, README, NEXT_PHASES])
    bad = [
        phrase
        for phrase in [
            "hosted_browser_smoke_status=passed",
            "hosted browser smoke: passed",
            "browser smoke passed: yes",
        ]
        if phrase in text
    ]
    return Check("Hosted browser smoke not falsely marked passed", not bad, ", ".join(bad))


def actual_embed_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [README, NEXT_PHASES, PUBLIC_LAUNCH, RESULT_DOC])
    bad = [
        phrase
        for phrase in [
            "actual alte embed complete",
            "actual site embed completed",
            "actual site embed executed: yes",
        ]
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
        js_backend_contract_present(),
        widget_assets_are_safe(),
        zip_rebuilt_and_contains_assets(),
        status_recorded(),
        decision_recorded(),
        public_launch_not_complete(),
        browser_smoke_not_passed(),
        actual_embed_not_complete(),
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
