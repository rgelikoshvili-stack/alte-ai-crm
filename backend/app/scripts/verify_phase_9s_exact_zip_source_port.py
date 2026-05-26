from __future__ import annotations

import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DOCS = PROJECT_ROOT / "docs" / "deployment"
ZIP_EVIDENCE = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_pro_v2_zip_source"

FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
DIST_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"

RESULT_STATUS = "PHASE_9S_EXACT_ZIP_SOURCE_PORT_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST"
DECISION = "BACKEND_DEPLOYED_EXACT_ZIP_SOURCE_PRO_V2_WIDGET_READY_PENDING_NETLIFY_REDEPLOY"

FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant", re.IGNORECASE),
    re.compile("DATABASE" + r"_URL", re.IGNORECASE),
    re.compile(r"window\.claude\.complete", re.IGNORECASE),
    re.compile(r"['\"]\/api\/chat['\"]", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files() -> list[Check]:
    files = [
        ZIP_EVIDENCE,
        ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-chat.jsx",
        ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-strings.jsx",
        ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-icons.jsx",
        ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-modals.jsx",
        DOCS / "PRO_V2_ZIP_SOURCE_AUDIT.md",
        DOCS / "PRO_V2_ZIP_EXACT_PORT_PLAN.md",
        DOCS / "PHASE_9S_EXACT_ZIP_SOURCE_PORT_RESULT.md",
        FINAL_WIDGET,
        TEST_JS,
        TEST_HTML,
        DIST_JS,
        DIST_HTML,
        ZIP_PATH,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_status() -> Check:
    return Check("Phase 9S result status recorded", RESULT_STATUS in read(DOCS / "PHASE_9S_EXACT_ZIP_SOURCE_PORT_RESULT.md"))


def decision_state() -> Check:
    files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
        DOCS / "PRODUCTION_READINESS_DECISION.md",
        DOCS / "FINAL_PREFLIGHT_GATE.md",
        DOCS / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
        DOCS / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        DOCS / "FINAL_WIDGET_ASSET_URL_DECISION.md",
        PROJECT_ROOT / "docs" / "final_handoff" / "FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md",
        PROJECT_ROOT / "docs" / "embed_package" / "WEBSITE_DEVELOPER_HANDOFF_GEO.md",
        DOCS / "PHASE_9S_EXACT_ZIP_SOURCE_PORT_RESULT.md",
    ]
    text = "\n".join(read(path) for path in files)
    return Check("Phase 9S decision state recorded", DECISION in text)


def markers_present() -> Check:
    text = "\n".join(read(path) for path in [FINAL_WIDGET, TEST_JS, TEST_HTML, DIST_JS, DIST_HTML])
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
        "expand",
        "close",
        "settings",
        "cw-win",
        "cw-win expanded",
        "cw-backdrop",
        "cw-side",
        "cw-side collapsed",
        "quick",
        "cw-comp",
        "operator",
        "handover",
    ]
    missing = [item for item in required if item not in text]
    return Check("Safe widget contains exact ZIP visual/backend markers", not missing, ", ".join(missing))


def no_forbidden() -> Check:
    findings: list[str] = []
    for path in [FINAL_WIDGET, TEST_JS, TEST_HTML, DIST_JS, DIST_HTML]:
        text = read(path)
        for pattern in FORBIDDEN:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    return Check("Safe widget contains no unsafe provider/API/secret patterns", not findings, ", ".join(findings))


def zip_root() -> Check:
    if not ZIP_PATH.exists():
        return Check("Netlify ZIP exists", False, str(ZIP_PATH))
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {info.filename.replace("\\", "/") for info in archive.infolist()}
        expected = {
            "index.html",
            "join.html",
            "alte-ai-chat-widget.js",
            "alte-ai-chat-widget.html",
            "_redirects",
            "README_GEO.md",
            "NETLIFY_DEPLOY_README_GEO.md",
        }
        missing = expected - names
        nested = [name for name in names if name.startswith("test_site/")]
        html = archive.read("alte-ai-chat-widget.html").decode("utf-8") if "alte-ai-chat-widget.html" in names else ""
    marker_ok = "cw-win" in html and "cw-backdrop" in html and "pro_v2_safe" in html
    return Check("Netlify ZIP root contains updated exact widget", not missing and not nested and marker_ok, f"missing={sorted(missing)} nested={nested} marker_ok={marker_ok}")


def docs_not_complete() -> Check:
    files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
        DOCS / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
        DOCS / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        DOCS / "PHASE_9S_EXACT_ZIP_SOURCE_PORT_RESULT.md",
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
    return Check("Docs do not mark browser smoke/embed/public launch complete", not bad, ", ".join(bad))


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
        markers_present(),
        no_forbidden(),
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
