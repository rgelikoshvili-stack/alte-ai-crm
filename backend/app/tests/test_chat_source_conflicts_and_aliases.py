from sqlalchemy import select

from app.models import Customer, Lead, Task
from app.services.chat_service import (
    is_clearly_unsupported_official_question,
    is_official_academic_rules_text,
    is_selected_official_document_text,
    normalize_chat_retrieval_query,
)


def start_session(client, language="ka"):
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def create_source(client, *, title, source_domain, category="academic_rules", language="ka", status="approved"):
    response = client.post(
        "/knowledge/sources",
        json={
            "source_key": title.lower().replace(" ", "_"),
            "title": title,
            "source_type": "pdf",
            "status": status,
            "language": language,
            "source_domain": source_domain,
            "category": category,
            "sensitivity": "official" if source_domain.startswith("official") else "low",
        },
    )
    assert response.status_code == 200
    return response.json()


def create_snippet(client, source, *, title, content, keywords, category=None):
    response = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": source["source_key"],
            "title": title,
            "content": content,
            "category": category or source["category"] or "academic_rules",
            "source_domain": source["source_domain"],
            "sensitivity": source["sensitivity"],
            "keywords": keywords,
            "status": "approved",
            "language": source["language"],
        },
    )
    assert response.status_code == 200
    return response.json()


def seed_conflicting_sources(client):
    official_bachelor = create_source(client, title="ბაკალავრიატის დებულება", source_domain="official_academic_rules")
    create_snippet(
        client,
        official_bachelor,
        title="ბაკალავრიატის დებულება - ECTS",
        content="საბაკალავრო პროგრამის დასასრულებლად საჭიროა არანაკლებ 240 ECTS კრედიტის დაგროვება.",
        keywords="ბაკალავრიატი ბაკალავრიატის დასრულება ECTS კრედიტი 240 bachelor",
    )
    official_master = create_source(client, title="მაგისტრატურის დებულება", source_domain="official_academic_rules")
    create_snippet(
        client,
        official_master,
        title="მაგისტრატურის დებულება - ECTS",
        content="სამაგისტრო პროგრამისთვის საჭიროა არანაკლებ 120 ECTS კრედიტის დაგროვება.",
        keywords="მაგისტრატურა სამაგისტრო ECTS კრედიტი 120 master",
    )
    process = create_source(client, title="სასწავლო პროცესის მარეგულირებელი წესი", source_domain="official_academic_rules")
    create_snippet(
        client,
        process,
        title="სტუდენტის სტატუსის შეჩერება",
        content="სტუდენტის სტატუსის შეჩერების საერთო ვადა არ უნდა აღემატებოდეს 5 წელს.",
        keywords="სტატუსი სტატუსის შეჩერება შევიჩერო რამდენ ხანს 5 წელი student status suspension",
    )
    create_snippet(
        client,
        official_master,
        title="მაგისტრატურის ჩარიცხვის საბუთები",
        content=(
            "მაგისტრატურაზე ჩასარიცხად საჭიროა: პირადობის დამადასტურებელი დოკუმენტის ასლი; CV; "
            "3x4 ფოტოსურათი ბეჭდური და ელექტრონული ფორმით; სამხედრო აღრიცხვაზე ყოფნის დამადასტურებელი "
            "დოკუმენტის ასლი მამაკაცი აპლიკანტებისთვის; ნოტარიულად დამოწმებული დიპლომის ასლი; დიპლომის დანართის ასლი."
        ),
        keywords="მაგისტრატურა საბუთები დოკუმენტები ჩარიცხვა ID CV 3x4 სამხედრო ნოტარიული დიპლომის დანართი",
    )

    stale_local = create_source(client, title="ძველი ლოკალური საბაკალავრო აღწერა", source_domain="alte.edu.ge")
    create_snippet(
        client,
        stale_local,
        title="ძველი 180 კრედიტიანი აღწერა",
        content="ძველი აღწერის მიხედვით ბაკალავრიატი არის 180 კრედიტი.",
        keywords="ბაკალავრიატი კრედიტი 180 ECTS bachelor",
    )

    official_finance = create_source(
        client,
        title="ფინანსური მხარდაჭერის მექანიზმები",
        source_domain="official_alte_pdf_kb",
        category="finance",
    )
    create_snippet(
        client,
        official_finance,
        title="ფინანსური მხარდაჭერის მექანიზმები",
        content="დამტკიცებული წყარო აღწერს ფინანსური მხარდაჭერის მექანიზმებს და დაფინანსების წესს.",
        keywords="ფინანსური დახმარება ფინანსური მხარდაჭერა დაფინანსება funding rule financial support",
        category="finance",
    )
    old_finance = create_source(client, title="ძველი ფასდაკლების გვერდი", source_domain="alte.edu.ge", category="finance")
    create_snippet(
        client,
        old_finance,
        title="ძველი აქცია",
        content="ძველი ლოკალური წყარო ამბობს, რომ მოქმედებს 70% ფასდაკლება.",
        keywords="ფინანსური დახმარება აქცია ფასდაკლება financial support",
        category="finance",
    )

    ai_policy = create_source(client, title="AI გამოყენების პოლიტიკა", source_domain="official_alte_pdf_kb", category="policy")
    create_snippet(
        client,
        ai_policy,
        title="გენერაციული AI-ის გამოყენების პოლიტიკა",
        content="გენერაციული AI-ის გამოყენება უნდა მოხდეს უნივერსიტეტის დამტკიცებული წესებისა და აკადემიური კეთილსინდისიერების დაცვით.",
        keywords="AI-ის გამოყენება გენერაციული ხელოვნური ინტელექტი AI policy",
        category="policy",
    )


