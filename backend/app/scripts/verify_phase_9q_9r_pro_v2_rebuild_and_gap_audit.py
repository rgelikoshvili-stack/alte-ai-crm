from __future__ import annotations

import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

DOCS = PROJECT_ROOT / "docs" / "deployment"
EVIDENCE = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_pro_v2_widget" / "Alte_AI_Chat_Pro_v2_standalone.html"
FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"

REQUIRED_DOCS = [
    DOCS / "PRO_V2_EXTRACTION_RESULT.md",
    DOCS / "PRO_V2_UPLOADED_WIDGET_AUDIT.md",
    DOCS / "PRO_V2_FINAL_UI_TARGET.md",
    DOCS / "PRO_V2_FUNCTION_INVENTORY.md",
    DOCS / "PRO_V2_CURRENT_PROGRAM_GAP_MATRIX.md",
    DOCS / "PRO_V2_MISSING_FUNCTION_IMPLEMENTATION_PLAN.md",
    DOCS / "PRO_V2_BACKEND_GAPS_REQUIRING_APPROVAL.md",
    DOCS / "PHASE_9Q_9R_PRO_V2_REBUILD_AND_GAP_AUDIT_RESULT.md",
]

STATUS = "PHASE_9Q_9R_PRO_V2_REBUILD_AND_GAP_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST"
DECISION = "BACKEND_DEPLOYED_PRO_V2_REBUILT_AND_FUNCTION_GAPS_AUDITED_PENDING_NETLIFY_REDEPLOY"

FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant", re.IGNORECASE),
    re.compile("DATABASE" + r"_URL", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files() -> list[Check]:
    files = [EVIDENCE, FINAL_WIDGET, TEST_JS, TEST_HTML, DIST_JS, ZIP_PATH, *REQUIRED_DOCS]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_status() -> Check:
    result = read(DOCS / "PHASE_9Q_9R_PRO_V2_REBUILD_AND_GAP_AUDIT_RESULT.md")
    return Check("Combined result status recorded", STATUS in result)


def decision_state() -> Check:
    files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
        DOCS / "PRODUCTION_READINESS_DECISION.md",
        DOCS / "FINAL_PREFLIGHT_GATE.md",
        DOCS / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
        DOCS / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        DOCS / "PHASE_9Q_9R_PRO_V2_REBUILD_AND_GAP_AUDIT_RESULT.md",
    ]
    text = "\n".join(read(path) for path in files)
    return Check("Decision state recorded", DECISION in text)


def widget_markers() -> Check:
    text = "\n".join(read(path) for path in [FINAL_WIDGET, TEST_JS, TEST_HTML, DIST_JS])
    required = [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
        "source_domain",
        "widget_variant",
        "language",
        "reset",
        "fullscreen",
        "expand",
        "close",
        "operator",
        "handover",
        "source card renderer",
        "keydown",
        "Enter",
        "Alte AI Assistant",
        "KA",
        "EN",
    ]
    missing = [item for item in required if item not in text]
    return Check("Widget contains Pro v2 safe markers", not missing, ", ".join(missing))


def widget_no_forbidden() -> Check:
    findings: list[str] = []
    for path in [FINAL_WIDGET, TEST_JS, TEST_HTML, DIST_JS]:
        text = read(path)
        for pattern in FORBIDDEN:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    return Check("Widget assets contain no direct AI/secrets/DB patterns", not findings, ", ".join(findings))


def zip_root() -> Check:
    if not ZIP_PATH.exists():
        return Check("Netlify ZIP exists", False, str(ZIP_PATH))
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {info.filename.replace("\\", "/") for info in archive.infolist()}
        expected = {"index.html", "join.html", "alte-ai-chat-widget.js", "alte-ai-chat-widget.html", "_redirects", "README_GEO.md", "NETLIFY_DEPLOY_README_GEO.md"}
        missing = expected - names
        nested = [name for name in names if name.startswith("test_site/")]
    return Check("Netlify ZIP root contains updated assets", not missing and not nested, f"missing={sorted(missing)} nested={nested}")


def docs_not_complete() -> Check:
    files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
        DOCS / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
        DOCS / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        DOCS / "PHASE_9Q_9R_PRO_V2_REBUILD_AND_GAP_AUDIT_RESULT.md",
    ]
    text = "\n".join(read(path).lower() for path in files)
    bad = [
        phrase
        for phrase in [
            "hosted_browser_smoke_status=passed",
            "hosted browser smoke: passed",
            "public launch complete",
            "public_launch_decision=go",
            "actual site embed executed: yes",
            "actual alte embed complete",
        ]
        if phrase in text
    ]
    return Check("Docs do not mark smoke/embed/launch complete", not bad, ", ".join(bad))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets are not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files(),
        result_status(),
        decision_state(),
        widget_markers(),
        widget_no_forbidden(),
        zip_root(),
        docs_not_complete(),
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
