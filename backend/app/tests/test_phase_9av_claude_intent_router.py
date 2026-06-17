from __future__ import annotations

import json
import inspect
from pathlib import Path
from types import SimpleNamespace

from app.services import chat_service
from app.services import claude_intent_router_service
from app.services.claude_intent_router_service import ClaudeIntentRoute
from app.services.claude_intent_router_service import (
    allowed_source_group_ids,
    fallback_intent_route,
    load_source_group_descriptions,
    route_decision_from_intent,
    validate_router_payload,
)
from app.services.knowledge_routing_service import classify_knowledge_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
SOURCE_DESCRIPTIONS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_group_descriptions.json"
FRONTEND_ROOTS = [PROJECT_ROOT / "test_site", PROJECT_ROOT / "widget", PROJECT_ROOT / "frontend"]
MOJIBAKE_MARKERS = ["\u00e1\u0192", "\u00e2", "\u00c3", "\ufffd"]


def start_session(client, language: str = "en") -> dict:
    response = client.post("/chat/session/start", json={"source_domain": "join.alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def send_message(client, session: dict, message: str, language: str = "en") -> dict:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "join.alte.edu.ge",
            "language": language,
            "widget_variant": "pro_v2_safe",
        },
    )
    assert response.status_code == 200
    return response.json()


def seed_source(client, *, source_key: str, title: str, source_domain: str | None, category: str, content: str, keywords: str) -> None:
    source_response = client.post(
        "/knowledge/sources",
        json={
            "source_key": source_key,
            "title": title,
            "source_type": "policy",
            "status": "approved",
            "language": "en",
            "source_domain": source_domain,
            "category": category,
            "sensitivity": "approved public source",
        },
    )
    assert source_response.status_code == 200
    source = source_response.json()
    snippet_response = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": source_key,
            "title": title,
            "content": content,
            "category": category,
            "source_domain": source_domain,
            "sensitivity": "approved public source",
            "keywords": keywords,
            "status": "approved",
            "language": "en",
        },
    )
    assert snippet_response.status_code == 200


def patch_route(monkeypatch, route: ClaudeIntentRoute) -> None:
    monkeypatch.setattr(
        chat_service,
        "route_with_claude_intent",
        lambda *args, **kwargs: (
            route,
            {
                "provider": "claude",
                "model": "test-router",
                "fallback": route.fallback_used,
                "raw_response": route.model_dump(),
                "router_validation_status": route.router_validation_status,
            },
        ),
    )


def fake_retrieval_item(*, source_key: str, title: str, category: str, source_domain: str | None = None):
    source = SimpleNamespace(
        source_key=source_key,
        title=title,
        category=category,
        source_domain=source_domain,
        source_path=None,
        document_id=None,
    )
    snippet = SimpleNamespace(
        id=f"snippet-{source_key}",
        source_key=source_key,
        title=title,
        category=category,
        source_domain=source_domain,
        keywords="",
        source_path=None,
        document_id=None,
    )
    return SimpleNamespace(source=source, snippet=snippet, score=1.0)


def assert_route_group(message: str, expected_group: str) -> None:
    route = fallback_intent_route(message, source_domain="join.alte.edu.ge")
    assert expected_group in route.source_groups_to_search
    decision = route_decision_from_intent(route, classify_knowledge_route(message, source_domain="join.alte.edu.ge"))
    assert decision.primary_source_group == expected_group


def test_source_group_descriptions_are_valid_and_allowed():
    raw = json.loads(SOURCE_DESCRIPTIONS.read_text(encoding="utf-8"))
    assert len(raw["source_groups"]) >= 10
    descriptions = load_source_group_descriptions()
    required = {
        "official_academic_rules",
        "academic_calendar_2025_2026",
        "admissions_rules",
        "student_status_and_mobility",
        "exams_and_assessment",
        "finance_sources",
        "library_sources",
        "it_support_sources",
        "international_admissions_sources",
        "career_sources",
    }
    assert required.issubset(descriptions)
    assert required.issubset(allowed_source_group_ids())
    for group_id in required:
        item = descriptions[group_id]
        assert item["description_ka"]
        assert item["description_en"]
        assert item["good_for"]
        assert "fallback_department" in item


def test_broad_study_question_asks_clarification_without_retrieval():
    route = fallback_intent_route("სწავლა მაინტერესებს")
    assert route.needs_clarification is True
    assert route.source_groups_to_search == []
    assert route.operator_needed is False