def ask(client, message, language="ka"):
    session = start_session(client, language=language)
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "alte.edu.ge",
            "language": language,
        },
    )
    assert response.status_code == 200
    return response.json()


def assert_no_info_side_effects(payload):
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def count_all(session_factory, model):
    import asyncio

    async def run():
        async with session_factory() as session:
            return len((await session.scalars(select(model))).all())

    return asyncio.run(run())


def test_georgian_aliases_route_to_official_sources_before_conflicting_old_sources(client):
    seed_conflicting_sources(client)

    cases = [
        ("რამდენი კრედიტია ბაკალავრიატი?", "240", ["180"]),
        ("ბაკალავრიატის დასრულებისთვის რამდენი ECTS სჭირდება?", "240", ["180"]),
        ("რამდენი კრედიტია სამაგისტრო პროგრამა?", "120", []),
        ("სტატუსი რამდენ ხანს შემიძლია შევიჩერო?", "5", []),
    ]
    for question, required, forbidden in cases:
        payload = ask(client, question)
        assert payload["answer_source_status"] == "answered_from_approved_source"
        assert required in payload["reply"]
        for token in forbidden:
            assert token not in payload["reply"]
        assert any("official_academic_rules" in source or "დებულება" in source for source in payload["used_sources"])
        assert_no_info_side_effects(payload)


def test_master_documents_financial_support_and_ai_policy_aliases(client):
    seed_conflicting_sources(client)

    documents = ask(client, "რა საბუთებია მაგისტრატურაზე?")
    assert documents["answer_source_status"] == "answered_from_approved_source"
    for expected in ["CV", "3x4", "სამხედრო", "ნოტარ", "დიპლომის დანართ"]:
        assert expected in documents["reply"]
    assert_no_info_side_effects(documents)

    finance = ask(client, "ფინანსური დახმარება არსებობს?")
    assert finance["answer_source_status"] == "answered_from_approved_source"
    assert any("ფინანსური_მხარდაჭერის_მექანიზმები" in source or "ფინანსური მხარდაჭერის მექანიზმები" in source for source in finance["used_sources"])
    assert "ფინანსური მხარდაჭერის" in finance["reply"]
    assert "70%" not in finance["reply"]
    assert_no_info_side_effects(finance)

    ai = ask(client, "AI-ის გამოყენება შეიძლება?")
    assert ai["answer_source_status"] == "answered_from_approved_source"
    assert ai["used_sources"]
    assert "უნივერსალურად დაშვებული ან აკრძალული" in ai["reply"]
    assert "AI ყოველთვის შეიძლება" not in ai["reply"]
    assert_no_info_side_effects(ai)


def test_unsupported_current_or_fake_questions_do_not_use_old_sources_or_create_crm_records(client, session_factory):
    seed_conflicting_sources(client)

    unsupported_questions = [
        "2031 კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?",
        "მიმდინარე სწავლის ფასი რა არის?",
        "კონკრეტული კონსულტანტის ტელეფონი მომეცი",
        "დღევანდელი აქცია რა არის?",
    ]
    for question in unsupported_questions:
        payload = ask(client, question)
        assert payload["answer_source_status"] == "no_approved_source_found"
        assert "70%" not in payload["reply"]
        assert_no_info_side_effects(payload)

    assert count_all(session_factory, Customer) == 0
    assert count_all(session_factory, Lead) == 0
    assert count_all(session_factory, Task) == 0


def test_selected_official_doc_question_does_not_fall_back_to_marketing_or_local_kb(client):
    old_local = create_source(client, title="ძველი AI მარკეტინგული FAQ", source_domain="alte.edu.ge", category="policy")
    create_snippet(
        client,
        old_local,
        title="ძველი AI FAQ",
        content="ძველი FAQ ამბობს, რომ AI ყოველთვის შეიძლება ყველა დავალებაში.",
        keywords="AI-ის გამოყენება ხელოვნური ინტელექტი ყოველთვის შეიძლება",
        category="policy",
    )

    payload = ask(client, "AI-ის გამოყენება შეიძლება?")

    assert payload["answer_source_status"] == "no_approved_source_found"
    assert "ყოველთვის შეიძლება" not in payload["reply"]
    assert_no_info_side_effects(payload)


def test_ambiguous_program_credit_question_asks_for_clarification_without_crm_side_effects(client):
    payload = ask(client, "რამდენი კრედიტია პროგრამა?")

    assert "რომელ პროგრამას გულისხმობთ" in payload["reply"]
    assert "240" in payload["reply"]
    assert "120" in payload["reply"]
    assert_no_info_side_effects(payload)


def test_alias_and_unsupported_classifiers_cover_requested_wordings():
    for question in [
        "რამდენი კრედიტია ბაკალავრიატი?",
        "ბაკალავრიატის დასრულებისთვის რამდენი ECTS სჭირდება?",
        "რა საბუთებია მაგისტრატურაზე?",
        "სტატუსი რამდენ ხანს შემიძლია შევიჩერო?",
    ]:
        assert is_official_academic_rules_text(question)
        assert normalize_chat_retrieval_query(question) != question

    assert is_selected_official_document_text("ფინანსური დახმარება არსებობს?")
    assert is_selected_official_document_text("AI-ის გამოყენება შეიძლება?")

    for question in [
        "2031 კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?",
        "მიმდინარე სწავლის ფასი რა არის?",
        "კონკრეტული კონსულტანტის ტელეფონი მომეცი",
        "დღევანდელი აქცია რა არის?",
    ]:
        assert is_clearly_unsupported_official_question(question)
