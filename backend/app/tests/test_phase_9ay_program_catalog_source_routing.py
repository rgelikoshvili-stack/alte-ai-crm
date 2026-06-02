from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from app.services.chat_service import grounded_source_backed_reply, retrieval_result_belongs_to_source_group
from app.services.claude_intent_router_service import fallback_intent_route, forced_source_group, validate_router_payload
from app.services.knowledge_routing_service import source_group_config


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"


CATALOG_QUESTIONS = [
    "რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?",
    "როგორ ნაწილდება ეს პროგრამები საფეხურების მიხედვით?",
    "ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები.",
    "ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები.",
    "რომელი ერთსაფეხურიანი პროგრამები აქვს ალტე უნივერსიტეტს?",
    "რა ინფორმაციას შეიცავს პროგრამების კატალოგი თითოეულ პროგრამაზე?",
    "რა კვალიფიკაციას ანიჭებს სამართლის საბაკალავრო პროგრამა?",
    "რა კვალიფიკაციას ანიჭებს სამართლის სამაგისტრო პროგრამა?",
    "რა ენებზე გვხვდება კომპიუტერული მეცნიერების პროგრამა კატალოგში?",
    "თუ ვკითხავ პროგრამის სწავლის ზუსტ საფასურს, პროგრამების კატალოგიდან უნდა მიპასუხო თუ უნდა თქვა რომ წყაროში არ ჩანს?",
]


def router_payload(groups: list[str]) -> dict:
    return {
        "intent": "information_request",
        "language": "ka",
        "department": "Programs",
        "public_department_label": "Programs",
        "topic": "program_catalog",
        "needs_clarification": False,
        "clarification_question": None,
        "clarification_options": [],
        "source_groups_to_search": groups,
        "search_terms": ["program catalog"],
        "operator_needed": False,
        "operator_reason": None,
        "unsupported_likely": False,
        "confidence": 0.95,
    }


def fake_retrieval_item(*, source_key: str, title: str, category: str = "programs", source_domain: str = "official_alte_pdf_kb"):
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
        source_path=None,
        document_id=None,
    )
    return SimpleNamespace(source=source, snippet=snippet, score=1.0)


def test_program_catalog_source_group_exists_and_references_catalog():
    groups = {item["id"]: item for item in json.loads(SOURCE_GROUPS.read_text(encoding="utf-8"))["source_groups"]}
    group = groups["program_catalog_sources"]
    identity = " ".join(group.get("source_files", []) + group.get("source_keys", []))
    assert "01_program_catalog.pdf" in identity
    assert "Higher Education Program Catalog" in identity
    assert "official_alte_8_pdf_kb_01_01_program_catalog" in identity
    assert group["source_domain"] == "official_alte_pdf_kb"
    assert group["exact_answer_allowed"] is True


def test_catalog_questions_force_program_catalog_not_academic_rules():
    for question in CATALOG_QUESTIONS:
        assert forced_source_group(question.lower()) == "program_catalog_sources"
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        assert route.source_groups_to_search[0] == "program_catalog_sources"
        assert route.source_groups_to_search[:1] != ["official_academic_rules"]
        assert route.operator_needed is False


def test_library_catalog_questions_do_not_route_to_program_catalog():
    for question in [
        "ბიბლიოთეკის კატალოგი როგორ გამოვიყენო?",
        "How do I use the library catalog?",
    ]:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        assert route.source_groups_to_search[0] == "library_sources"
        assert route.department == "library"
        assert route.source_groups_to_search[:1] != ["program_catalog_sources"]
        assert forced_source_group(question.lower()) == "library_sources"


def test_program_catalog_explicit_catalog_markers_still_route_to_catalog():
    for question in [
        "პროგრამების კატალოგი რას შეიცავს?",
        "რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?",
        "ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები.",
    ]:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        assert route.source_groups_to_search[0] == "program_catalog_sources"
        assert route.department == "programs"


def test_non_program_list_prompts_do_not_route_to_program_catalog():
    cases = [
        ("ჩამომითვალე მიღებისთვის საჭირო საბუთები", "admissions_rules"),
        ("ჩამომითვალე გრანტები", "finance_sources"),
        ("ჩამომითვალე ბიბლიოთეკის რესურსები", "library_sources"),
        ("ჩამომითვალე IT დახმარების გზები", "it_support_sources"),
    ]
    for question, expected_group in cases:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        assert route.source_groups_to_search[:1] != ["program_catalog_sources"]
        assert forced_source_group(question.lower()) != "program_catalog_sources"
        assert route.source_groups_to_search[0] == expected_group


def test_program_list_prompts_still_route_to_program_catalog():
    for question in [
        "ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები",
        "ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები",
        "ჩამომითვალე ერთსაფეხურიანი პროგრამები",
    ]:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        assert forced_source_group(question.lower()) == "program_catalog_sources"
        assert route.source_groups_to_search[0] == "program_catalog_sources"
        assert route.department == "programs"


