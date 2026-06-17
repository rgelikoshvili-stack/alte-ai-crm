from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AD_INTEGRATED_ROUTING_FIX_RESULT.md"
FOCUSED_SMOKE = BACKEND_ROOT / "app" / "scripts" / "production_phase_9ad_routing_fix_smoke.py"
INTEGRATED_QA = BACKEND_ROOT / "app" / "scripts" / "production_integrated_chat_routing_operator_qa.py"
REGRESSION_TEST = BACKEND_ROOT / "app" / "tests" / "test_phase_9ad_integrated_routing_fix.py"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str = ""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def result_doc_exists() -> Check:
    return Check("Phase 9AD result doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def scripts_and_tests_exist() -> Check:
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in [FOCUSED_SMOKE, INTEGRATED_QA, REGRESSION_TEST] if not path.exists()]
    return Check("Phase 9AD scripts/tests exist", not missing, f"missing={missing}")


def status_valid() -> Check:
    if not RESULT_DOC.exists():
        return Check("Phase 9AD status is valid", False, "result doc missing")
    text = _read(RESULT_DOC)
    statuses = [
        "PHASE_9AD_ROUTING_FIX_STATUS=PASSED_PENDING_MOBILE_VISUAL_QA_PRIVACY_AND_EMBED_APPROVAL",
        "PHASE_9AD_ROUTING_FIX_STATUS=FAILED_PENDING_ROUTING_FIX",
    ]
    return Check("Phase 9AD status is valid", sum(status in text for status in statuses) == 1)


def fixed_failures_documented() -> Check:
    if not RESULT_DOC.exists():
        return Check("All three Phase 9AC failures documented", False, "result doc missing")
    text = _read(RESULT_DOC).lower()
    required = [
        "admissions question routed to programs",
        "library question routed to international admissions",
        "finance handover question routed to international admissions",
        "admissions_auto_route_fixed",
        "library_auto_route_fixed",
        "finance_handover_route_fixed",
    ]
    missing = [item for item in required if item not in text]
    return Check("All three Phase 9AC failures documented", not missing, f"missing={missing}")


def contact_safety_documented() -> Check:
    if not RESULT_DOC.exists():
        return Check("Contact safety documented", False, "result doc missing")
    text = _read(RESULT_DOC).lower()
    required = [
        "no phone/email/name request",
        "no lead/task/customer created",
        "contact details sent: no",
    ]
    missing = [item for item in required if item not in text]
    return Check("Contact safety documented", not missing, f"missing={missing}")


def public_launch_no_go() -> Check:
    if not RESULT_DOC.exists():
        return Check("Public launch remains NO-GO", False, "result doc missing")
    text = _read(RESULT_DOC).lower()
    return Check(
        "Public launch remains NO-GO",
        "public launch: no-go" in text
        and "public_launch_decision=go" not in text
        and "public launch complete" not in text,
    )


def frontend_contract_safe() -> Check:
    text = _read(TEST_JS) + "\n" + _read(TEST_HTML)
    missing = [endpoint for endpoint in ["/chat/session/start", "/chat/message"] if endpoint not in text]
    forbidden = [item for item in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"] if item in text]
    return Check("Frontend uses backend contract and no forbidden provider calls", not missing and not forbidden, f"missing={missing}; forbidden={forbidden}")


def ignored_secret_dirs_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".env", ".env.*", ".local-secrets", ".local-secrets/*", "backend/.local-secrets"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env and .local-secrets not tracked", not tracked, f"tracked={tracked}")


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        scripts_and_tests_exist(),
        status_valid(),
        fixed_failures_documented(),
        contact_safety_documented(),
        public_launch_no_go(),
        frontend_contract_safe(),
        ignored_secret_dirs_not_tracked(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        state = "PASS" if check.passed else "FAIL"
        print(f"{state} {check.name}: {check.detail}")
    if not all(check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
