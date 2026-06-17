from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AP_FIX_9AO_QA_BUGS_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
BACKEND_FILES = [
    PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py",
    PROJECT_ROOT / "backend" / "app" / "services" / "knowledge_routing_service.py",
]
FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-strings.jsx",
]
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9ap_fix_9ao_qa_bugs.py"
QA_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_phase_9ap_fix_9ao_bugs_qa.py"
MOJIBAKE_MARKER = "\u00e1\u0192"
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
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
    result = read(RESULT_DOC)
    public = read(PUBLIC_LAUNCH).lower()
    backend = "\n".join(read(path) for path in BACKEND_FILES)
    frontend = "\n".join(read(path) for path in FRONTEND_FILES)
    tests = read(TEST_FILE)
    qa_script = read(QA_SCRIPT)
    combined = "\n".join([result, public, backend, frontend, tests, qa_script])
    safety_docs = "\n".join([result, public, qa_script])
    secret_surface = "\n".join([result, public, frontend, qa_script])
    tracked = tracked_files()

    return [
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("test file exists", TEST_FILE.exists(), str(TEST_FILE)),
        check("production QA script exists", QA_SCRIPT.exists(), str(QA_SCRIPT)),
        check("Computer Science expected facts documented", all(value in result for value in ["9-14 March", "30 March", "Computer Science"])),
        check("calendar source group documented", "academic_calendar_2025_2026" in result + tests + qa_script),
        check("deterministic source-backed fix exists", "is_computer_science_spring_registration_question" in backend),
        check("frontend medicine label fixed", "მედიცინა / MD" in frontend and "Medicine / MD" in frontend),
        check("old medicine label absent", "მედიცინა/MD" not in frontend),
        check("contact textarea prefill fix exists", "latestUserText() || m.text" in frontend and "m.text || latestUserText()" not in frontend),
        check("contact textarea fix documented", "latest user question" in result and "Contact textarea" in result),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public and "no-go" in public and "Public launch: NO-GO" in result),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in result),
        check("contact creation not executed", "CONTACT_FLOW_EXECUTED=NO" in result and "LEAD_TASK_CUSTOMER_CREATED=NO" in result),
        check("no real contact data", all(pattern not in safety_docs for pattern in REAL_CONTACT_PATTERNS)),
        check("no secrets", all(pattern not in secret_surface for pattern in SECRET_PATTERNS)),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("no frontend API key", all(value not in frontend for value in ["ANTHROPIC_API_KEY", "sk-ant"])),
        check("no direct Anthropic frontend call", "api.anthropic.com" not in frontend),
        check("no mojibake marker", MOJIBAKE_MARKER not in combined),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
