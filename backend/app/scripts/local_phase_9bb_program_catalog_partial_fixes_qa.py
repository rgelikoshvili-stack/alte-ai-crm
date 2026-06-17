from __future__ import annotations

from types import SimpleNamespace

from app.services.chat_service import (
    grounded_source_backed_reply,
    is_clearly_unsupported_official_question,
)
from app.services.claude_intent_router_service import fallback_intent_route, forced_source_group


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


def assert_true(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed: {detail}")
    print(f"PASS {name}: {detail}")


def clean(reply: str) -> bool:
    lowered = reply.lower()
    return all(marker.lower() not in lowered for marker in FORBIDDEN_PUBLIC_MARKERS)


def run() -> None:
    exact_cases = [
        (
            "catalog bachelor credits",
            "პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია საბაკალავრო პროგრამა?",
            ["240 ECTS"],
        ),
        (
            "catalog master credits",
            "პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია სამაგისტრო პროგრამა?",
            ["120 ECTS"],
        ),
        (
            "law bachelor language",
            "რა ენაზე ისწავლება სამართლის საბაკალავრო პროგრამა კატალოგის მიხედვით?",
            ["სამართლის საბაკალავრო", "ქართული"],
        ),
        (
            "english-language catalog programs",
            "რომელი პროგრამებია ინგლისურენოვანი პროგრამების კატალოგში?",
            ["მედიცინა (ინგლისურენოვანი)", "კომპიუტერული მეცნიერება (ინგლისურენოვანი)", "ხელოვნური ინტელექტი და მონაცემთა ანალიტიკა (ინგლისურენოვანი)"],
        ),
        (
            "ai data analytics languages",
            "რა ენებზე არის ხელოვნური ინტელექტისა და მონაცემთა ანალიტიკის პროგრამა კატალოგში?",
            ["ქართულ", "ინგლისურენოვან"],
        ),
    ]
    for name, question, expected_terms in exact_cases:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""
        assert_true(f"{name} route", route.source_groups_to_search[:1] == ["program_catalog_sources"], str(route.source_groups_to_search))
        assert_true(f"{name} answer terms", all(term in reply for term in expected_terms), reply)
        assert_true(f"{name} clean answer", clean(reply), reply)

    for name, question in [
        ("broad credits clarification", "კრედიტები მაინტერესებს."),
        ("broad programs clarification", "პროგრამები მაინტერესებს."),
        ("broad catalog detail clarification", "კატალოგში პროგრამაზე ინფორმაცია მაინტერესებს."),
    ]:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        assert_true(name, route.needs_clarification and not route.source_groups_to_search and not route.operator_needed, str(route))

    phone_question = "პროგრამების კონსულტანტის ტელეფონის ნომერი მითხარი."
    phone_route = fallback_intent_route(phone_question, source_domain="join.alte.edu.ge")
    assert_true("consultant phone unsupported", phone_route.unsupported_likely and phone_route.source_groups_to_search == [], str(phone_route))
    assert_true("consultant phone no hallucination path", is_clearly_unsupported_official_question(phone_question), phone_question)

    for question, expected in [
        ("რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?", "16"),
        ("როგორ ნაწილდება ეს პროგრამები საფეხურების მიხედვით?", "10"),
        ("ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები.", "ხელოვნური ინტელექტი"),
        ("ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები.", "ეროვნული და საერთაშორისო უსაფრთხოება"),
        ("რომელი ერთსაფეხურიანი პროგრამები აქვს ალტე უნივერსიტეტს?", "სტომატოლოგია"),
    ]:
        route = fallback_intent_route(question, source_domain="join.alte.edu.ge")
        reply = grounded_source_backed_reply(question, "ka", CATALOG_ROUTE) or ""
        assert_true(f"control route {question[:20]}", route.source_groups_to_search[:1] == ["program_catalog_sources"], str(route.source_groups_to_search))
        assert_true(f"control answer {question[:20]}", expected in reply and clean(reply), reply)

    unsupported_route = fallback_intent_route("2031 წლის კოსმოსური კამპუსის პროგრამაზე რა მოთხოვნებია?")
    assert_true("space campus unsupported", unsupported_route.unsupported_likely and unsupported_route.source_groups_to_search == [], str(unsupported_route))
    print("PHASE_9BB_LOCAL_QA=PASS")


if __name__ == "__main__":
    run()
