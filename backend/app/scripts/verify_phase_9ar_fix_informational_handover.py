from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_RESULT.md"
QA_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_phase_9ar_fix_informational_handover_qa.py"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9ar_fix_informational_handover_pollution.py"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "OPENAI_API_KEY=",
    "sk-ant",
    "sk-",
]
REAL_CONTACT_PATTERNS = [
    "@gmail.com",
    "@alte.edu.ge",
    "+995",
    "555-",
    "599-",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    result_doc = read(RESULT_DOC)
    qa_script = read(QA_SCRIPT)
    test_file = read(TEST_FILE)
    public_launch = read(PUBLIC_LAUNCH).lower()
    safety_surface = "\n".join([result_doc, qa_script])
    code_and_tests = "\n".join([qa_script, test_file])
    tracked = tracked_files()

    return [
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("QA script exists", QA_SCRIPT.exists(), str(QA_SCRIPT)),
        check("test file exists", TEST_FILE.exists(), str(TEST_FILE)),
        check("status documented", "PHASE_9AR_FIX_STATUS=PASSED_PENDING_APPROVALS" in result_doc),
        check("decision state documented", "BACKEND_DEPLOYED_CHATBOT_OPERATOR_ALIGNMENT_FIX_VERIFIED_PENDING_APPROVALS" in result_doc),
        check("Bachelor behavior documented", "Bachelor ECTS" in result_doc and "should_handover=false" in result_doc and "human_handover=false" in result_doc),
        check("source-backed informational policy documented", "Source-backed informational answers now clear `should_handover`" in result_doc),
        check("explicit operator handover documented", "Explicit operator request still has `should_handover=true`" in result_doc),
        check("unsupported fallback handover documented", "Unsupported no-source answer still has operator fallback" in result_doc),
        check("wait-for-operator documented", "Wait-for-operator still sets `waiting_for_operator` and `human_handover=true`" in result_doc),
        check("polling limitation documented", "VISITOR_SIDE_OPERATOR_REPLY_POLLING=NOT_ACTIVE" in result_doc),
        check("production QA passed documented", "36/36 passed" in result_doc and "116/116 passed" in result_doc),
        check("deployed revision documented", "alte-ai-crm-backend-00037-7xh" in result_doc),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public_launch and "Public launch: NO-GO" in result_doc),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in result_doc and "Real Alte site modified: NO" in result_doc),
        check("no migration or seed", "Production DB migration run: NO" in result_doc and "Production seed run: NO" in result_doc),
        check("contact flow not executed", "CONTACT_FLOW_EXECUTED=NO" in result_doc),
        check("lead/customer/task not created", "LEAD_TASK_CUSTOMER_CREATED=NO" in result_doc),
        check("QA script validates no CRM creation", "created_lead_id" in qa_script and "created_task_id" in qa_script),
        check("tests cover source backed false", "should_handover\"] is False" in code_and_tests and "human_handover is False" in code_and_tests),
        check("tests cover wait true", "waiting_for_operator" in code_and_tests and "human_handover is True" in code_and_tests),
        check("no real contact data", all(pattern not in safety_surface for pattern in REAL_CONTACT_PATTERNS)),
        check("no secrets", all(pattern not in safety_surface for pattern in SECRET_PATTERNS)),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
