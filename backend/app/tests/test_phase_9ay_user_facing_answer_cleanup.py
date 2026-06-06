from __future__ import annotations

from types import SimpleNamespace

from app.services.chat_service import (
    build_source_backed_reply,
    clean_public_answer_text,
    grounded_admissions_reply,
    grounded_calendar_reply,
    grounded_student_status_reply,
    knowledge_payload_from_results,
    official_academic_rules_regression_reply,
)


FORBIDDEN_PUBLIC_MARKERS = (
    "Official source",
    "Reference:",
    "Policy:",
    "answer only from",
    "handover if",
    "official_academic_rules",
    "chunk",
    "p022_c050",
    "page 22",
)


def assert_public_answer_is_clean(answer: str) -> None:
    lowered = answer.lower()
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        assert marker.lower() not in lowered


def fake_retrieval_item(*, source_key: str, title: str, category: str = "academic_rules"):
    source = SimpleNamespace(
        source_key=source_key,
        title=title,
        category=category,
        source_domain="official_alte_pdf_kb",
        source_path=None,
        document_id=None,
    )
    snippet = SimpleNamespace(
        id=f"snippet-{source_key}",
        source_key=source_key,
        title=title,
        content="approved excerpt",
        category=category,
        source_domain="official_alte_pdf_kb",
        source_path=None,
        document_id=None,
    )
    return SimpleNamespace(source=source, snippet=snippet, score=1.0, source_status="approved")


def test_clean_public_answer_removes_internal_policy_and_source_lines():
    dirty = """
    Official source: official_academic_rules_full_p001_c001
    Reference: chunk 4
    Policy: answer only from this official source; handover if the answer is not supported.
    The public answer is 240 ECTS. page 22 p022_c050
    Source: official_academic_rules_full_p002_c003.
    """
    answer = clean_public_answer_text(dirty)
    assert answer == "The public answer is 240 ECTS."
    assert_public_answer_is_clean(answer)


def test_inline_chunk_marker_is_stripped_without_removing_sentence():
    answer = clean_public_answer_text("სტუდენტის სტატუსის შეჩერება შესაძლებელია 5 წლით. chunk 2")
    assert answer == "სტუდენტის სტატუსის შეჩერება შესაძლებელია 5 წლით."
    assert_public_answer_is_clean(answer)


def test_inline_official_source_token_is_stripped_without_removing_sentence():
    answer = clean_public_answer_text(
        "სამაგისტრო პროგრამა მოიცავს 120 ECTS კრედიტს. official_academic_rules_full_p022_c050"
    )
    assert answer == "სამაგისტრო პროგრამა მოიცავს 120 ECTS კრედიტს."
    assert_public_answer_is_clean(answer)


def test_inline_page_and_chunk_markers_are_stripped_without_removing_sentence():
    answer = clean_public_answer_text("საბაკალავრო პროგრამა მოიცავს 240 ECTS კრედიტს. page 22; chunk 50")
    assert answer == "საბაკალავრო პროგრამა მოიცავს 240 ECTS კრედიტს."
    assert_public_answer_is_clean(answer)


def test_control_only_source_line_is_removed():
    answer = clean_public_answer_text("Official source: official_academic_rules_full_01_p022_c050")
    assert answer == ""


def test_policy_control_line_is_removed():
    answer = clean_public_answer_text("Policy: answer only from this official source")
    assert answer == ""


def test_mixed_multiline_answer_keeps_answer_and_removes_control_lines():
    answer = clean_public_answer_text(
        "\n".join(
            [
                "სამაგისტრო პროგრამა მოიცავს 120 ECTS კრედიტს. chunk 2",
                "Official source: official_academic_rules_full_01_p022_c050",
                "Policy: answer only from this official source",
            ]
        )
    )
    assert answer == "სამაგისტრო პროგრამა მოიცავს 120 ECTS კრედიტს."
    assert_public_answer_is_clean(answer)


def test_source_backed_bachelor_credits_answer_has_no_internal_debug_text():
    reply = official_academic_rules_regression_reply(
        "How many ECTS credits are required for bachelor completion?",
        "en",
    )
    answer = build_source_backed_reply(
        SimpleNamespace(reply=f"{reply}\n\nOfficial source: official_academic_rules_full_p001_c001", language="en"),
        ["official_academic_rules_full_p001_c001"],
    )
    assert "240" in answer
    assert_public_answer_is_clean(answer)


