from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DOCS = PROJECT_ROOT / "docs" / "deployment"

TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
DIST_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"

RESULT = DOCS / "PHASE_9S_FRONTEND_EVENT_BINDING_FIX_RESULT.md"
HOSTED_SMOKE = DOCS / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
PUBLIC_LAUNCH = DOCS / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

STATUS = "PHASE_9S_FRONTEND_EVENT_BINDING_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST"
DECISION = "BACKEND_DEPLOYED_PRO_V2_EVENT_BINDING_FIXED_PENDING_NETLIFY_REDEPLOY"

FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant", re.IGNORECASE),
    re.compile("DATABASE" + r"_URL", re.IGNORECASE),
    re.compile(r"window\.claude\.complete", re.IGNORECASE),
    re.compile(r"['\"]\/api\/chat['\"]", re.IGNORECASE),
]

UNSAFE_BINDING_PATTERNS = [
    re.compile(r"document\.getElementById\([^;\n]+\)\.addEventListener", re.IGNORECASE),
    re.compile(r"document\.querySelector\([^;\n]+\)\.addEventListener", re.IGNORECASE),
    re.compile(r"querySelector\([^;\n]+\)\.addEventListener", re.IGNORECASE),
    re.compile(r"\bel\.[A-Za-z0-9_]+\.addEventListener", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files() -> list[Check]:
    files = [TEST_JS, TEST_HTML, DIST_JS, DIST_HTML, FINAL_WIDGET, RESULT]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def safe_binding_helper() -> Check:
    text = "\n".join(read(path) for path in [TEST_HTML, DIST_HTML, FINAL_WIDGET])
    required = [
        "function on(selectorOrElement, event, handler, options)",
        "missing event target",
        "target.addEventListener(event, handler, options)",
        'attach: document.getElementById("cw-attach")',
        'voice: document.getElementById("cw-voice")',
    ]
    missing = [item for item in required if item not in text]
    return Check("Safe event binding helper and optional controls are present", not missing, ", ".join(missing))


def unsafe_bindings_absent() -> Check:
    findings: list[str] = []
    for path in [TEST_HTML, DIST_HTML, FINAL_WIDGET]:
        text = read(path)
        for pattern in UNSAFE_BINDING_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{line}:{match.group(0)}")
    return Check("No unguarded element.addEventListener patterns remain", not findings, "; ".join(findings))


def markers_present() -> Check:
    text = "\n".join(read(path) for path in [TEST_JS, TEST_HTML, DIST_JS, DIST_HTML, FINAL_WIDGET])
    required = [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
        "cw-win",
        "cw-backdrop",
        "cw-side",
        "cw-comp",
    ]
    missing = [item for item in required if item not in text]
    return Check("Backend and Pro v2 markers are present", not missing, ", ".join(missing))


def no_forbidden() -> Check:
    findings: list[str] = []
    for path in [TEST_JS, TEST_HTML, DIST_JS, DIST_HTML, FINAL_WIDGET]:
        text = read(path)
        for pattern in FORBIDDEN:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    return Check("Frontend has no direct provider/API/secret patterns", not findings, ", ".join(findings))


def result_status() -> Check:
    return Check("Event binding fix status recorded", STATUS in read(RESULT))


def decision_state() -> Check:
    files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
        HOSTED_SMOKE,
        RESULT,
    ]
    text = "\n".join(read(path) for path in files)
    return Check("Decision state recorded", DECISION in text)


def docs_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [PROJECT_ROOT / "README.md", PROJECT_ROOT / "docs" / "NEXT_PHASES.md", HOSTED_SMOKE, PUBLIC_LAUNCH])
    bad = [
        phrase
        for phrase in [
            "hosted_browser_smoke_status=passed",
            "hosted browser smoke: passed",
            "public_launch_decision=go",
            "public launch complete",
            "actual site embed executed: yes",
        ]
        if phrase in text
    ]
    return Check("Browser smoke/public launch/site embed are not marked complete", not bad, ", ".join(bad))


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
        safe_binding_helper(),
        unsafe_bindings_absent(),
        markers_present(),
        no_forbidden(),
        result_status(),
        decision_state(),
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
