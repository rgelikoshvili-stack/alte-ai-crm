from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DESIGN_DOC = PROJECT_ROOT / "docs" / "architecture" / "PHASE_9AV_CLAUDE_INTENT_ROUTER_DESIGN.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AV_CLAUDE_INTENT_ROUTER_RESULT.md"
SOURCE_DESCRIPTIONS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_group_descriptions.json"
ROUTER_SERVICE = PROJECT_ROOT / "backend" / "app" / "services" / "claude_intent_router_service.py"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9av_claude_intent_router.py"
QA_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "local_phase_9av_claude_intent_router_qa.py"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
FRONTEND_ROOTS = [PROJECT_ROOT / "test_site", PROJECT_ROOT / "widget", PROJECT_ROOT / "frontend"]

FORBIDDEN_SECRET_MARKERS = [
    "DATABASE_URL=",
    "postgres://",
    "postgresql://",
    "sk-" + "ant-",
    "api_key=",
    "password=",
]
MOJIBAKE_MARKERS = ["\u00e1\u0192", "\u00e2", "\u00c3", "\ufffd"]


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
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(result.stdout.splitlines())


def assert_no_secrets(paths: list[Path]) -> None:
    for path in paths:
        text = read(path)
        for marker in FORBIDDEN_SECRET_MARKERS:
            if marker.lower() in text.lower():
                    raise AssertionError(f"Forbidden secret marker {marker!r} in {path}")


def assert_no_mojibake(paths: list[Path]) -> None:
    for path in paths:
        text = read(path)
        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                raise AssertionError(f"Mojibake marker found in {path}")


def assert_frontend_safe() -> None:
    forbidden = ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk-" + "ant-"]
    for root in FRONTEND_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".html"}:
                continue
            text = read(path)
            for marker in forbidden:
                if marker in text:
                    raise AssertionError(f"Frontend forbidden marker {marker!r} found in {path}")


def main() -> int:
    for path in [DESIGN_DOC, RESULT_DOC, SOURCE_DESCRIPTIONS, ROUTER_SERVICE, TEST_FILE, QA_SCRIPT]:
        assert_exists(path)

    source_data = json.loads(read(SOURCE_DESCRIPTIONS))
    groups = source_data.get("source_groups")
    if not isinstance(groups, list) or len(groups) < 10:
        raise AssertionError("source_group_descriptions.json must contain at least 10 source groups")
    for item in groups:
        for key in [
            "id",
            "description_ka",
            "description_en",
            "good_for",
            "not_good_for",
            "fallback_department",
            "exact_answer_allowed",
            "needs_operator_if_missing_source",
        ]:
            if key not in item:
                raise AssertionError(f"source group {item.get('id')} missing {key}")

    assert_contains(
        DESIGN_DOC,
        [
            "strict JSON",
            "approved source",
            "Scoped Retrieval Enforcement",
            "Deterministic Safety Overrides",
            "router_validation_status=invalid_source_groups",
            "allow_category_fallback=true",
            "Claude Call Count Control",
            "hallucination",
            "Operator CRM",
            "NO-GO",
        ],
    )
    assert_contains(
        RESULT_DOC,
        [
            "PHASE_9AV_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY",
            "BACKEND_CODE_CLAUDE_INTENT_ROUTER_READY_PENDING_DEPLOY",
            "NOT_DEPLOYED_PENDING_APPROVAL",
            "selected source groups are now hard retrieval boundaries",
            "deterministic backend overrides beat valid Claude JSON",
            "deterministic fallback checks operator/contact intent before forced source-group routing",
            "operator department inference uses department_for_operator_request",
            "duplicate operator detector was removed",
            "Georgian encoding cleanup",
            "allow_category_fallback=true",
            "invalid_source_groups",
            "empty_source_groups",
            "deterministic_override_reason",
            "used_legacy_ai_analysis",
            "Public launch:",
            "NO-GO",
            "Contact creation executed: NO",
            "Lead/customer/task created: NO",
        ],
    )
    assert_contains(
        ROUTER_SERVICE,
        [
            "ClaudeIntentRoute",
            "validate_router_payload",
            "router_validation_status",
            "source_groups_to_search",
            "route_decision_from_intent",
            "fallback_intent_route",
            "deterministic_override_for_message",
            "known_broad_question",
            "department_for_operator_request",
        ],
    )
    assert_contains(
        PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py",
        [
            "search_approved_sources_for_groups",
            "retrieval_result_belongs_to_source_group",
            "should_use_legacy_ai_analysis",
            "used_grounded_answer_generator",
            "allow_category_fallback",
            "deterministic_override_applied",
        ],
    )
    if read(ROUTER_SERVICE).count("def has_operator_request(") != 1:
        raise AssertionError("Expected exactly one has_operator_request implementation")

    launch_text = read(PUBLIC_LAUNCH)
    if "NO-GO" not in launch_text:
        raise AssertionError("Public launch is not documented as NO-GO")

    tracked = tracked_files()
    if ".env" in tracked or ".local-secrets" in tracked:
        raise AssertionError(".env or .local-secrets is tracked")

    assert_frontend_safe()
    assert_no_secrets([DESIGN_DOC, RESULT_DOC, SOURCE_DESCRIPTIONS, ROUTER_SERVICE, TEST_FILE, QA_SCRIPT])
    assert_no_mojibake([DESIGN_DOC, RESULT_DOC, SOURCE_DESCRIPTIONS, ROUTER_SERVICE])
    print("PHASE_9AV_CLAUDE_INTENT_ROUTER_VERIFIER=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
