from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md"
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read_doc() -> str:
    return RESULT_DOC.read_text(encoding="utf-8") if RESULT_DOC.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def qa_row_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith("| 01_program_catalog.pdf |"))


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    text = read_doc()
    tracked = tracked_files()
    return [
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("phase status present", "PHASE_9BA_PROGRAM_CATALOG_FILE_QA_STATUS=" in text),
        check("decision state present", "BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS" in text),
        check("public launch remains NO-GO", "Public launch: `NO-GO`" in text and "Public launch remains: NO-GO" in text),
        check("program catalog file/source present", "01_program_catalog.pdf" in text and "Higher Education Program Catalog" in text),
        check("all 20 QA rows present", qa_row_count(text) == 20, str(qa_row_count(text))),
        check("summary counts present", all(marker in text for marker in ["Total tests: 20", "PASS count:", "PARTIAL count:", "FAIL count:"])),
        check("required categories present", all(marker in text for marker in ["| main |", "| detailed |", "| clarification |", "| unsupported/safety |"])),
        check("required result states present", all(marker in text for marker in ["| PASS |", "| PARTIAL |"])),
        check("failure root cause summary present", "## Failure Root Causes" in text),
        check("proposed fixes section present", "## Proposed Fixes If Needed" in text),
        check("safety no execution documented", all(marker in text for marker in [
            "Real site modified: NO",
            "Assets uploaded or embedded: NO",
            "DB schema/migration/seed/import changed or run: NO",
            "Secret Manager changed: NO",
            "CORS changed: NO",
            "Bridge Hub touched: NO",
            "Contact flow submitted: NO",
            "Lead/customer/task created: NO",
        ])),
        check("lead/customer/task not marked executed", "Lead/customer/task created: YES" not in text and "lead/customer/task created: YES" not in text),
        check("no secrets in result doc", all(pattern not in text for pattern in SECRET_PATTERNS)),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