def test_programs_broad_question_has_expected_options():
    route = fallback_intent_route("პროგრამები მაინტერესებს")
    assert route.needs_clarification is True
    assert "ბაკალავრიატი" in route.clarification_options
    assert "მაგისტრატურა" in route.clarification_options
    assert "მედიცინა / MD" in route.clarification_options


def test_payment_broad_question_routes_or_clarifies_finance():
    route = fallback_intent_route("გადახდებზე მაინტერესებს")
    assert route.department == "finance"
    assert route.needs_clarification is True
    assert route.operator_needed is False


def test_bachelor_ects_selects_official_academic_rules():
    assert_route_group("How many ECTS credits are required to complete a bachelor program?", "official_academic_rules")


def test_master_ects_selects_official_academic_rules():
    assert_route_group("How many credits are required for a master's program at Alte University?", "official_academic_rules")


def test_computer_science_spring_registration_selects_calendar():
    assert_route_group("When does Computer Science spring semester registration start?", "academic_calendar_2025_2026")


def test_admission_documents_selects_admissions_rules():
    assert_route_group("Which documents are needed for bachelor admission?", "admissions_rules")


def test_status_suspension_selects_student_status_or_rules():
    route = fallback_intent_route("How many years can student status be suspended?")
    assert {"student_status_and_mobility", "official_academic_rules"}.intersection(route.source_groups_to_search)


def test_fx_exam_question_selects_exams_and_assessment():
    assert_route_group("What does FX mean and when can a student retake an exam?", "exams_and_assessment")


def test_library_resources_selects_library_sources():
    assert_route_group("How can I use library resources and databases?", "library_sources")


def test_it_emis_login_selects_it_sources():
    assert_route_group("I cannot log in to EMIS, who can help?", "it_support_sources")


def test_international_medicine_selects_international_sources():
    route = fallback_intent_route("I am an international student and want to apply to Medicine")
    assert "international_admissions_sources" in route.source_groups_to_search


def test_unsupported_fake_scholarship_is_not_retrieved_broadly():
    route = fallback_intent_route("How do I get the 2031 space campus scholarship?")
    assert route.unsupported_likely is True
    assert route.source_groups_to_search == []


def test_explicit_operator_request_sets_operator_needed():
    route = fallback_intent_route("I want to talk to a human operator")
    assert route.operator_needed is True
    assert route.source_groups_to_search == []


def test_fallback_finance_operator_request_beats_forced_finance_group():
    route = fallback_intent_route("I want finance operator")
    assert route.operator_needed is True
    assert route.source_groups_to_search == []
    assert route.department == "finance"


def test_fallback_contact_finance_department_beats_forced_finance_group():
    route = fallback_intent_route("I want to contact finance department")
    assert route.operator_needed is True
    assert route.source_groups_to_search == []
    assert route.department == "finance"


def test_fallback_georgian_finance_operator_request_beats_forced_finance_group():
    route = fallback_intent_route("მინდა ფინანსურ დეპარტამენტთან დაკავშირება")
    assert route.operator_needed is True
    assert route.source_groups_to_search == []
    assert route.department == "finance"


def test_fallback_georgian_generic_operator_request_routes_human_operator():
    route = fallback_intent_route("ცოცხალი ოპერატორი მინდა")
    assert route.operator_needed is True
    assert route.source_groups_to_search == []
    assert route.department == "human_operator"


def test_non_operator_finance_question_still_routes_normally():
    route = fallback_intent_route("გადახდის გრაფიკი მაინტერესებს")
    assert route.operator_needed is False
    assert route.department == "finance" or "finance_sources" in route.source_groups_to_search


def test_only_one_operator_detector_definition_remains():
    source = inspect.getsource(claude_intent_router_service)
    assert source.count("def has_operator_request(") == 1


def test_validator_rejects_unknown_source_groups_and_limits_count():
    payload = {
        "intent": "information_request",
        "language": "en",
        "department": "Programs",
        "public_department_label": "Programs",
        "topic": "credits",
        "needs_clarification": False,
        "clarification_question": None,
        "clarification_options": [],
        "source_groups_to_search": [
            "official_academic_rules",
            "unknown_group",
            "academic_calendar_2025_2026",
            "admissions_rules",
            "finance_sources",
        ],
        "search_terms": ["ECTS"],
        "operator_needed": False,
        "operator_reason": None,
        "unsupported_likely": False,
        "confidence": 0.94,
    }
    route = validate_router_payload(payload, message="How many credits?")
    assert route.source_groups_to_search == [
        "official_academic_rules",
        "academic_calendar_2025_2026",
        "admissions_rules",
    ]


