from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRIAGE_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BE_ACADEMIC_CALENDAR_FAILURE_TRIAGE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9BE_ACADEMIC_CALENDAR_FIXES_RESULT.md"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9be_academic_calendar_fixes.py"
LOCAL_QA = PROJECT_ROOT / "backend" / "app" / "scripts" / "local_phase_9be_academic_calendar_fixes_qa.py"
SECRET_PATTERNS = ["DATABASE_URL=", "ANTHROPIC_API_KEY=", "sk-ant", "password=", "token="]
FORBIDDEN_CLAIMS = [
    r"Real site modified:\s*YES",
    r"Assets uploaded or embedded:\s*YES",
    r"Frontend/Netlify changed:\s*YES",
    r"DB schema/migration/seed/import changed or run:\s*YES",
    r"Secret Manager changed:\s*YES",
    r"CORS changed:\s*YES",
    r"Bridge Hub touched:\s*YES",
    r"Contact flow submitted:\s*YES",
    r"Lead/customer/task created:\s*YES",
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
    triage = read(TRIAGE_DOC)
    result = read(RESULT_DOC)
    combined = triage + "\n" + result
    tracked = tracked_files()
    root_causes = [
        "wrong_source_program_catalog",
        "missing_calendar_priority",
        "generic_answer_generation",
        "clarification_missing",
        "future_year_unsupported_failure",
        "program_group_confusion",
        "stale_expectation",
    ]
    return [
        check("triage doc exists", TRIAGE_DOC.exists(), str(TRIAGE_DOC)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("tests exist", TEST_FILE.exists(), str(TEST_FILE)),
        check("local QA exists", LOCAL_QA.exists(), str(LOCAL_QA)),
        check("all 26 non-PASS rows documented", triage.count("| 9bd-") == 26, str(triage.count("| 9bd-"))),
        check("root cause taxonomy documented", all(root in triage for root in root_causes)),
        check("future year guard documented", "future year guard" in combined.lower() and "2027" in combined and "2031" in combined),
        check("clarification rules documented", "clarification" in combined.lower() and "გამოცდები როდის არის?" in combined),
        check("local QA 30/30 documented", "Local QA result: 30 PASS / 0 PARTIAL / 0 FAIL" in result),
        check("review over-capture fix documented", "registration` alone is not a calendar marker" in combined and "Over-capture regression: 23 PASS / 0 FAIL" in combined),
        check("english date substring fix documented", "word-boundary" in combined.lower() and "updated" in combined and "candidate" in combined and "outdated" in combined),
        check("computer science shortcut fix documented", "Computer Science spring" in combined and "forced-source shortcut was removed" in combined),
        check("chat helper substring fix documented", "direct `chat_service.py`" in combined and "direct deterministic helper probes" in combined),
        check("grounded fallback over-capture fix documented", "grounded_source_backed_reply" in combined and "Fallback over-capture regression: 7 PASS / 0 FAIL" in combined),
        check("stale bachelor registration fix documented", "stale Bachelor registration" in combined and "Stale-date regression: 4 PASS / 0 FAIL" in combined),
        check("admissions requirements exclusions documented", all(marker in combined.lower() for marker in ["requirements", "documents", "admissions"])),
        check("phase status code ready", "PHASE_9BE_STATUS=CODE_READY_PENDING_REVIEW" in result),
        check("decision state pending review", "BACKEND_CODE_ACADEMIC_CALENDAR_QA_FIXES_READY_PENDING_REVIEW" in result),
        check("public launch NO-GO", "Public launch: `NO-GO`" in result and "Public launch remains: NO-GO" in result),
        check("deploy not performed", "Deploy status: NOT_DEPLOYED" in result),
        check("safety claims present", all(marker in result for marker in [
            "Real site modified: NO",
            "Assets uploaded or embedded: NO",
            "Frontend/Netlify changed: NO",
            "DB schema/migration/seed/import changed or run: NO",
            "Secret Manager changed: NO",
            "CORS changed: NO",
            "Bridge Hub touched: NO",
            "Contact flow submitted: NO",
            "Lead/customer/task created: NO",
        ])),
        check("no forbidden safety claims", not any(re.search(pattern, combined, re.I) for pattern in FORBIDDEN_CLAIMS)),
        check("no secrets in docs", all(pattern not in combined for pattern in SECRET_PATTERNS)),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
