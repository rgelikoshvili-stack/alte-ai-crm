from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRIAGE_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BB_PROGRAM_CATALOG_PARTIAL_TRIAGE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9BB_PROGRAM_CATALOG_PARTIAL_FIXES_RESULT.md"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9bb_program_catalog_partial_fixes.py"
LOCAL_QA = PROJECT_ROOT / "backend" / "app" / "scripts" / "local_phase_9bb_program_catalog_partial_fixes_qa.py"
SECRET_PATTERNS = ["DATABASE_URL=", "ANTHROPIC_API_KEY=", "sk-ant", "password=", "token="]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    triage = read(TRIAGE_DOC)
    result = read(RESULT_DOC)
    combined = "\n".join([triage, result, read(TEST_FILE), read(LOCAL_QA)])
    tracked = tracked_files()
    partial_rows = [line for line in triage.splitlines() if line.startswith("| ") and "| QA-" in line]

    return [
        check("triage doc exists", TRIAGE_DOC.exists(), str(TRIAGE_DOC)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("tests exist", TEST_FILE.exists(), str(TEST_FILE)),
        check("local QA script exists", LOCAL_QA.exists(), str(LOCAL_QA)),
        check("all 9 partial cases documented", len(partial_rows) == 9, str(len(partial_rows))),
        check("baseline documented", "11 PASS / 9 PARTIAL / 0 FAIL" in result),
        check("phase status documented", "PHASE_9BB_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY" in result),
        check("decision state documented", "BACKEND_CODE_PROGRAM_CATALOG_PARTIAL_FIXES_READY_PENDING_DEPLOY" in result),
        check("public launch remains NO-GO", "Public launch: NO-GO" in result and "Public launch remains NO-GO" in triage),
        check("deploy status not deployed", "Deploy status: NOT_DEPLOYED_PENDING_APPROVAL" in result),
        check("safety no execution documented", all(marker in result for marker in [
            "Real site modified: NO",
            "Assets uploaded or embedded: NO",
            "Frontend/Netlify changed: NO",
            "Contact flow executed: NO",
            "Lead/customer/task created: NO",
            "DB schema/migration/seed/import: NO",
            "Secret Manager/CORS/Bridge Hub changes: NO",
        ])),
        check("lead/customer/task not marked created", "Lead/customer/task created: YES" not in combined),
        check("all fix categories present", all(marker in triage for marker in [
            "wrong_source",
            "incomplete_answer",
            "clarification_missing",
            "answer_generation_gap",
        ])),
        check("no secrets in phase docs/scripts/tests", all(pattern not in combined for pattern in SECRET_PATTERNS)),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
