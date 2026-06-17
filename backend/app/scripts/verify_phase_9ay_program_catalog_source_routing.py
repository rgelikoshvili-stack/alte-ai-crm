from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
SOURCE_DESCRIPTIONS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_group_descriptions.json"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9ay_program_catalog_source_routing.py"
QA_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_phase_9ay_program_catalog_source_qa.py"
QA_RESULT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AY_PROGRAM_CATALOG_SOURCE_QA_RESULT.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AY_PROGRAM_CATALOG_SOURCE_ROUTING_FIX_RESULT.md"
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


def assert_program_catalog_group() -> None:
    groups = {item["id"]: item for item in json.loads(read(SOURCE_GROUPS))["source_groups"]}
    group = groups.get("program_catalog_sources")
    if not group:
        raise AssertionError("program_catalog_sources source group is missing")
    identity = " ".join(group.get("source_files", []) + group.get("source_keys", []))
    for marker in ["01_program_catalog.pdf", "Higher Education Program Catalog", "official_alte_8_pdf_kb_01_01_program_catalog"]:
        if marker not in identity:
            raise AssertionError(f"program_catalog_sources missing identity marker: {marker}")
    if group.get("source_domain") != "official_alte_pdf_kb":
        raise AssertionError("program_catalog_sources must scope to official_alte_pdf_kb")


def main() -> int:
    for path in [SOURCE_GROUPS, SOURCE_DESCRIPTIONS, TEST_FILE, QA_SCRIPT, QA_RESULT, RESULT_DOC]:
        assert_exists(path)

    assert_program_catalog_group()
    assert_contains(SOURCE_DESCRIPTIONS, ["program_catalog_sources", "Higher Education Program Catalog", "program count"])
    assert_contains(
        TEST_FILE,
        [
            "test_catalog_questions_force_program_catalog_not_academic_rules",
            "test_program_catalog_strict_source_membership_accepts_catalog_only",
            "test_mandatory_existing_routes_are_preserved",
            "program_catalog_sources",
        ],
    )
    assert_contains(
        QA_SCRIPT,
        [
            "program_catalog_sources",
            "official_academic_rules_not_primary",
            "Contact flow submitted: NO",
            "Lead/customer/task created",
        ],
    )
    assert_contains(
        RESULT_DOC,
        [
            "PHASE_9AY_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY",
            "BACKEND_CODE_PROGRAM_CATALOG_SOURCE_ROUTING_READY_PENDING_DEPLOY",
            "program_catalog_sources",
            "01_program_catalog.pdf",
            "Higher Education Program Catalog",
            "Public launch: NO-GO",
            "Contact flow executed: NO",
            "Lead/customer/task created: NO",
            "DB migration/seed/import: NO",
        ],
    )

    if "NO-GO" not in read(PUBLIC_LAUNCH):
        raise AssertionError("Public launch must remain NO-GO")

    tracked = tracked_files()
    if ".env" in tracked or ".local-secrets" in tracked:
        raise AssertionError(".env or .local-secrets is tracked")

    assert_no_secrets([SOURCE_GROUPS, SOURCE_DESCRIPTIONS, TEST_FILE, QA_SCRIPT, QA_RESULT, RESULT_DOC])
    print("PHASE_9AY_PROGRAM_CATALOG_SOURCE_ROUTING_VERIFIER=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
