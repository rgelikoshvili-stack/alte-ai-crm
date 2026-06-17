from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRIAGE_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AX_FINAL_TWO_FAILURES_TRIAGE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AX_FINAL_TWO_9AS_FAILURES_RESULT.md"
LOCAL_QA = PROJECT_ROOT / "backend" / "app" / "scripts" / "local_phase_9ax_final_two_9as_failures_qa.py"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9ax_final_two_9as_failures.py"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

FORBIDDEN_SECRET_MARKERS = [
    "DATABASE_URL=",
    "postgres://",
    "postgresql://",
    "sk-" + "ant-",
    "api_key=",
    "password=",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")


def assert_contains(path: Path, required: list[str]) -> None:
    text = read(path)
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"{path} missing required text: {missing}")


def tracked_files() -> set[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
    return set(result.stdout.splitlines())


def assert_no_secrets(paths: list[Path]) -> None:
    for path in paths:
        text = read(path).lower()
        for marker in FORBIDDEN_SECRET_MARKERS:
            if marker.lower() in text:
                raise AssertionError(f"Forbidden secret marker {marker!r} in {path}")


def main() -> int:
    for path in [TRIAGE_DOC, RESULT_DOC, LOCAL_QA, TEST_FILE]:
        assert_exists(path)

    assert_contains(
        TRIAGE_DOC,
        [
            "admission_without_exams_ka",
            "english_program_requirements_en",
            "admissions_rules",
            "international_admissions_sources",
            "No approved-source expectation was weakened",
            "Public launch remains NO-GO",
        ],
    )
    assert_contains(
        RESULT_DOC,
        [
            "PHASE_9AX_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY",
            "BACKEND_CODE_FINAL_9AS_FAILURES_FIXED_PENDING_DEPLOY",
            "NOT_DEPLOYED_PENDING_APPROVAL",
            "PENDING_BACKEND_DEPLOY",
            "admission-without-exams",
            "English-language program requirement",
            "Contact flow executed: NO",
            "Lead/customer/task created: NO",
            "DB migration/seed/import: NO",
            "Public launch: NO-GO",
        ],
    )
    assert_contains(
        LOCAL_QA,
        [
            "admission_without_exams_validated_route_admissions",
            "english_program_requirements_international",
            "generic_programs_not_international",
            "operator_handover_no_source_group",
            "public_launch_no_go",
        ],
    )
    assert_contains(
        TEST_FILE,
        [
            "test_admission_without_exams_ka_routes_to_admissions_not_exams",
            "test_english_program_requirements_routes_to_international_not_programs",
            "test_generic_program_question_does_not_become_international_admissions",
            "test_public_launch_remains_no_go",
        ],
    )

    if "NO-GO" not in read(PUBLIC_LAUNCH):
        raise AssertionError("Public launch must remain NO-GO")

    tracked = tracked_files()
    if ".env" in tracked or ".local-secrets" in tracked:
        raise AssertionError(".env or .local-secrets is tracked")

    assert_no_secrets([TRIAGE_DOC, RESULT_DOC, LOCAL_QA, TEST_FILE])
    print("PHASE_9AX_FINAL_TWO_9AS_FAILURES_VERIFIER=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