def test_operator_override_beats_claude_source_backed_route():
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "credits",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="I want an operator",
    )
    assert route.operator_needed is True
    assert route.source_groups_to_search == []
    assert route.deterministic_override_applied is True
    assert route.deterministic_override_reason == "explicit_operator_request"


def test_georgian_operator_override_beats_claude_source_backed_route():
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "ka",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "credits",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="მინდა ოპერატორთან დაკავშირება",
    )
    assert route.operator_needed is True
    assert route.source_groups_to_search == []
    assert route.deterministic_override_reason == "explicit_operator_request"


def test_validated_claude_override_infers_finance_department():
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "ka",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "finance",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["finance_sources"],
            "search_terms": ["finance"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="მინდა ფინანსურ დეპარტამენტთან დაკავშირება",
    )
    assert route.operator_needed is True
    assert route.department == "finance"
    assert route.source_groups_to_search == []
    assert route.deterministic_override_reason == "explicit_operator_request"


def test_validated_claude_override_infers_library_it_and_generic_operator_departments():
    cases = [
        ("ბიბლიოთეკის ოპერატორი მინდა", "library"),
        ("emis-ზე ვერ შევდივარ, ოპერატორი მინდა", "it_support"),
        ("ცოცხალი ოპერატორი მინდა", "human_operator"),
        ("I want to contact finance department", "finance"),
    ]
    for message, expected_department in cases:
        route = validate_router_payload(
            {
                "intent": "information_request",
                "language": "ka" if any("\u10a0" <= char <= "\u10ff" for char in message) else "en",
                "department": "Programs",
                "public_department_label": "Programs",
                "topic": "operator",
                "needs_clarification": False,
                "clarification_question": None,
                "clarification_options": [],
                "source_groups_to_search": ["official_academic_rules"],
                "search_terms": ["operator"],
                "operator_needed": False,
                "operator_reason": None,
                "unsupported_likely": False,
                "confidence": 0.9,
            },
            message=message,
        )
        assert route.operator_needed is True
        assert route.department == expected_department
        assert route.source_groups_to_search == []


def test_broad_question_override_beats_claude_source_backed_route():
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "ka",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "credits",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="სწავლა მაინტერესებს",
    )
    assert route.needs_clarification is True
    assert route.operator_needed is False
    assert route.source_groups_to_search == []
    assert route.deterministic_override_reason == "known_broad_question"


def test_finance_broad_question_override_clarifies():
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "ka",
            "department": "Finance",
            "public_department_label": "Finance",
            "topic": "payment",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["finance_sources"],
            "search_terms": ["payment"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="გადახდებზე მაინტერესებს",
    )
    assert route.needs_clarification is True
    assert route.department == "finance"
    assert route.source_groups_to_search == []


def test_clean_georgian_clarification_outputs_for_admissions_and_help():
    for message in ["მიღება მაინტერესებს", "დახმარება მინდა"]:
        route = fallback_intent_route(message)
        text = " ".join([route.clarification_question or "", *route.clarification_options])
        assert route.needs_clarification is True
        assert any("\u10a0" <= char <= "\u10ff" for char in text)
        assert not any(marker in text for marker in MOJIBAKE_MARKERS)


def test_source_group_descriptions_have_clean_georgian():
    raw = SOURCE_DESCRIPTIONS.read_text(encoding="utf-8")
    assert not any(marker in raw for marker in MOJIBAKE_MARKERS)
    data = json.loads(raw)
    for item in data["source_groups"]:
        description = item["description_ka"]
        assert any("\u10a0" <= char <= "\u10ff" for char in description)


def test_informational_router_does_not_create_crm_entities():
    route = fallback_intent_route("How many ECTS credits are required to complete a bachelor program?")
    assert route.operator_needed is False
    assert route.unsupported_likely is False


