from __future__ import annotations


def seed_source(
    client,
    *,
    source_key: str,
    title: str,
    source_domain: str,
    category: str,
    language: str,
    content: str,
    keywords: str,
) -> None:
    source_response = client.post(
        "/knowledge/sources",
        json={
            "source_key": source_key,
            "title": title,
            "source_type": "pdf",
            "status": "approved",
            "language": language,
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
            "language": language,
        },
    )
    assert snippet_response.status_code == 200


def seed_phase_10b_sources(client) -> None:
    seed_source(
        client,
        source_key="official_alte_8_pdf_kb_01_01_program_catalog",
        title="Program Catalog - Computer Science",
        source_domain="official_alte_pdf_kb",
        category="programs",
        language="en",
        content=(
            "The approved program catalog includes the Computer Science bachelor program. "
            "Computer Science is a program in the program catalog; program information belongs to program_catalog_sources."
        ),
        keywords="computer science program catalog bachelor program programs",
    )
    seed_source(
        client,
        source_key="official_alte_8_pdf_kb_01_01_program_catalog",
        title="Program Catalog - Computer Science KA",
        source_domain="official_alte_pdf_kb",
        category="programs",
        language="ka",
        content=(
            "\u10e1\u10d0\u10d2\u10d0\u10dc\u10db\u10d0\u10dc\u10d0\u10d7\u10da\u10d4\u10d1\u10da\u10dd \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8\u10e1 \u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10e8\u10d8 \u10db\u10dd\u10ea\u10d4\u10db\u10e3\u10da\u10d8\u10d0 Computer Science "
            "\u10e1\u10d0\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10dd \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0. Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0 \u10d4\u10d9\u10e3\u10d7\u10d5\u10dc\u10d8\u10e1 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8\u10e1 \u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10e1."
        ),
        keywords="Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0 \u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10d8",
    )
    seed_source(
        client,
        source_key="academic_calendar_geo_2025_2026",
        title="Academic Calendar 2025-2026 KA",
        source_domain="official_academic_rules",
        category="academic_rules",
        language="ka",
        content=(
            "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10d0\u10d3\u10db\u10d8\u10dc\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10e3\u10da\u10d8 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0: "
            "23 - 28 February 2026. \u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0: "
            "2 - 7 March 2026. Computer Science-\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0: 9-14 \u10db\u10d0\u10e0\u10e2\u10d8 / 9 - 14 March 2026."
        ),
        keywords="academic calendar registration spring bachelor Computer Science 23 28 2 7 9 14",
    )
    seed_source(
        client,
        source_key="academic_calendar_eng_2025_2026",
        title="Academic Calendar 2025-2026 EN",
        source_domain="official_academic_rules",
        category="academic_rules",
        language="en",
        content=(
            "Bachelor spring administrative registration is 23 - 28 February 2026. "
            "Bachelor spring academic registration is 2 - 7 March 2026. "
            "Computer Science spring registration is 9 - 14 March 2026."
        ),
        keywords="academic calendar registration spring bachelor Computer Science 23 28 2 7 9 14",
    )


def start_session(client, language: str = "ka") -> dict:
    response = client.post(
        "/chat/session/start",
        json={
            "source_domain": "join.alte.edu.ge",
            "language": language,
            "widget_variant": "pro_v2_safe",
            "metadata": {"phase": "10b_topic_switch_source_display"},
        },
    )
    assert response.status_code == 200
    return response.json()


def send(client, session: dict, message: str, language: str = "ka") -> dict:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "join.alte.edu.ge",
            "language": language,
            "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html",
            "widget_variant": "pro_v2_safe",
        },
    )
    assert response.status_code == 200
    return response.json()


def assert_public_sources_clean(payload: dict) -> None:
    sources = payload.get("used_sources") or []
    assert len(sources) <= 1
    if payload.get("answer_source_status") == "answered_from_approved_source":
        assert payload.get("public_source_label")
        assert sources == [payload["public_source_label"]]
    forbidden = [
        "full_alte_local_kb",
        "selected_alte_45_doc",
        "official_alte_8_pdf_kb",
        "official_academic_rules_full",
        "chunk",
        "source_key",
        "source_id",
    ]
    joined = " ".join(str(value) for value in sources + [payload.get("public_source_label") or ""]).lower()
    for marker in forbidden:
        assert marker not in joined


