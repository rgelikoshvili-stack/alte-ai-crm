from __future__ import annotations

from app.services.chat_service import (
    grounded_source_backed_reply,
    is_computer_science_spring_registration_question,
    official_academic_rules_regression_reply,
)
from app.services.claude_intent_router_service import fallback_intent_route
from app.services.knowledge_routing_service import KnowledgeRouteDecision


def calendar_decision(language: str = "en") -> KnowledgeRouteDecision:
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
        reason="phase_9be_test",
    )


def admissions_decision(language: str = "en") -> KnowledgeRouteDecision:
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
        reason="phase_9be_test",
    )


def calendar_answer(question: str, language: str = "en") -> str:
    return grounded_source_backed_reply(question, language, calendar_decision(language)) or ""


def assert_calendar_answer(question: str, language: str, *tokens: str) -> None:
    route = fallback_intent_route(question)
    answer = calendar_answer(question, language)
    assert route.source_groups_to_search[:1] == ["academic_calendar_2025_2026"]
    assert route.unsupported_likely is False
    assert all(token in answer for token in tokens)
    assert not any(marker in answer.lower() for marker in ["source_group", "chunk", "page_article_reference", "official_academic_rules_full"])


def test_phase_9be_bachelor_calendar_exact_dates():
    assert_calendar_answer("საბაკალავრო პროგრამებისთვის შემოდგომის სემესტრი როდის იწყება?", "ka", "29 September 2025")
    assert_calendar_answer("საბაკალავრო პროგრამებისთვის გაზაფხულის სემესტრის დასკვნითი გამოცდები როდის არის?", "ka", "29 June - 11 July 2026")
    assert_calendar_answer("საბაკალავრო პროგრამებისთვის გაზაფხულის აკადემიური რეგისტრაცია როდის არის?", "ka", "2 - 7 March 2026")
    assert_calendar_answer("When are spring final exams for Bachelor programs except Computer Science?", "en", "29 June - 11 July 2026")


def test_phase_9be_computer_science_calendar_exact_dates():
    assert_calendar_answer("Computer Science-ის გაზაფხულის სემესტრის რეგისტრაცია როდის არის?", "ka", "9 - 14 March 2026")
    assert_calendar_answer("Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?", "ka", "30 March 2026")
    assert_calendar_answer("Computer Science-ის გაზაფხულის დასკვნითი გამოცდები როდის არის?", "ka", "13 - 25 July 2026")
    assert_calendar_answer("When is academic registration for Computer Science in spring?", "en", "9 - 14 March 2026")
    assert_calendar_answer("When do spring final exams take place for Computer Science?", "en", "13 - 25 July 2026")


def test_phase_9be_master_and_one_cycle_exact_dates():
    assert_calendar_answer("სამაგისტრო პროგრამებისთვის გაზაფხულის სემესტრი როდის იწყება?", "ka", "9 March 2026")
    assert_calendar_answer("სამაგისტრო პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?", "ka", "29 June - 11 July 2026")
    assert_calendar_answer("ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?", "ka", "20 July - 1 August 2026")
    assert_calendar_answer("ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდების აღდგენა როდის არის?", "ka", "3 - 8 August 2026")
    assert_calendar_answer("When does the spring semester start for Master programs?", "en", "9 March 2026")
    assert_calendar_answer("When are final exams for one-cycle programs in spring?", "en", "20 July - 1 August 2026")


def test_phase_9be_first_year_one_cycle_english_exact_dates():
    assert_calendar_answer("When does the fall semester start for first-year students of one-cycle English education programs?", "en", "3 November 2025")
    assert_calendar_answer("When are fall midterm exams for first-year one-cycle English programs?", "en", "5 - 10 January 2026")


def test_phase_9be_holiday_exact_dates():
    assert_calendar_answer("ახალი წლის არდადეგები როდის არის?", "ka", "30 December 2025 - 4 January 2026")
    assert_calendar_answer("აღდგომის არდადეგები როდის არის?", "ka", "10 - 13 April 2026")
    assert_calendar_answer("What are the New Year holidays?", "en", "30 December 2025 - 4 January 2026")
    assert_calendar_answer("What are the Easter holidays?", "en", "10 - 13 April 2026")
    assert_calendar_answer("აკადემიური კალენდრის უქმე დღეები რომლებია?", "ka", "14 October", "26 May")


def test_phase_9be_ambiguous_calendar_questions_ask_clarification():
    for question in [
        "გამოცდები როდის არის?",
        "რეგისტრაცია როდის არის?",
        "სემესტრი როდის იწყება?",
        "When are exams?",
        "When is registration?",
        "When does the semester start?",
    ]:
        route = fallback_intent_route(question)
        assert route.needs_clarification is True
        assert route.source_groups_to_search == []
        assert route.department == "academic_calendar"
        assert route.clarification_question


def test_phase_9be_future_year_calendar_questions_are_unsupported():
    for question in [
        "2031 წლის გაზაფხულის სემესტრი როდის იწყება?",
        "2027 წლის Computer Science-ის გამოცდები როდისაა?",
        "When does the 2028 spring semester start?",
    ]:
        route = fallback_intent_route(question)
        assert route.unsupported_likely is True
        assert route.source_groups_to_search == []
        assert route.department == "academic_calendar"