def test_selected_admissions_group_does_not_return_calendar_or_finance_chunks(client, monkeypatch):
    seed_source(
        client,
        source_key="bachelor admission chunks",
        title="Bachelor admission documents",
        source_domain=None,
        category="admissions",
        content="Bachelor admission requires approved enrollment documents.",
        keywords="admission documents enrollment bachelor",
    )
    seed_source(
        client,
        source_key="phase_9av_calendar",
        title="Academic calendar admissions deadline noise",
        source_domain="official_academic_rules",
        category="academic_calendar",
        content="Calendar registration and admission timeline words but no documents.",
        keywords="admission documents calendar registration",
    )
    patch_route(
        monkeypatch,
        ClaudeIntentRoute(
            intent="information_request",
            language="en",
            department="admissions",
            public_department_label="Admissions",
            topic="admission_documents",
            source_groups_to_search=["admissions_rules"],
            confidence=0.95,
            fallback_used=False,
            router_validation_status="valid",
        ),
    )
    monkeypatch.setattr(chat_service, "analyze_with_ai", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("legacy AI should be skipped")))
    session = start_session(client)

    result = send_message(client, session, "Which documents are needed for bachelor admission?")

    assert result["answer_source_status"] == "answered_from_approved_source"
    assert result["public_source_label"]
    assert result["used_sources"] == [result["public_source_label"]]
    assert "bachelor admission chunks" not in result["used_sources"]
    assert "phase_9av_calendar" not in result["used_sources"]


def test_source_domain_null_finance_group_filters_out_international_admissions(client, monkeypatch):
    seed_source(
        client,
        source_key="financial_support_mechanisms",
        title="Financial support mechanisms",
        source_domain=None,
        category="finance",
        content="Financial support and grant rules are covered in this approved finance source.",
        keywords="financial support grant scholarship finance",
    )
    seed_source(
        client,
        source_key="phase_9av_international_admissions",
        title="International admission grant wording noise",
        source_domain="alte.edu.ge",
        category="admissions",
        content="International admission content mentions grant as a generic word.",
        keywords="international admission grant",
    )
    patch_route(
        monkeypatch,
        ClaudeIntentRoute(
            intent="information_request",
            language="en",
            department="finance",
            public_department_label="Finance",
            topic="financial_support",
            source_groups_to_search=["finance_sources"],
            confidence=0.95,
            fallback_used=False,
            router_validation_status="valid",
        ),
    )
    session = start_session(client)

    result = send_message(client, session, "What financial support grants are available?")

    assert result["answer_source_status"] == "answered_from_approved_source"
    assert result["public_source_label"]
    assert result["used_sources"] == [result["public_source_label"]]
    assert "financial_support_mechanisms" not in result["used_sources"]
    assert "phase_9av_international_admissions" not in result["used_sources"]


def test_calendar_group_does_not_return_admissions_chunks(client, monkeypatch):
    seed_source(
        client,
        source_key="academic_calendar_geo_2025_2026",
        title="Academic calendar 2025-2026",
        source_domain="official_academic_rules",
        category="academic_calendar",
        content="Computer Science spring semester registration is 9-14 March and semester starts 30 March.",
        keywords="computer science spring semester registration 9-14 march 30 march calendar",
    )
    seed_source(
        client,
        source_key="phase_9av_admissions_noise",
        title="Admissions registration wording noise",
        source_domain=None,
        category="admissions",
        content="Admissions registration documents are required for enrollment.",
        keywords="registration computer science admissions",
    )
    patch_route(
        monkeypatch,
        ClaudeIntentRoute(
            intent="information_request",
            language="en",
            department="academic_calendar",
            public_department_label="Study Process",
            topic="calendar",
            source_groups_to_search=["academic_calendar_2025_2026"],
            confidence=0.95,
            fallback_used=False,
            router_validation_status="valid",
        ),
    )
    session = start_session(client)

    result = send_message(client, session, "When is Computer Science spring semester registration?")

    assert result["answer_source_status"] == "answered_from_approved_source"
    assert result["public_source_label"]
    assert result["used_sources"] == [result["public_source_label"]]
    assert "academic_calendar_geo_2025_2026" not in result["used_sources"]
    assert "phase_9av_admissions_noise" not in result["used_sources"]


def test_invalid_claude_source_group_does_not_retrieve_broadly(client, monkeypatch):
    seed_source(
        client,
        source_key="phase_9av_broad_admissions_noise",
        title="Broad admissions noise",
        source_domain=None,
        category="admissions",
        content="Admission content should not be used for invalid router source group output.",
        keywords="admission documents enrollment",
    )
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Admissions",
            "public_department_label": "Admissions",
            "topic": "documents",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["fake_group"],
            "search_terms": ["admission documents"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="Which admission documents are needed?",
    )
    patch_route(monkeypatch, route)
    monkeypatch.setattr(chat_service, "analyze_with_ai", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("legacy AI should be skipped")))
    session = start_session(client)

    result = send_message(client, session, "Which admission documents are needed?")

    assert result["answer_source_status"] == "no_approved_source_found"
    assert result["used_sources"] == []


