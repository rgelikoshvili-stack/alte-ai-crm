from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRIAGE_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AW_9AV_PRODUCTION_FAILURE_TRIAGE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AW_9AV_FAILURE_TUNING_RESULT.md"
LOCAL_QA = PROJECT_ROOT / "backend" / "app" / "scripts" / "local_phase_9aw_9av_failure_tuning_qa.py"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9aw_9av_failure_tuning.py"
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
            "21 failing 9AS cases",
            "status_suspension_ka",
            "credit_recognition_ka",
            "english_program_requirements_en",
            "unsupported_library_rules_en",
            "operator_finance_handover_en",
            "router_selection_bug",
            "stale_test_expectation",
        ],
    )
    if read(TRIAGE_DOC).count("| `") < 21:
        raise AssertionError("Triage table must document at least 21 failed case rows")

    assert_contains(
        RESULT_DOC,
        [
            "PHASE_9AW_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY",
            "BACKEND_CODE_9AV_FAILURE_TUNING_READY_PENDING_DEPLOY",
            "PENDING_BACKEND_DEPLOY",
            "NOT_DEPLOYED_PENDING_APPROVAL",
            "Public launch: NO-GO",
            "Contact flow executed: NO",
            "Lead/customer/task created: NO",
            "DB migration/seed/import: NO",
            "Secret Manager/CORS/Bridge Hub changes: NO",
        ],
    )
    assert_contains(
        LOCAL_QA,
        [
            "status_route_specialized",
            "georgian_final_exam_route_specialized",
            "fallback_georgian_final_exam_primary_exams",
            "operator_reply_duplicate_removed",
            "invalid_group_not_specialized",
            "public_launch_no_go",
        ],
    )
    assert_contains(
        TEST_FILE,
        [
            "test_valid_official_status_route_specializes_to_student_status_group",
            "test_georgian_final_exam_admission_route_specializes_to_exams_group",
            "test_fallback_georgian_final_exam_admission_primary_group_is_exams",
            "test_operator_reply_has_single_georgian_return_path",
            "test_public_launch_remains_no_go",
        ],
    )

    if "NO-GO" not in read(PUBLIC_LAUNCH):
        raise AssertionError("Public launch must remain NO-GO")

    tracked = tracked_files()
    if ".env" in tracked or ".local-secrets" in tracked:
        raise AssertionError(".env or .local-secrets is tracked")

    assert_no_secrets([TRIAGE_DOC, RESULT_DOC, LOCAL_QA, TEST_FILE])
    print("PHASE_9AW_9AV_FAILURE_TUNING_VERIFIER=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