def test_phase_9be_program_catalog_routing_remains_intact():
    for question in [
        "How many educational programs does Alte University have in total?",
        "List Alte University's master programs.",
        "What languages does the Computer Science program appear in in the catalog?",
    ]:
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[:1] == ["program_catalog_sources"]
        assert route.unsupported_likely is False


def test_phase_9be_registration_requirements_do_not_overcapture_calendar():
    for question in [
        "What are updated registration requirements for bachelor admission?",
        "What are candidate registration requirements for bachelor admission?",
        "What are outdated registration requirements for bachelor admission?",
        "What are updated Computer Science spring semester registration requirements?",
        "What are candidate Computer Science spring semester registration requirements?",
        "What are outdated Computer Science spring semester registration requirements?",
        "What are the registration requirements for bachelor admission?",
        "What documents are required for bachelor registration?",
        "What are Computer Science spring registration requirements?",
        "What documents are required for Computer Science spring registration?",
        "Computer Science-ის გაზაფხულის რეგისტრაციის მოთხოვნები რა არის?",
        "Computer Science-ის გაზაფხულის რეგისტრაციისთვის რა საბუთებია საჭირო?",
        "ბაკალავრზე რეგისტრაციის მოთხოვნები რა არის?",
        "ბაკალავრზე რეგისტრაციისთვის რა საბუთებია საჭირო?",
    ]:
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[:1] != ["academic_calendar_2025_2026"]
        assert route.department != "academic_calendar"


def test_phase_9be_cs_spring_helper_does_not_substring_match_date_words():
    for question in [
        "What are updated Computer Science spring semester registration requirements?",
        "What are candidate Computer Science spring semester registration requirements?",
        "What are outdated Computer Science spring semester registration requirements?",
    ]:
        assert is_computer_science_spring_registration_question(question.lower()) is False
        assert official_academic_rules_regression_reply(question, "en") is None
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[:1] != ["academic_calendar_2025_2026"]
        assert route.department != "academic_calendar"


def test_phase_9be_grounded_source_backed_reply_does_not_calendar_fallback_for_admissions():
    calendar_dates = [
        "9 - 14 March 2026",
        "30 March 2026",
        "15 - 20 September 2025",
        "22 - 27 September 2025",
    ]
    for question in [
        "What documents are required for Computer Science spring registration?",
        "What are updated Computer Science spring semester registration requirements?",
        "What are candidate Computer Science spring semester registration requirements?",
        "What are the registration requirements for bachelor admission?",
        "What documents are required for bachelor registration?",
    ]:
        answer = grounded_source_backed_reply(question, "en", admissions_decision("en")) or ""
        assert not any(date in answer for date in calendar_dates)
        assert "academic calendar" not in answer.lower()


def test_phase_9be_grounded_source_backed_reply_calendar_source_group_still_answers_dates():
    answer = calendar_answer("What date does Computer Science spring registration start?", "en")
    assert "9 - 14 March 2026" in answer
    assert "30 March 2026" in answer


def test_phase_9be_broad_bachelor_registration_uses_approved_dates():
    for question in [
        "When is bachelor registration?",
        "What date does bachelor registration start?",
    ]:
        answer = calendar_answer(question, "en")
        assert "15 - 20 September 2025" in answer
        assert "22 - 27 September 2025" in answer
        assert "23 - 28 February 2026" in answer
        assert "2 - 7 March 2026" in answer
        assert "8-13 September 2025" not in answer
        assert "8 - 13 September 2025" not in answer
        assert "academic registration - 15 - 20 September 2025" not in answer
        assert "academic registration: 15 - 20 September 2025" not in answer


def test_phase_9be_broad_bachelor_registration_georgian_uses_approved_dates():
    answer = calendar_answer("ბაკალავრზე რეგისტრაცია როდის არის?", "ka")
    assert "15 - 20 September 2025" in answer
    assert "22 - 27 September 2025" in answer
    assert "23 - 28 February 2026" in answer
    assert "2 - 7 March 2026" in answer
    assert "8-13" not in answer
    assert "8 - 13" not in answer


def test_phase_9be_computer_science_registration_dates_still_use_cs_mapping():
    spring_answer = calendar_answer("When is Computer Science spring registration?", "en")
    fall_answer = calendar_answer("When is Computer Science fall academic registration?", "en")
    assert "9 - 14 March 2026" in spring_answer
    assert "29 September - 4 October 2025" in fall_answer


def test_phase_9be_registration_date_questions_still_route_calendar():
    for question in [
        "When is bachelor registration?",
        "What date does bachelor registration start?",
        "What are the registration dates for Computer Science?",
        "What date does Computer Science spring registration start?",
        "When is Computer Science spring registration?",
        "What date is Computer Science spring registration?",
        "ბაკალავრზე რეგისტრაცია როდის არის?",
        "Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?",
        "Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?",
    ]:
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[:1] == ["academic_calendar_2025_2026"]
        assert route.department == "academic_calendar"
        assert route.unsupported_likely is False


def test_phase_9be_no_lead_customer_task_creation_claims_in_answer_layer():
    answer = calendar_answer("When do spring final exams take place for Computer Science?", "en")
    assert "13 - 25 July 2026" in answer
    assert "lead" not in answer.lower()
    assert "customer" not in answer.lower()
    assert "task" not in answer.lower()