def test_source_backed_master_credits_answer_has_no_internal_source_labels():
    reply = official_academic_rules_regression_reply(
        "რამდენი კრედიტია საჭირო სამაგისტრო პროგრამისთვის?",
        "ka",
    )
    answer = build_source_backed_reply(
        SimpleNamespace(reply=f"{reply}\n\nწყარო: official_academic_rules_full_p002_c004 chunk 2", language="ka"),
        ["official_academic_rules_full_p002_c004 chunk 2"],
    )
    assert "120" in answer
    assert_public_answer_is_clean(answer)


def test_suspension_grounds_and_duration_are_distinct_answers():
    grounds = grounded_student_status_reply("რა შემთხვევაში შეიძლება სტუდენტის სტატუსის შეჩერება?", True)
    duration = grounded_student_status_reply("რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?", True)

    assert grounds != duration
    assert "5 წლ" in duration
    assert "წერილობითი განცხადება" in grounds
    assert "უცხოეთში სწავლა" in grounds
    assert "ავადმყოფობა" in grounds
    assert "ორსულობა" in grounds
    assert "სამხედრო სამსახური" in grounds
    assert "სწავლის საფასურის გადაუხდელობა" in grounds
    assert "რეგისტრაციის არ გავლა" in grounds
    assert "დოკუმენტების ვადაში არ წარმოდგენა" in grounds
    assert_public_answer_is_clean(grounds)
    assert_public_answer_is_clean(duration)


def test_official_academic_status_shortcut_preserves_grounds_question():
    answer = official_academic_rules_regression_reply("რა შემთხვევაში შეიძლება სტუდენტის სტატუსის შეჩერება?", "ka")

    assert answer
    assert "წერილობითი განცხადება" in answer
    assert "ავადმყოფობა" in answer
    assert "5 წელს" not in answer
    assert_public_answer_is_clean(answer)


def test_bachelor_admission_documents_returns_specific_document_list():
    answer = grounded_admissions_reply("ჩამომითვალე ბაკალავრიატზე მიღებისთვის საჭირო საბუთები", True)
    assert "საბუთ" in answer
    assert "პირადობის" in answer
    assert "სრული ზოგადი განათლების" in answer
    assert "განცხადება" in answer
    assert "ხელშეკრულ" in answer
    assert "სამხედრო აღრიცხვაზე" in answer
    assert_public_answer_is_clean(answer)


def test_calendar_reply_returns_clean_dates_without_internal_chunks():
    answer = grounded_calendar_reply("კომპიუტერული მეცნიერების გაზაფხულის რეგისტრაცია როდის არის?", True)
    assert "9-14 მარტ" in answer
    assert "30 მარტ" in answer
    assert_public_answer_is_clean(answer)


def test_used_sources_are_public_labels_for_known_internal_sources():
    payload = knowledge_payload_from_results(
        [
            fake_retrieval_item(
                source_key="official_academic_rules_full_08_study_process_p001_c001",
                title="official_academic_rules_full_08_study_process chunk 1",
            ),
            fake_retrieval_item(
                source_key="official_alte_8_pdf_kb_02_02_academic_calendar_2025_2026_p001_c001",
                title="Academic Calendar 2025-2026 p.1 chunk 1",
                category="calendar",
            ),
        ]
    )
    assert payload["used_sources"] == [
        "სასწავლო პროცესის მარეგულირებელი წესი",
        "აკადემიური კალენდარი 2025–2026",
    ]
    for label in payload["used_sources"]:
        assert_public_answer_is_clean(label)


def test_used_sources_include_human_readable_admissions_labels():
    payload = knowledge_payload_from_results(
        [
            fake_retrieval_item(
                source_key="official_alte_8_pdf_kb_03_admissions_rules_p022_c050",
                title="Admissions rules page 22 chunk 50",
                category="admissions",
            ),
            fake_retrieval_item(
                source_key="official_alte_8_pdf_kb_04_international_admissions_p003_c002",
                title="International admissions source p.3 chunk 2",
                category="international_admissions",
            ),
        ]
    )
    assert payload["used_sources"] == ["მიღების წესი", "საერთაშორისო მიღების წესი"]
    for label in payload["used_sources"]:
        assert_public_answer_is_clean(label)
