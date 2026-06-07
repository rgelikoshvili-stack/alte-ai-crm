from __future__ import annotations

import json
from pathlib import Path

from app.services.chat_service import clean_public_answer_text
from app.services.claude_intent_router_service import fallback_intent_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_MAP = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "global_source_map.json"
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

REQUIRED_FIELDS = {
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


def load_source_map() -> dict:
    return json.loads(SOURCE_MAP.read_text(encoding="utf-8"))


def load_source_groups() -> dict:
    data = json.loads(SOURCE_GROUPS.read_text(encoding="utf-8"))
    return {item["id"]: item for item in data["source_groups"]}


def test_global_source_map_loads_and_covers_phase_a_sources():
    data = load_source_map()

    assert data["phase"] == "9BC"
    assert data["public_launch_status"] == "NO-GO"
    assert len(data["sources"]) >= 19


def test_every_source_has_required_routing_and_clarification_fields():
    data = load_source_map()

    for source in data["sources"]:
        missing = REQUIRED_FIELDS - set(source)
        assert missing == set(), f"{source.get('source_id')} missing {missing}"
        assert source["source_group"]
        assert source["route"]
        assert source["label_ka"]
        assert source["label_en"]
        assert source["use_when"]
        assert source["do_not_use_when"]
        assert source["clarification_question_ka"]
        assert source["clarification_question_en"]
        assert source["source_group_status"] in {"configured", "missing_source_group_config"}
        assert isinstance(source["routable"], bool)
        assert isinstance(source["qa_ready"], bool)


def test_configured_source_map_entries_have_strict_source_group_membership():
    data = load_source_map()
    groups = load_source_groups()

    for source in data["sources"]:
        status = source["source_group_status"]
        if status == "missing_source_group_config":
            assert source["routable"] is False
            assert source["qa_ready"] is False
            assert "Strict source group membership" in source["notes"]
            continue

        assert status == "configured"
        assert source["routable"] is True
        assert source["qa_ready"] is True
        group = groups[source["source_group"]]
        membership = {
            str(value).lower()
            for key in ["source_files", "source_keys", "document_ids"]
            for value in group.get(key, [])
        }
        identities = {
            source["source_id"].lower(),
            source["file_name"].lower(),
            source["label_ka"].lower(),
            source["label_en"].lower(),
        }
        assert membership & identities, f"{source['source_id']} lacks strict source-group membership"


def test_standalone_phase_a_config_gaps_are_not_routable_or_qa_ready():
    sources = {item["source_id"]: item for item in load_source_map()["sources"]}

    for source_id in [
        "ects_credit_recognition",
        "exam_regulation",
        "student_services",
        "student_rights",
        "ombudsman",
        "special_needs",
        "ai_policy",
        "plagiarism",
        "ethics_code",
    ]:
        item = sources[source_id]
        assert item["source_group_status"] == "missing_source_group_config"
        assert item["routable"] is False
        assert item["qa_ready"] is False


def test_ambiguous_prompts_return_clarification_without_source_retrieval():
    cases = {
        "გამოცდებზე მაინტერესებს": "გამოცდების თარიღები",
        "პროგრამის კრედიტები მაინტერესებს": "რომელი პროგრამის კრედიტები",
        "მიღება მაინტერესებს": "გამოცდების გარეშე",
        "სტატუსზე კითხვა მაქვს": "შეჩერება",
    }

    for question, expected_fragment in cases.items():
        route = fallback_intent_route(question)
        assert route.needs_clarification is True
        assert route.source_groups_to_search == []
        assert route.operator_needed is False
        assert expected_fragment in (route.clarification_question or "")


def test_priority_routes_admission_exam_rule_and_exam_date_distinctly():
    admissions = fallback_intent_route("ეროვნული გამოცდების გარეშე ჩარიცხვა")
    exam_rule = fallback_intent_route("დასკვნით გამოცდაზე დაშვების წესი როგორია?")
    exam_date = fallback_intent_route("დასკვნითი გამოცდები როდის არის?")

    assert admissions.department == "admissions"
    assert admissions.source_groups_to_search[0] == "admissions_rules"

    assert exam_rule.department == "study_process"
    assert exam_rule.source_groups_to_search[0] == "exams_and_assessment"

    assert exam_date.department == "academic_calendar"
    assert exam_date.source_groups_to_search[0] == "academic_calendar_2025_2026"


def test_generic_credit_question_asks_clarification_not_program_catalog_retrieval():
    route = fallback_intent_route("რამდენი კრედიტია პროგრამა?")

    assert route.needs_clarification is True
    assert route.source_groups_to_search == []
    assert route.operator_needed is False
    assert "რომელი პროგრამის კრედიტები" in (route.clarification_question or "")


def test_unsupported_prompt_does_not_get_source_groups_or_hallucination_route():
    route = fallback_intent_route("2031 წლის კოსმოსური კამპუსის პროგრამაზე რა მოთხოვნებია?")

    assert route.unsupported_likely is True
    assert route.source_groups_to_search == []
    assert route.operator_needed is False


def test_operator_request_with_phone_number_still_handover_not_unsupported():
    route = fallback_intent_route("ოპერატორთან დამაკავშირე, ჩემი ტელეფონის ნომერია 555123456")

    assert route.operator_needed is True
    assert route.unsupported_likely is False
    assert route.source_groups_to_search == []
    assert route.department == "human_operator"


def test_no_source_label_or_internal_noise_in_clean_public_answer():
    cleaned = clean_public_answer_text(
        "საბაკალავრო პროგრამა მოიცავს 240 ECTS კრედიტს. "
        "official_academic_rules_full_p022_c050 source_group=official_academic_rules chunk 2"
    )
    lowered = cleaned.lower()

    assert "240 ECTS" in cleaned
    for forbidden in ["official_academic_rules", "source_group", "chunk", "p022_c050"]:
        assert forbidden not in lowered


def test_public_launch_remains_no_go():
    assert "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")
