from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_PACKAGE.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
PHASE_9AB_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AB_MOBILE_RESPONSIVE_WIDGET_FIX_RESULT.md"
PHASE_9AD_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AD_INTEGRATED_ROUTING_FIX_RESULT.md"

FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
]

FORBIDDEN_FRONTEND_PATTERNS = [
    re.compile(r"/api/chat", re.IGNORECASE),
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def result_doc_exists() -> Check:
    return Check("Phase 9AE package exists", RESULT_DOC.exists(), str(RESULT_DOC))


def status_valid() -> Check:
    text = read(RESULT_DOC)
    required = [
        "PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_STATUS=NO_GO_PENDING_PRIVACY_CONTACT_ASSET_EMBED_AND_REAL_DOMAIN_SMOKE",
        "BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL",
        "Public launch: NO-GO",
    ]
    missing = [item for item in required if item not in text]
    return Check("Phase 9AE status remains NO-GO", not missing, ", ".join(missing))


def approvals_are_pending() -> Check:
    text = read(RESULT_DOC)
    required = [
        "OFFICIAL_PRIVACY_URL_STATUS=PENDING",
        "CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST",
        "FINAL_WIDGET_ASSET_URL_STATUS=PENDING_APPROVAL_AND_UPLOAD",
        "site embed status: NOT_EXECUTED",
        "Real-domain smoke",
    ]
    missing = [item for item in required if item not in text]
    return Check("Required approvals remain pending", not missing, ", ".join(missing))


def proposed_asset_and_snippet_present() -> Check:
    text = read(RESULT_DOC)
    required = [
        "https://alte.edu.ge/assets/alte-ai-chat-widget.js",
        "window.AlteChatWidgetConfig",
        "apiBaseUrl",
        "sourceDomain",
        "join.alte.edu.ge",
    ]
    missing = [item for item in required if item not in text]
    return Check("Proposed asset URL and embed snippet are present", not missing, ", ".join(missing))


def real_domain_smoke_checklist_present() -> Check:
    text = read(RESULT_DOC)
    required = ["240 ECTS", "120 ECTS", "5 years", "9-14 March", "2031", "No lead/task/customer"]
    missing = [item for item in required if item not in text]
    return Check("Real-domain smoke checklist covers required cases", not missing, ", ".join(missing))


def dirty_tree_triage_present() -> Check:
    text = read(RESULT_DOC)
    required = ["Dirty Tree Triage", "README.md", "FULL_PROJECT_AUDIT_2026_05_30.md", "leave pending"]
    missing = [item for item in required if item not in text]
    return Check("Dirty tree triage is documented", not missing, ", ".join(missing))


def frontend_contract_intact() -> Check:
    text = "\n".join(read(path) for path in FRONTEND_FILES)
    required = ["/chat/session/start", "/chat/message"]
    missing = [item for item in required if item not in text]
    return Check("Frontend still uses approved backend chat endpoints", not missing, ", ".join(missing))


def forbidden_frontend_patterns_absent() -> Check:
    findings: list[str] = []
    for path in FRONTEND_FILES:
        text = read(path)
        for pattern in FORBIDDEN_FRONTEND_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    return Check("Frontend has no forbidden direct AI/API/key patterns", not findings, ", ".join(findings))


def public_launch_not_go() -> Check:
    text = "\n".join(read(path).lower() for path in [RESULT_DOC, PUBLIC_LAUNCH])
    bad = ["public_launch_decision=go", "public launch: go", "public launch complete"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def real_site_not_modified() -> Check:
    text = read(RESULT_DOC).lower()
    required = ["real `alte.edu.ge` modified: no", "real `join.alte.edu.ge` modified: no"]
    missing = [item for item in required if item not in text]
    return Check("Real Alte site remains unmodified", not missing, ", ".join(missing))


def technical_passes_referenced() -> Check:
    text = "\n".join(read(path) for path in [RESULT_DOC, PHASE_9AB_DOC, PHASE_9AD_DOC])
    required = ["18/18", "sidebarVisible=false", "430x932", "390x844", "375x667"]
    missing = [item for item in required if item not in text]
    return Check("Current passing technical checks are referenced", not missing, ", ".join(missing))


def tracked_secret_files_absent() -> Check:
    tracked = set(git_lines("ls-files"))
    forbidden = [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
    return Check("No .env or .local-secrets files are tracked", not forbidden, ", ".join(forbidden))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        status_valid(),
        approvals_are_pending(),
        proposed_asset_and_snippet_present(),
        real_domain_smoke_checklist_present(),
        dirty_tree_triage_present(),
        frontend_contract_intact(),
        forbidden_frontend_patterns_absent(),
        public_launch_not_go(),
        real_site_not_modified(),
        technical_passes_referenced(),
        tracked_secret_files_absent(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
