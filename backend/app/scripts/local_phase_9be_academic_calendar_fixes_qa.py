from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from app.services.chat_service import grounded_source_backed_reply
from app.services.chat_service import is_computer_science_spring_registration_question
from app.services.chat_service import official_academic_rules_regression_reply
from app.services.claude_intent_router_service import fallback_intent_route
from app.services.knowledge_routing_service import KnowledgeRouteDecision


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9BE_ACADEMIC_CALENDAR_FIXES_RESULT.md"


@dataclass(frozen=True)
class Case:
    id: str
    question: str
    language: str
    expected_tokens: tuple[str, ...] = ()
    expected_type: str = "answer"


@dataclass(frozen=True)
class OvercaptureCase:
    id: str
    question: str
    expect_calendar: bool
    expect_helper_reply: bool | None = None


@dataclass(frozen=True)
class FallbackCase:
    id: str
    question: str
    language: str = "en"


@dataclass(frozen=True)
class StaleDateCase:
    id: str
    question: str
    language: str
    expected_tokens: tuple[str, ...]
    forbidden_tokens: tuple[str, ...] = ()


CASES = [
    Case("9bd-01", "საბაკალავრო პროგრამებისთვის შემოდგომის სემესტრი როდის იწყება?", "ka", ("29 September 2025",)),
    Case("9bd-02", "საბაკალავრო პროგრამებისთვის გაზაფხულის სემესტრის დასკვნითი გამოცდები როდის არის?", "ka", ("29 June - 11 July 2026",)),
    Case("9bd-03", "საბაკალავრო პროგრამებისთვის გაზაფხულის აკადემიური რეგისტრაცია როდის არის?", "ka", ("2 - 7 March 2026",)),
    Case("9bd-04", "Computer Science-ის გაზაფხულის სემესტრის რეგისტრაცია როდის არის?", "ka", ("9 - 14 March 2026",)),
    Case("9bd-05", "Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?", "ka", ("30 March 2026",)),
    Case("9bd-06", "Computer Science-ის გაზაფხულის დასკვნითი გამოცდები როდის არის?", "ka", ("13 - 25 July 2026",)),
    Case("9bd-07", "სამაგისტრო პროგრამებისთვის გაზაფხულის სემესტრი როდის იწყება?", "ka", ("9 March 2026",)),
    Case("9bd-08", "სამაგისტრო პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?", "ka", ("29 June - 11 July 2026",)),
    Case("9bd-09", "ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?", "ka", ("20 July - 1 August 2026",)),
    Case("9bd-10", "ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდების აღდგენა როდის არის?", "ka", ("3 - 8 August 2026",)),
    Case("9bd-11", "ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდები როდის არის?", "ka", ("25 - 30 May 2026",)),
    Case("9bd-12", "ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდების აღდგენა როდის არის?", "ka", ("13 - 18 July 2026",)),
    Case("9bd-13", "When does the fall semester start for Bachelor programs except Computer Science?", "en", ("29 September 2025",)),
    Case("9bd-14", "When are spring final exams for Bachelor programs except Computer Science?", "en", ("29 June - 11 July 2026",)),
    Case("9bd-15", "When is academic registration for Computer Science in spring?", "en", ("9 - 14 March 2026",)),
    Case("9bd-16", "When do spring final exams take place for Computer Science?", "en", ("13 - 25 July 2026",)),
    Case("9bd-17", "When does the spring semester start for Master programs?", "en", ("9 March 2026",)),
    Case("9bd-18", "When are final exams for one-cycle programs in spring?", "en", ("20 July - 1 August 2026",)),
    Case("9bd-19", "When does the fall semester start for first-year students of one-cycle English education programs?", "en", ("3 November 2025",)),
    Case("9bd-20", "When are fall midterm exams for first-year one-cycle English programs?", "en", ("5 - 10 January 2026",)),
    Case("9bd-21", "აკადემიური კალენდრის უქმე დღეები რომლებია?", "ka", ("14 October", "26 May")),
    Case("9bd-22", "ახალი წლის არდადეგები როდის არის?", "ka", ("30 December 2025 - 4 January 2026",)),
    Case("9bd-23", "აღდგომის არდადეგები როდის არის?", "ka", ("10 - 13 April 2026",)),
    Case("9bd-24", "What are the New Year holidays?", "en", ("30 December 2025 - 4 January 2026",)),
    Case("9bd-25", "What are the Easter holidays?", "en", ("10 - 13 April 2026",)),
    Case("9bd-26", "გამოცდები როდის არის?", "ka", expected_type="clarification"),
    Case("9bd-27", "რეგისტრაცია როდის არის?", "ka", expected_type="clarification"),
    Case("9bd-28", "სემესტრი როდის იწყება?", "ka", expected_type="clarification"),
    Case("9bd-29", "2031 წლის გაზაფხულის სემესტრი როდის იწყება?", "ka", expected_type="unsupported"),
    Case("9bd-30", "2027 წლის Computer Science-ის გამოცდები როდისაა?", "ka", expected_type="unsupported"),
]