def test_validated_claude_academic_rules_route_is_specialized_to_catalog():
    for question in CATALOG_QUESTIONS:
        route = validate_router_payload(router_payload(["official_academic_rules"]), message=question)
        assert route.source_groups_to_search == ["program_catalog_sources"]
        assert route.department == "programs"
        assert route.operator_needed is False


def test_program_catalog_strict_source_membership_accepts_catalog_only():
    config = source_group_config("program_catalog_sources")
    assert config is not None
    catalog_item = fake_retrieval_item(
        source_key="official_alte_8_pdf_kb_01_01_program_catalog_p001_c001",
        title="Higher Education Program Catalog p.1 c.1",
    )
    academic_rules_item = fake_retrieval_item(
        source_key="official_academic_rules_full_01_p005_c009",
        title="Official Academic Rules",
        source_domain="official_academic_rules",
    )
    other_pdf_item = fake_retrieval_item(
        source_key="official_alte_8_pdf_kb_02_02_academic_calendar_2025_2026_p001_c001",
        title="Academic Calendar",
    )
    assert retrieval_result_belongs_to_source_group(catalog_item, "program_catalog_sources", config)
    assert not retrieval_result_belongs_to_source_group(academic_rules_item, "program_catalog_sources", config)
    assert not retrieval_result_belongs_to_source_group(other_pdf_item, "program_catalog_sources", config)


def test_mandatory_existing_routes_are_preserved():
    assert forced_source_group("How many ECTS credits are required for bachelor completion?") == "official_academic_rules"
    assert forced_source_group("How many credits are required for a master program?") == "official_academic_rules"
    assert forced_source_group("How many ECTS credits are required for Dentistry if the approved academic rules include it?") == "official_academic_rules"
    assert forced_source_group("ეროვნული გამოცდების გარეშე როგორ ჩავირიცხო?") == "admissions_rules"
    assert forced_source_group("What are the requirements for English-language programs?") == "international_admissions_sources"
    assert fallback_intent_route("დასკვნით გამოცდაზე დაშვების წესი როგორია?").source_groups_to_search[0] == "exams_and_assessment"
    assert fallback_intent_route("დასკვნითი გამოცდები როდის არის?").source_groups_to_search[0] == "academic_calendar_2025_2026"
    assert fallback_intent_route("ერთსაფეხურიანი პროგრამების დასკვნითი გამოცდები როდის არის?").source_groups_to_search[0] == "academic_calendar_2025_2026"


def test_no_handover_for_catalog_informational_routes_and_public_launch_no_go():
    route = fallback_intent_route("რა კვალიფიკაციას ანიჭებს სამართლის საბაკალავრო პროგრამა?")
    assert route.operator_needed is False
    assert route.source_groups_to_search == ["program_catalog_sources"]
    assert "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")


def test_program_catalog_grounded_replies_cover_production_qa_terms():
    cases = [
        ("რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?", ("16",)),
        ("როგორ ნაწილდება ეს პროგრამები საფეხურების მიხედვით?", ("10", "3", "ბაკალავრ", "მაგისტრ", "ერთსაფეხურ")),
        (
            "ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები.",
            ("სამართ", "კომპიუტერულ", "ბიზნეს", "ბაკალავრ"),
        ),
        ("ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები.", ("სამართ", "ბიზნეს", "მაგისტრ")),
        ("რომელი ერთსაფეხურიანი პროგრამები აქვს ალტე უნივერსიტეტს?", ("მედიც", "სტომატოლოგ", "ერთსაფეხურ")),
        (
            "რა ინფორმაციას შეიცავს პროგრამების კატალოგი თითოეულ პროგრამაზე?",
            ("სახელ", "საფეხურ", "კვალიფიკ", "ენა", "კრედიტ", "ხანგრძლივ", "წინაპირობ", "შედეგ"),
        ),
        ("რა კვალიფიკაციას ანიჭებს სამართლის საბაკალავრო პროგრამა?", ("სამართლის ბაკალავრ",)),
        ("რა კვალიფიკაციას ანიჭებს სამართლის სამაგისტრო პროგრამა?", ("სამართლის მაგისტრ",)),
        ("რა ენებზე გვხვდება კომპიუტერული მეცნიერების პროგრამა კატალოგში?", ("ქართულ", "ინგლის")),
        (
            "თუ ვკითხავ პროგრამის სწავლის ზუსტ საფასურს, პროგრამების კატალოგიდან უნდა მიპასუხო თუ უნდა თქვა რომ წყაროში არ ჩანს?",
            ("არ", "წყარო", "ოპერატორ"),
        ),
    ]
    route_decision = SimpleNamespace(primary_source_group="program_catalog_sources")
    for question, expected_terms in cases:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        reply = grounded_source_backed_reply(question, "ka", route_decision) or ""
        lowered = reply.lower()
        assert route.source_groups_to_search[0] == "program_catalog_sources"
        assert all(term.lower() in lowered for term in expected_terms)
        assert "₾" not in reply
        assert "gel" not in lowered
