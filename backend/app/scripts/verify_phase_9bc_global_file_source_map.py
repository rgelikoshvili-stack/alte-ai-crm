from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_MAP_DOC = PROJECT_ROOT / "docs" / "knowledge_evidence" / "PHASE_9BC_GLOBAL_FILE_SOURCE_MAP.md"
SOURCE_MAP_JSON = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "global_source_map.json"
QA_TEMPLATE = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BC_FILE_QA_TEMPLATE.md"
LOCAL_QA_FRAMEWORK = PROJECT_ROOT / "backend" / "app" / "scripts" / "local_phase_9bc_file_by_file_qa_framework.py"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9bc_global_file_source_map.py"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9BC_GLOBAL_FILE_SOURCE_MAP_AND_QA_FRAMEWORK_RESULT.md"


REQUIRED_JSON_FIELDS = {
    "source_id",
    "file_name",
    "source_group",
    "route",
    "department",
    "label_ka",
    "label_en",
    "use_when",
    "do_not_use_when",
    "clarification_triggers",
    "clarification_question_ka",
    "clarification_question_en",
    "unsupported_patterns",
    "priority_rules",
    "source_group_status",
    "routable",
    "qa_ready",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _tracked_secret_files() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except Exception:
        return ["git ls-files unavailable"]
    tracked = completed.stdout.splitlines()
    return [
        item
        for item in tracked
        if item.endswith(".env") or ".local-secrets" in item or item.endswith(".local-secrets")
    ]


def main() -> int:
    failures: list[str] = []

    for path in [SOURCE_MAP_DOC, SOURCE_MAP_JSON, QA_TEMPLATE, LOCAL_QA_FRAMEWORK, TEST_FILE, RESULT_DOC]:
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(PROJECT_ROOT)}")

    if SOURCE_MAP_JSON.exists():
        data = json.loads(_read(SOURCE_MAP_JSON))
        sources = data.get("sources", [])
        source_groups = {}
        source_groups_path = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
        if source_groups_path.exists():
            source_groups_data = json.loads(_read(source_groups_path))
            source_groups = {item["id"]: item for item in source_groups_data.get("source_groups", [])}
        if len(sources) < 19:
            failures.append(f"source map should contain at least 19 Phase A sources, found {len(sources)}")
        for index, source in enumerate(sources, start=1):
            missing = sorted(REQUIRED_JSON_FIELDS - set(source))
            if missing:
                failures.append(f"source {index} missing fields: {', '.join(missing)}")
            for field in ["use_when", "do_not_use_when", "clarification_triggers", "unsupported_patterns", "priority_rules"]:
                if not isinstance(source.get(field), list) or not source.get(field):
                    failures.append(f"source {source.get('source_id', index)} has empty/non-list {field}")
            status = source.get("source_group_status")
            if status == "configured":
                if source.get("routable") is not True or source.get("qa_ready") is not True:
                    failures.append(f"configured source {source.get('source_id')} must be routable and qa_ready")
                group = source_groups.get(source.get("source_group"))
                if not group:
                    failures.append(f"configured source {source.get('source_id')} references unknown source_group")
                elif not _source_group_has_strict_membership(source, group):
                    failures.append(
                        f"configured source {source.get('source_id')} lacks strict membership in {source.get('source_group')}"
                    )
            elif status == "missing_source_group_config":
                if source.get("routable") is not False or source.get("qa_ready") is not False:
                    failures.append(f"config-gap source {source.get('source_id')} must have routable=false and qa_ready=false")
                if "Strict source group membership" not in str(source.get("notes", "")):
                    failures.append(f"config-gap source {source.get('source_id')} must document strict membership gap")
            else:
                failures.append(f"source {source.get('source_id', index)} has invalid source_group_status: {status}")
        if data.get("public_launch_status") != "NO-GO":
            failures.append("global_source_map.json must keep public_launch_status=NO-GO")

    if SOURCE_MAP_DOC.exists():
        doc = _read(SOURCE_MAP_DOC)
        for marker in [
            "გამოცდებზე მაინტერესებს",
            "პროგრამის კრედიტები მაინტერესებს",
            "მიღება მაინტერესებს",
            "სტატუსზე კითხვა მაქვს",
            "Public launch remains: `NO-GO`",
        ]:
            if marker not in doc:
                failures.append(f"source map doc missing marker: {marker}")

    if RESULT_DOC.exists():
        result = _read(RESULT_DOC)
        for marker in [
            "PHASE_9BC_STATUS=CODE_READY_PENDING_REVIEW",
            "BACKEND_CODE_GLOBAL_FILE_QA_FRAMEWORK_READY_PENDING_REVIEW",
            "Public launch: NO-GO",
            "Deploy status: NOT_DEPLOYED",
            "No real site/upload/embed/contact-flow/DB/Secret/CORS changes",
            "No lead/customer/task created",
        ]:
            if marker not in result:
                failures.append(f"result doc missing marker: {marker}")

    tracked_secret_files = _tracked_secret_files()
    if tracked_secret_files:
        failures.append(f"tracked secret/local files found: {tracked_secret_files}")

    if failures:
        print("Phase 9BC verifier: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Phase 9BC verifier: PASS")
    print("Global source map, QA template, local QA framework, tests, and result doc are present.")
    print("Public launch remains NO-GO. No real site/upload/embed/contact-flow/DB/Secret/CORS changes claimed.")
    return 0


def _source_group_has_strict_membership(source: dict, group: dict) -> bool:
    identity_values = {
        str(source.get("source_id", "")).lower(),
        str(source.get("file_name", "")).lower(),
        str(source.get("label_en", "")).lower(),
        str(source.get("label_ka", "")).lower(),
    }
    membership_values: set[str] = set()
    for key in ["source_files", "source_keys", "document_ids"]:
        for value in group.get(key, []) or []:
            membership_values.add(str(value).lower())
    return any(value and value in membership_values for value in identity_values)


if __name__ == "__main__":
    raise SystemExit(main())