OVERCAPTURE_CASES = [
    OvercaptureCase("negative-updated-registration-requirements-en", "What are updated registration requirements for bachelor admission?", False),
    OvercaptureCase("negative-candidate-registration-requirements-en", "What are candidate registration requirements for bachelor admission?", False),
    OvercaptureCase("negative-outdated-registration-requirements-en", "What are outdated registration requirements for bachelor admission?", False),
    OvercaptureCase("negative-updated-cs-spring-semester-registration-requirements-en", "What are updated Computer Science spring semester registration requirements?", False, False),
    OvercaptureCase("negative-candidate-cs-spring-semester-registration-requirements-en", "What are candidate Computer Science spring semester registration requirements?", False, False),
    OvercaptureCase("negative-outdated-cs-spring-semester-registration-requirements-en", "What are outdated Computer Science spring semester registration requirements?", False, False),
    OvercaptureCase("negative-admission-registration-requirements-en", "What are the registration requirements for bachelor admission?", False),
    OvercaptureCase("negative-registration-documents-en", "What documents are required for bachelor registration?", False),
    OvercaptureCase("negative-cs-spring-registration-requirements-en", "What are Computer Science spring registration requirements?", False),
    OvercaptureCase("negative-cs-spring-registration-documents-en", "What documents are required for Computer Science spring registration?", False),
    OvercaptureCase("negative-cs-spring-registration-requirements-ka", "Computer Science-ის გაზაფხულის რეგისტრაციის მოთხოვნები რა არის?", False),
    OvercaptureCase("negative-cs-spring-registration-documents-ka", "Computer Science-ის გაზაფხულის რეგისტრაციისთვის რა საბუთებია საჭირო?", False),
    OvercaptureCase("negative-admission-registration-requirements-ka", "ბაკალავრზე რეგისტრაციის მოთხოვნები რა არის?", False),
    OvercaptureCase("negative-registration-documents-ka", "ბაკალავრზე რეგისტრაციისთვის რა საბუთებია საჭირო?", False),
    OvercaptureCase("positive-registration-date-en", "When is bachelor registration?", True),
    OvercaptureCase("positive-registration-date-word-en", "What date does bachelor registration start?", True),
    OvercaptureCase("positive-registration-dates-word-en", "What are the registration dates for Computer Science?", True),
    OvercaptureCase("positive-cs-spring-registration-start-date-en", "What date does Computer Science spring registration start?", True, True),
    OvercaptureCase("positive-cs-spring-registration-date-en", "When is Computer Science spring registration?", True),
    OvercaptureCase("positive-cs-spring-registration-date-word-en", "What date is Computer Science spring registration?", True),
    OvercaptureCase("positive-registration-date-ka", "ბაკალავრზე რეგისტრაცია როდის არის?", True),
    OvercaptureCase("positive-cs-spring-registration-date-ka", "Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?", True),
    OvercaptureCase("positive-cs-spring-semester-start-ka", "Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?", True),
]


def calendar_decision(language: str) -> KnowledgeRouteDecision:
    return KnowledgeRouteDecision(
        department_id="academic_calendar",
        department_label="Academic Calendar",
        source_groups=["academic_calendar_2025_2026"],
        primary_source_group="academic_calendar_2025_2026",
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language=language,
        confidence=1.0,
        reason="phase_9be_local_qa",
    )


FALLBACK_OVERCAPTURE_CASES = [
    FallbackCase("fallback-cs-spring-registration-documents-en", "What documents are required for Computer Science spring registration?"),
    FallbackCase("fallback-updated-cs-spring-semester-registration-requirements-en", "What are updated Computer Science spring semester registration requirements?"),
    FallbackCase("fallback-candidate-cs-spring-semester-registration-requirements-en", "What are candidate Computer Science spring semester registration requirements?"),
    FallbackCase("fallback-admission-registration-requirements-en", "What are the registration requirements for bachelor admission?"),
    FallbackCase("fallback-bachelor-registration-documents-en", "What documents are required for bachelor registration?"),
    FallbackCase("fallback-admission-registration-requirements-ka", "ბაკალავრზე რეგისტრაციის მოთხოვნები რა არის?", "ka"),
    FallbackCase("fallback-cs-spring-registration-documents-ka", "Computer Science-ის გაზაფხულის რეგისტრაციისთვის რა საბუთებია საჭირო?", "ka"),
]


