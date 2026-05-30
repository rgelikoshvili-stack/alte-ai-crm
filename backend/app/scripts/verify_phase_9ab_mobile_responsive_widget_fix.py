from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AB_MOBILE_RESPONSIVE_WIDGET_FIX_RESULT.md"
VISUAL_QA_DIR = PROJECT_ROOT / "docs" / "deployment" / "visual_qa"
TEST_SITE_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
]
WIDGET_FILES = [
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
]
DOC_FILES = [
    RESULT_DOC,
    PROJECT_ROOT / "docs" / "deployment" / "FINAL_LAUNCH_READINESS_AND_SITE_EMBED_APPROVAL_PACKAGE.md",
    PROJECT_ROOT / "docs" / "deployment" / "FULL_PROJECT_AUDIT_2026_05_30.md",
    PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AD_INTEGRATED_ROUTING_FIX_RESULT.md",
]

VALID_STATUSES = {
    "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=FIXED_PENDING_NETLIFY_REDEPLOY_AND_VISUAL_QA",
    "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL",
    "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=FAILED_PENDING_LAYOUT_FIX",
    "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=BLOCKED_NETLIFY_REDEPLOY_REQUIRED",
}

FORBIDDEN_FRONTEND_PATTERNS = [
    re.compile(r"/api/chat", re.IGNORECASE),
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def result_doc_exists() -> Check:
    return Check("Phase 9AB result doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def result_doc_status_valid() -> Check:
    text = read(RESULT_DOC)
    matches = [status for status in VALID_STATUSES if status in text]
    return Check("Phase 9AB result status is valid", len(matches) == 1, ", ".join(matches))


def visual_evidence_present_or_marked_pending() -> Check:
    text = read(RESULT_DOC)
    screenshots = [
        VISUAL_QA_DIR / "local_widget_desktop_1440x900_phase_9ab.png",
        VISUAL_QA_DIR / "local_widget_mobile_430x932_phase_9ab.png",
        VISUAL_QA_DIR / "netlify_widget_desktop_1440x900_phase_9ab.png",
        VISUAL_QA_DIR / "netlify_widget_mobile_430x932_phase_9ab.png",
    ]
    has_screenshot = any(path.exists() for path in screenshots)
    marked_pending = "PLAYWRIGHT_UNAVAILABLE" in text or "PENDING_NETLIFY_REDEPLOY" in text
    return Check("Visual QA evidence or pending marker exists", has_screenshot or marked_pending)


def no_false_mobile_pass() -> Check:
    text = read(RESULT_DOC)
    passed = "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL" in text
    has_netlify_mobile = (VISUAL_QA_DIR / "netlify_widget_mobile_430x932_phase_9ab.png").exists()
    explicit_pass = "Mobile 430x932: PASS" in text and "Netlify visual QA: PASS" in text
    return Check("Mobile pass is not marked without Netlify evidence", not passed or (has_netlify_mobile and explicit_pass))


def frontend_backend_contract_intact() -> Check:
    text = "\n".join(read(path) for path in TEST_SITE_FILES + WIDGET_FILES)
    required = ["/chat/session/start", "/chat/message"]
    missing = [item for item in required if item not in text]
    return Check("Frontend still uses backend chat endpoints", not missing, ", ".join(missing))


def frontend_forbidden_patterns_absent() -> Check:
    findings: list[str] = []
    for path in TEST_SITE_FILES + WIDGET_FILES:
        text = read(path)
        for pattern in FORBIDDEN_FRONTEND_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    return Check("Frontend has no forbidden API/provider/key patterns", not findings, ", ".join(findings))


def public_launch_no_go() -> Check:
    text = "\n".join(read(path) for path in DOC_FILES).lower()
    bad = ["public_launch_decision=go", "public launch complete", "public launch: go"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def real_site_not_modified() -> Check:
    text = read(RESULT_DOC).lower()
    return Check(
        "Real Alte site not modified",
        "real alte site modified: no" in text and "real join.alte.edu.ge modified: no" in text,
    )


def official_facts_documented() -> Check:
    text = "\n".join(read(path) for path in DOC_FILES)
    required = ["240", "120", "5"]
    missing = [item for item in required if item not in text]
    return Check("Official KB facts remain documented", not missing, ", ".join(missing))


def integrated_qa_state_not_downgraded() -> Check:
    text = "\n".join(read(path) for path in DOC_FILES)
    return Check(
        "Integrated QA state not downgraded",
        "BACKEND_DEPLOYED_INTEGRATED_CHAT_ROUTING_QA_PASSED_PENDING_FINAL_APPROVALS" in text
        or "18/18 passed" in text,
    )


def responsive_css_present() -> Check:
    text = "\n".join(read(path) for path in [TEST_SITE_FILES[-1], WIDGET_FILES[0]])
    breakpoint = (
        "@media (max-width: 1024px)" in text
        or "@media (max-width: 900px)" in text
        or "@media (max-width: 640px)" in text
    )
    required = ["max-width:calc(100vw - 16px)", ".cw-win.expanded .cw-side"]
    missing = [item for item in required if item not in text]
    return Check("Responsive mobile CSS guard exists", breakpoint and not missing, ", ".join(missing))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        result_doc_status_valid(),
        visual_evidence_present_or_marked_pending(),
        no_false_mobile_pass(),
        frontend_backend_contract_intact(),
        frontend_forbidden_patterns_absent(),
        public_launch_no_go(),
        real_site_not_modified(),
        official_facts_documented(),
        integrated_qa_state_not_downgraded(),
        responsive_css_present(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
