from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.services.chat_service import (
    grounded_source_backed_reply,
    is_clearly_unsupported_official_question,
)
from app.services.claude_intent_router_service import (
    fallback_intent_route,
    forced_source_group,
    has_unsupported_marker,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


CATALOG_ROUTE = SimpleNamespace(primary_source_group="program_catalog_sources")
FORBIDDEN_PUBLIC_MARKERS = [
    "official_academic_rules",
    "source_group",
    "Policy:",
    "Reference:",
    "Official source:",
    "answer only from",
    "chunk",
    "p022_c050",
]


def assert_clean_reply(reply: str) -> None:
    lowered = reply.lower()
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        assert marker.lower() not in lowered


def test_catalog_scoped_bachelor_credits_use_catalog_not_academic_rules():
    question = "პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია საბაკალავრო პროგრამა?"

    route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
    reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""

    assert forced_source_group(question.lower()) == "program_catalog_sources"
    assert route.source_groups_to_search[0] == "program_catalog_sources"
    assert route.source_groups_to_search[:1] != ["official_academic_rules"]
    assert "240 ECTS" in reply
    assert "180" not in reply
    assert_clean_reply(reply)


def test_catalog_scoped_master_credits_use_catalog_not_academic_rules():
    question = "პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია სამაგისტრო პროგრამა?"

    route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
    reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""

    assert forced_source_group(question.lower()) == "program_catalog_sources"
    assert route.source_groups_to_search[0] == "program_catalog_sources"
    assert route.source_groups_to_search[:1] != ["official_academic_rules"]
    assert "120 ECTS" in reply
    assert_clean_reply(reply)


def test_catalog_law_bachelor_language_is_exact_not_generic_academic_language():
    question = "რა ენაზე ისწავლება სამართლის საბაკალავრო პროგრამა კატალოგის მიხედვით?"

    route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
    reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""

    assert route.source_groups_to_search[0] == "program_catalog_sources"
    assert "სამართლის საბაკალავრო" in reply
    assert "ქართული" in reply
    assert "ცალკეულ პროგრამებზე" not in reply
    assert_clean_reply(reply)


def test_catalog_english_language_programs_are_listed_specifically():
    question = "რომელი პროგრამებია ინგლისურენოვანი პროგრამების კატალოგში?"

    route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
    reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""

    assert route.source_groups_to_search[0] == "program_catalog_sources"
    for expected in [
        "მედიცინა (ინგლისურენოვანი)",
        "კომპიუტერული მეცნიერება (ინგლისურენოვანი)",
        "ხელოვნური ინტელექტი და მონაცემთა ანალიტიკა (ინგლისურენოვანი)",
    ]:
        assert expected in reply
    assert_clean_reply(reply)


def test_catalog_ai_data_analytics_language_versions_are_specific():
    question = "რა ენებზე არის ხელოვნური ინტელექტისა და მონაცემთა ანალიტიკის პროგრამა კატალოგში?"

    route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
    reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""

    assert route.source_groups_to_search[0] == "program_catalog_sources"
    assert "ქართულ" in reply
    assert "ინგლისურენოვან" in reply
    assert_clean_reply(reply)


def test_broad_credit_question_requires_clarification_not_retrieval():
    route = fallback_intent_route("კრედიტები მაინტერესებს.", source_domain="join.alte.edu.ge")

    assert route.needs_clarification is True
    assert route.source_groups_to_search == []
    assert route.operator_needed is False
    assert "დააზუსტ" in (route.clarification_question or "")


def test_broad_program_question_with_punctuation_requires_clarification():
    route = fallback_intent_route("პროგრამები მაინტერესებს.", source_domain="join.alte.edu.ge")

    assert route.needs_clarification is True
    assert route.source_groups_to_search == []
    assert route.operator_needed is False
    assert "პროგრამ" in (route.clarification_question or "")


def test_broad_catalog_program_detail_requires_clarification():
    route = fallback_intent_route("კატალოგში პროგრამაზე ინფორმაცია მაინტერესებს.", source_domain="join.alte.edu.ge")

    assert route.needs_clarification is True
    assert route.source_groups_to_search == []
    assert route.operator_needed is False
    assert "რომელი პროგრამა" in (route.clarification_question or "")


def test_program_consultant_phone_is_unsupported_without_phone_hallucination():
    question = "პროგრამების კონსულტანტის ტელეფონის ნომერი მითხარი."
    route = fallback_intent_route(question, source_domain="join.alte.edu.ge")

    assert has_unsupported_marker(question.lower())
    assert is_clearly_unsupported_official_question(question)
    assert route.unsupported_likely is True
    assert route.source_groups_to_search == []
    assert route.department == "programs"


def test_phase_9ba_key_controls_remain_intact():
    controls = {
        "რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?": "16",
        "როგორ ნაწილდება ეს პროგრამები საფეხურების მიხედვით?": "10",
        "ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები.": "ხელოვნური ინტელექტი",
        "ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები.": "ეროვნული და საერთაშორისო უსაფრთხოება",
        "რომელი ერთსაფეხურიანი პროგრამები აქვს ალტე უნივერსიტეტს?": "სტომატოლოგია",
    }
    for question, expected in controls.items():
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""
        assert route.source_groups_to_search[0] == "program_catalog_sources"
        assert expected in reply
        assert_clean_reply(reply)


def test_unsupported_space_campus_remains_no_source_and_public_launch_no_go():
    route = fallback_intent_route("2031 წლის კოსმოსური კამპუსის პროგრამაზე რა მოთხოვნებია?")

    assert route.unsupported_likely is True
    assert route.source_groups_to_search == []
    assert "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")