STALE_DATE_CASES = [
    StaleDateCase(
        "stale-bachelor-registration-en",
        "When is bachelor registration?",
        "en",
        ("15 - 20 September 2025", "22 - 27 September 2025", "23 - 28 February 2026", "2 - 7 March 2026"),
        ("8-13 September 2025", "8 - 13 September 2025", "academic registration - 15 - 20 September 2025"),
    ),
    StaleDateCase(
        "stale-bachelor-registration-start-en",
        "What date does bachelor registration start?",
        "en",
        ("15 - 20 September 2025", "22 - 27 September 2025", "23 - 28 February 2026", "2 - 7 March 2026"),
        ("8-13 September 2025", "8 - 13 September 2025", "academic registration - 15 - 20 September 2025"),
    ),
    StaleDateCase(
        "stale-bachelor-registration-ka",
        "ბაკალავრზე რეგისტრაცია როდის არის?",
        "ka",
        ("15 - 20 September 2025", "22 - 27 September 2025", "23 - 28 February 2026", "2 - 7 March 2026"),
        ("8-13", "8 - 13"),
    ),
    StaleDateCase(
        "cs-registration-dates-still-specific-en",
        "When is Computer Science fall academic registration?",
        "en",
        ("29 September - 4 October 2025",),
        (),
    ),
]


def admissions_decision(language: str) -> KnowledgeRouteDecision:
    return KnowledgeRouteDecision(
        department_id="admissions",
        department_label="Admissions",
        source_groups=["admissions_rules"],
        primary_source_group="admissions_rules",
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language=language,
        confidence=1.0,
        reason="phase_9be_local_qa",
    )


def answer_for(case: Case) -> str:
    return grounded_source_backed_reply(case.question, case.language, calendar_decision(case.language)) or ""


def evaluate(case: Case) -> dict[str, object]:
    route = fallback_intent_route(case.question)
    answer = "" if case.expected_type != "answer" else answer_for(case)
    checks: dict[str, bool]
    if case.expected_type == "clarification":
        checks = {
            "clarification": route.needs_clarification,
            "no_source_search": route.source_groups_to_search == [],
            "department": route.department == "academic_calendar",
        }
    elif case.expected_type == "unsupported":
        checks = {
            "unsupported": route.unsupported_likely,
            "no_source_search": route.source_groups_to_search == [],
            "department": route.department == "academic_calendar",
        }
    else:
        checks = {
            "calendar_route": route.source_groups_to_search[:1] == ["academic_calendar_2025_2026"],
            "expected_tokens": all(token in answer for token in case.expected_tokens),
            "no_source_noise": not any(marker in answer.lower() for marker in ["source_group", "chunk", "page_article_reference"]),
            "no_lead_customer_task": not any(marker in answer.lower() for marker in ["lead", "customer", "task"]),
        }
    return {
        "id": case.id,
        "question": case.question,
        "expected_type": case.expected_type,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "route": route.source_groups_to_search,
        "department": route.department,
        "unsupported": route.unsupported_likely,
        "answer": answer[:220],
    }


def evaluate_overcapture(case: OvercaptureCase) -> dict[str, object]:
    route = fallback_intent_route(case.question)
    is_calendar = route.source_groups_to_search[:1] == ["academic_calendar_2025_2026"]
    helper_reply = None
    helper_reply_matches = True
    if case.expect_helper_reply is not None:
        helper_reply = bool(
            is_computer_science_spring_registration_question(case.question.lower())
            and official_academic_rules_regression_reply(case.question, "en")
        )
        helper_reply_matches = helper_reply == case.expect_helper_reply
    return {
        "id": case.id,
        "question": case.question,
        "expect_calendar": case.expect_calendar,
        "expect_helper_reply": case.expect_helper_reply,
        "helper_reply": helper_reply,
        "result": "PASS" if is_calendar == case.expect_calendar and helper_reply_matches else "FAIL",
        "route": route.source_groups_to_search,
        "department": route.department,
        "unsupported": route.unsupported_likely,
    }


def evaluate_fallback_overcapture(case: FallbackCase) -> dict[str, object]:
    answer = grounded_source_backed_reply(case.question, case.language, admissions_decision(case.language)) or ""
    blocked_calendar_markers = [
        "academic calendar",
        "9 - 14 March 2026",
        "30 March 2026",
        "15 - 20 September 2025",
        "22 - 27 September 2025",
        "9-14 áƒ›áƒáƒ áƒ¢",
        "30 áƒ›áƒáƒ áƒ¢",
    ]
    leaked_calendar = any(marker in answer for marker in blocked_calendar_markers)
    return {
        "id": case.id,
        "question": case.question,
        "result": "PASS" if not leaked_calendar else "FAIL",
        "answer": answer[:220],
    }