def assert_no_crm_side_effects(payload: dict) -> None:
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def assert_computer_science_program_answer(payload: dict) -> None:
    reply = payload["reply"]
    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert payload["source_group"] == "program_catalog_sources"
    assert "Computer Science" in reply or "\u10d9\u10dd\u10db\u10de\u10d8\u10e3\u10e2\u10d4\u10e0\u10e3\u10da" in reply
    assert "9-14" not in reply
    assert "23 - 28" not in reply
    assert "3x4" not in reply
    assert_no_crm_side_effects(payload)
    assert_public_sources_clean(payload)


def assert_cs_registration_answer(payload: dict) -> None:
    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert payload["source_group"] == "academic_calendar_2025_2026"
    assert "9-14" in payload["reply"] or "9 - 14" in payload["reply"]
    assert_no_crm_side_effects(payload)
    assert_public_sources_clean(payload)


def test_phase_10b_topic_switch_registration_to_bachelor_calendar_to_cs_program(client):
    seed_phase_10b_sources(client)
    session = start_session(client)

    clarification = send(client, session, "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1\u10d0\u10d0?")
    assert clarification["answer_source_status"] == "clarification_needed"
    assert clarification["clarification_needed"] is True
    assert clarification["used_sources"] == []

    bachelor = send(client, session, "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1?")
    assert bachelor["source_group"] == "academic_calendar_2025_2026"
    assert "23 - 28" in bachelor["reply"]
    assert "2 - 7" in bachelor["reply"]
    assert_public_sources_clean(bachelor)

    cs_program = send(client, session, "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4")
    assert_computer_science_program_answer(cs_program)


def test_phase_10b_topic_switch_program_clarification_to_cs_registration(client):
    seed_phase_10b_sources(client)
    session = start_session(client)

    clarification = send(client, session, "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d6\u10d4 \u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8")
    assert clarification["answer_source_status"] == "clarification_needed"
    assert clarification["used_sources"] == []

    registration = send(client, session, "Computer Science-\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1?")
    assert_cs_registration_answer(registration)


def test_phase_10b_computer_science_context_switches_back_and_forth(client):
    seed_phase_10b_sources(client)
    session = start_session(client)

    first_program = send(client, session, "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4")
    assert_computer_science_program_answer(first_program)

    registration = send(client, session, "Computer Science-\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1?")
    assert_cs_registration_answer(registration)

    second_program = send(client, session, "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4")
    assert_computer_science_program_answer(second_program)


def test_phase_10b_direct_computer_science_program_and_registration_intents_split(client):
    seed_phase_10b_sources(client)
    session = start_session(client)

    program_ka = send(client, session, "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4")
    assert_computer_science_program_answer(program_ka)

    program_en = send(client, session, "Tell me about the Computer Science program", "en")
    assert_computer_science_program_answer(program_en)

    registration_ka = send(client, session, "Computer Science-\u10d8\u10e1 \u10d2\u10d0\u10d6\u10d0\u10e4\u10ee\u10e3\u10da\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1?")
    assert_cs_registration_answer(registration_ka)

    registration_en = send(client, session, "When is Computer Science spring registration?", "en")
    assert_cs_registration_answer(registration_en)


def test_phase_10b_english_computer_science_program_uses_catalog_cross_language_fallback(client):
    seed_source(
        client,
        source_key="official_alte_8_pdf_kb_01_01_program_catalog",
        title="Program Catalog - Computer Science KA only",
        source_domain="official_alte_pdf_kb",
        category="programs",
        language="ka",
        content=(
            "\u10e1\u10d0\u10d2\u10d0\u10dc\u10db\u10d0\u10dc\u10d0\u10d7\u10da\u10d4\u10d1\u10da\u10dd \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8\u10e1 \u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10e8\u10d8 \u10db\u10dd\u10ea\u10d4\u10db\u10e3\u10da\u10d8\u10d0 Computer Science "
            "\u10e1\u10d0\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10dd \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0."
        ),
        keywords="Computer Science \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0 \u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10d8",
    )
    session = start_session(client, language="en")

    payload = send(client, session, "Tell me about the Computer Science program", "en")

    assert_computer_science_program_answer(payload)
