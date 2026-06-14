from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
QA_SET_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md"
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]
FORBIDDEN_CLAIM_PATTERNS = [
    r"Real site modified:\s*YES",
    r"Assets uploaded or embedded:\s*YES",
    r"Frontend/Netlify changed:\s*YES",
    r"DB schema/migration/seed/import changed or run:\s*YES",
    r"Secret Manager changed:\s*YES",
    r"CORS changed:\s*YES",
    r"Bridge Hub touched:\s*YES",
    r"Contact flow submitted:\s*YES",
    r"Real contact data sent:\s*YES",
    r"Lead/customer/task created:\s*YES",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def result_row_count(text: str) -> int:
    return text.count("\nFile:")


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    qa_set = read(QA_SET_DOC)
    result = read(RESULT_DOC)
    combined = qa_set + "\n" + result
    tracked = tracked_files()
    row_count = result_row_count(result)

    return [
        check("QA set doc exists", QA_SET_DOC.exists(), str(QA_SET_DOC)),
        check("QA result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("QA set has at least 20 tests", qa_set.count("| 9bd-") >= 20, str(qa_set.count("| 9bd-"))),
        check("QA result has at least 20 rows", row_count >= 20, str(row_count)),
        check("summary counts present", all(marker in result for marker in ["Total tests:", "PASS count:", "PARTIAL count:", "FAIL count:"])),
        check("public launch remains NO-GO", "Public launch: `NO-GO`" in result and "Public launch remains: NO-GO" in result),
        check("live execution completed", "PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_STATUS=COMPLETED" in result),
        check("calendar files covered", all(marker in combined for marker in ["აკადემიური კალენდარი GEO", "Academic Calendar ENG"])),
        check("required dates present", all(marker in combined for marker in [
            "29 September 2025",
            "9 - 14 March 2026",
            "30 March 2026",
            "13 - 25 July 2026",
            "29 June - 11 July 2026",
            "20 July - 1 August 2026",
            "3 - 8 August 2026",
            "30 December 2025 - 4 January 2026",
            "10 - 13 April 2026",
        ])),
        check("ambiguous and unsupported cases covered", all(marker in combined for marker in [
            "გამოცდები როდის არის?",
            "რეგისტრაცია როდის არის?",
            "სემესტრი როდის იწყება?",
            "2031 წლის გაზაფხულის სემესტრი როდის იწყება?",
            "2027 წლის Computer Science-ის გამოცდები როდისაა?",
        ])),
        check("safety no-execution claims present", all(marker in result for marker in [
            "Real site modified: NO",
            "Assets uploaded or embedded: NO",
            "Frontend/Netlify changed: NO",
            "DB schema/migration/seed/import changed or run: NO",
            "Secret Manager changed: NO",
            "CORS changed: NO",
            "Bridge Hub touched: NO",
            "Contact flow submitted: NO",
            "Real contact data sent: NO",
            "Lead/customer/task created: NO",
        ])),
        check("no forbidden safety claims", not any(re.search(pattern, combined, re.I) for pattern in FORBIDDEN_CLAIM_PATTERNS)),
        check("no lead/customer/task marked created", "Lead/customer/task created: YES" not in combined),
        check("no secrets in docs", all(pattern not in combined for pattern in SECRET_PATTERNS)),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