def test_empty_validated_claude_source_groups_do_not_retrieve_broadly(client, monkeypatch):
    seed_source(
        client,
        source_key="phase_9av_library_noise",
        title="Library broad noise",
        source_domain="alte.edu.ge",
        category="library",
        content="Library source should not be used when Claude returns empty source groups.",
        keywords="library resources",
    )
    route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Library",
            "public_department_label": "Library",
            "topic": "library",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": [],
            "search_terms": ["library resources"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="How do I use library resources?",
    )
    patch_route(monkeypatch, route)
    session = start_session(client)

    result = send_message(client, session, "How do I use library resources?")

    assert result["answer_source_status"] == "no_approved_source_found"
    assert result["used_sources"] == []


def test_same_category_unlisted_source_is_rejected_for_admissions_group():
    item = fake_retrieval_item(
        source_key="unlisted_admissions_policy",
        title="Unlisted admissions policy",
        category="admissions",
        source_domain=None,
    )
    config = {
        "source_files": ["bachelor admission chunks", "master admission chunks"],
        "source_domain": None,
    }
    assert chat_service.retrieval_result_belongs_to_source_group(item, "admissions_rules", config) is False


def test_source_domain_null_group_filters_by_source_identity():
    item = fake_retrieval_item(
        source_key="unlisted_finance_policy",
        title="Unlisted finance policy",
        category="finance",
        source_domain=None,
    )
    config = {
        "source_files": ["financial_support_mechanisms", "state_social_grants"],
        "source_domain": None,
    }
    assert chat_service.retrieval_result_belongs_to_source_group(item, "finance_sources", config) is False

    allowed = fake_retrieval_item(
        source_key="financial_support_mechanisms",
        title="Financial support mechanisms",
        category="finance",
        source_domain=None,
    )
    assert chat_service.retrieval_result_belongs_to_source_group(allowed, "finance_sources", config) is True


def test_category_fallback_requires_explicit_allow_flag():
    item = fake_retrieval_item(
        source_key="category_only_policy",
        title="Category only policy",
        category="library",
        source_domain="alte.edu.ge",
    )
    assert chat_service.retrieval_result_belongs_to_source_group(
        item,
        "library_sources",
        {"source_files": ["library_rules"], "allowed_categories": ["library"]},
    ) is False
    assert chat_service.retrieval_result_belongs_to_source_group(
        item,
        "library_sources",
        {"source_files": ["library_rules"], "allow_category_fallback": True, "allowed_categories": ["library"]},
    ) is True


def test_invalid_json_fallback_can_use_deterministic_safe_route():
    route = fallback_intent_route("How many ECTS credits are required to complete a bachelor program?")
    assert route.fallback_used is True
    assert route.router_validation_status == "fallback_used"
    assert "official_academic_rules" in route.source_groups_to_search


def test_clarification_path_bypasses_legacy_ai(client, monkeypatch):
    patch_route(
        monkeypatch,
        ClaudeIntentRoute(
            intent="clarification",
            language="en",
            department="admissions",
            public_department_label="Admissions",
            topic="broad",
            needs_clarification=True,
            clarification_question="Please clarify which topic you mean.",
            clarification_options=["Admissions", "Programs"],
            confidence=0.95,
            fallback_used=False,
            router_validation_status="valid",
        ),
    )
    monkeypatch.setattr(chat_service, "analyze_with_ai", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("legacy AI should be skipped")))
    session = start_session(client)

    result = send_message(client, session, "I need information")

    assert result["clarification_needed"] is True
    assert result["should_handover"] is False


def test_unsupported_fake_question_does_not_retrieve_unrelated_chunks(client, monkeypatch):
    seed_source(
        client,
        source_key="phase_9av_finance_noise",
        title="Finance scholarship noise",
        source_domain=None,
        category="finance",
        content="Approved finance source about real scholarships.",
        keywords="scholarship finance",
    )
    route = fallback_intent_route("How do I get the 2031 space campus scholarship?")
    patch_route(monkeypatch, route)
    session = start_session(client)

    result = send_message(client, session, "How do I get the 2031 space campus scholarship?")

    assert result["answer_source_status"] == "no_approved_source_found"
    assert result["used_sources"] == []


def test_frontend_does_not_call_anthropic_or_expose_api_key():
    forbidden = ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk-" + "ant-"]
    for root in FRONTEND_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".html"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in forbidden:
                assert marker not in text, f"{marker} found in {path}"


def test_public_launch_remains_no_go():
    text = PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")
    assert "NO-GO" in text
    assert "PUBLIC_LAUNCH_GO" not in text