def evaluate_stale_date(case: StaleDateCase) -> dict[str, object]:
    answer = grounded_source_backed_reply(case.question, case.language, calendar_decision(case.language)) or ""
    expected_ok = all(token in answer for token in case.expected_tokens)
    forbidden_ok = not any(token in answer for token in case.forbidden_tokens)
    return {
        "id": case.id,
        "question": case.question,
        "result": "PASS" if expected_ok and forbidden_ok else "FAIL",
        "expected_ok": expected_ok,
        "forbidden_ok": forbidden_ok,
        "answer": answer[:260],
    }


def run_qa() -> dict[str, object]:
    cases = [evaluate(case) for case in CASES]
    overcapture_cases = [evaluate_overcapture(case) for case in OVERCAPTURE_CASES]
    fallback_cases = [evaluate_fallback_overcapture(case) for case in FALLBACK_OVERCAPTURE_CASES]
    stale_date_cases = [evaluate_stale_date(case) for case in STALE_DATE_CASES]
    root_causes = {}
    for case in cases:
        if case["result"] == "PASS":
            continue
        for name, passed in case["checks"].items():  # type: ignore[union-attr]
            if not passed:
                root_causes[name] = root_causes.get(name, 0) + 1
    overcapture_failures = [case for case in overcapture_cases if case["result"] != "PASS"]
    fallback_failures = [case for case in fallback_cases if case["result"] != "PASS"]
    stale_date_failures = [case for case in stale_date_cases if case["result"] != "PASS"]
    return {
        "total": len(cases),
        "PASS": sum(1 for case in cases if case["result"] == "PASS"),
        "PARTIAL": 0,
        "FAIL": sum(1 for case in cases if case["result"] == "FAIL"),
        "root_causes": root_causes,
        "cases": cases,
        "overcapture_regression": {
            "total": len(overcapture_cases),
            "PASS": len(overcapture_cases) - len(overcapture_failures),
            "FAIL": len(overcapture_failures),
            "cases": overcapture_cases,
        },
        "fallback_overcapture_regression": {
            "total": len(fallback_cases),
            "PASS": len(fallback_cases) - len(fallback_failures),
            "FAIL": len(fallback_failures),
            "cases": fallback_cases,
        },
        "stale_date_regression": {
            "total": len(stale_date_cases),
            "PASS": len(stale_date_cases) - len(stale_date_failures),
            "FAIL": len(stale_date_failures),
            "cases": stale_date_cases,
        },
        "safety": {
            "real_site_modified": False,
            "assets_uploaded_or_embedded": False,
            "frontend_netlify_changed": False,
            "db_secret_cors_bridgehub_changed": False,
            "contact_flow_submitted": False,
            "lead_customer_task_created": False,
            "public_launch": "NO-GO",
        },
    }


def main() -> int:
    result = run_qa()
    printable = {
        key: value
        for key, value in result.items()
        if key not in {"cases", "overcapture_regression", "fallback_overcapture_regression", "stale_date_regression"}
    }
    printable["overcapture_regression"] = {
        key: value
        for key, value in result["overcapture_regression"].items()  # type: ignore[union-attr]
        if key != "cases"
    }
    printable["fallback_overcapture_regression"] = {
        key: value
        for key, value in result["fallback_overcapture_regression"].items()  # type: ignore[union-attr]
        if key != "cases"
    }
    printable["stale_date_regression"] = {
        key: value
        for key, value in result["stale_date_regression"].items()  # type: ignore[union-attr]
        if key != "cases"
    }
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    for case in result["cases"]:  # type: ignore[index]
        print(f"{case['result']} {case['id']}: {case['question']}")  # type: ignore[index]
    for case in result["overcapture_regression"]["cases"]:  # type: ignore[index]
        print(f"{case['result']} overcapture {case['id']}: {case['question']}")  # type: ignore[index]
    for case in result["fallback_overcapture_regression"]["cases"]:  # type: ignore[index]
        print(f"{case['result']} fallback-overcapture {case['id']}: {case['question']}")  # type: ignore[index]
    for case in result["stale_date_regression"]["cases"]:  # type: ignore[index]
        print(f"{case['result']} stale-date {case['id']}: {case['question']}")  # type: ignore[index]
    overcapture_fail = result["overcapture_regression"]["FAIL"]  # type: ignore[index]
    fallback_fail = result["fallback_overcapture_regression"]["FAIL"]  # type: ignore[index]
    stale_date_fail = result["stale_date_regression"]["FAIL"]  # type: ignore[index]
    return 0 if result["FAIL"] == 0 and overcapture_fail == 0 and fallback_fail == 0 and stale_date_fail == 0 else 1  # type: ignore[index]


if __name__ == "__main__":
    sys.exit(main())
