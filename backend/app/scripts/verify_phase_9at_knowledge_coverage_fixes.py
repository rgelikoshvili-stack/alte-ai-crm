from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FAILURE_MATRIX = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AT_9AS_FAILURE_MATRIX.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AT_KNOWLEDGE_COVERAGE_FIX_RESULT.md"
QA_RESULT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9at_knowledge_coverage_fixes.py"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

SECRET_PATTERNS = ["DATABASE_URL=", "ANTHROPIC_API_KEY=", "OPENAI_API_KEY=", "sk-ant", "sk-"]
REAL_CONTACT_PATTERNS = ["@gmail.com", "+995", "555-", "599-"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    matrix = read(FAILURE_MATRIX)
    result = read(RESULT_DOC)
    qa = read(QA_RESULT)
    tests = read(TEST_FILE)
    public = read(PUBLIC_LAUNCH).lower()
    safety_surface = "\n".join([matrix, result, qa, tests])
    tracked = tracked_files()
    return [
        check("failure matrix exists", FAILURE_MATRIX.exists(), str(FAILURE_MATRIX)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("QA result exists", QA_RESULT.exists(), str(QA_RESULT)),
        check("tests exist", TEST_FILE.exists(), str(TEST_FILE)),
        check("calendar fixes documented", "Calendar Coverage Result" in result and "calendar_mapping" in matrix),
        check("admissions fixes documented", "Admissions Coverage Result" in result and "admissions_mapping" in matrix),
        check("unsupported false positives documented", "Unsupported False-Positive Result" in result and "unsupported_false_positive" in matrix),
        check("IT/EMIS handover documented", "IT/EMIS Handover Persistence Result" in result and "handover_persistence" in matrix),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public and "Public launch: NO-GO" in result),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in result),
        check("contact creation not executed", "CONTACT_FLOW_EXECUTED=NO" in result),
        check("lead/customer/task not created", "LEAD_TASK_CUSTOMER_CREATED=NO" in result),
        check("no secrets", not any(pattern in safety_surface for pattern in SECRET_PATTERNS)),
        check("no real contact data", not any(pattern in safety_surface for pattern in REAL_CONTACT_PATTERNS)),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
