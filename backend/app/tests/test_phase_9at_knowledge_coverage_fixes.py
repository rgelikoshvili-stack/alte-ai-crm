from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import select

from app.models import Conversation, Customer, KnowledgeSnippet, KnowledgeSource, Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service
from app.services.knowledge_routing_service import classify_knowledge_route, source_group_config


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client, language: str = "ka") -> dict:
    response = client.post("/chat/session/start", json={"source_domain": "join.alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def send_message(client, session: dict, message: str, language: str = "ka") -> dict:
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


def patch_ai(monkeypatch, *, intent: str = "general_info", confidence: float = 0.92, language: str = "ka") -> None:
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (
            AIAnalysisResult(
                reply="The AI service is temporarily unavailable. I can connect you with the relevant department.",
                language=language,
                intent=intent,
                confidence=confidence,
                should_create_lead=False,
                should_handover=False,
                extracted_contact=ExtractedContact(),
                conversation_summary="Phase 9AT regression",
            ),
            {"provider": "test", "model": "forced", "raw_response": None},
        ),
    )


def seed_official_source(client) -> None:
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": "phase_9at_official_source",
            "title": "Phase 9AT official academic and admissions source",
            "source_type": "pdf",
            "status": "approved",
            "language": "ka",
            "source_domain": "official_academic_rules",
            "category": "academic_rules",
            "sensitivity": "official academic rule",
        },
    )
    assert source.status_code == 200
    source_payload = source.json()
    snippets = [
        (
            "Computer Science spring calendar",
            "კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია არის 9-14 მარტი; სემესტრი იწყება 30 მარტს.",
            "academic_calendar",
            "კომპიუტერული მეცნიერება გაზაფხულის სემესტრი რეგისტრაცია 9-14 მარტი 30 მარტი",
        ),
        (
            "Bachelor admission documents",
            "ბაკალავრიატზე ჩარიცხვისთვის საჭიროა საბუთები და ჩარიცხვის ოფიციალური დოკუმენტები.",
            "admissions",
            "ბაკალავრიატი მიღება საბუთები დოკუმენტები ჩარიცხვა admissions documents",
        ),
        (
            "Master admission documents",
            "მაგისტრატურაზე ჩასარიცხად საჭიროა პირადობის ასლი, CV, ფოტო, დიპლომი და დიპლომის დანართი.",
            "admissions",
            "მაგისტრატურა საბუთები დოკუმენტები CV დიპლომი master admission documents",
        ),
        (
            "Bachelor ECTS",
            "საბაკალავრო პროგრამის დასასრულებლად საჭიროა არანაკლებ 240 ECTS კრედიტის დაგროვება.",
            "academic_rules",
            "საბაკალავრო ბაკალავრიატი bachelor ECTS კრედიტი 240 პროგრამის დასასრულებლად",
        ),
    ]
    for title, content, category, keywords in snippets:
        response = client.post(
            "/knowledge/snippets",
            json={
                "source_id": source_payload["id"],
                "source_key": source_payload["source_key"],
                "title": title,
                "content": content,
                "category": category,
                "source_domain": "official_academic_rules",
                "sensitivity": "official academic rule",
                "keywords": keywords,
                "status": "approved",
                "language": "ka",
            },
        )
        assert response.status_code == 200


def seed_selected_source(
    client,
    *,
    source_key: str,
    title: str,
    category: str,
    content: str,
    keywords: str,
) -> None:
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": source_key,
            "title": title,
            "source_type": "policy",
            "status": "approved",
            "language": "en",
            "source_domain": "alte.edu.ge",
            "category": category,
            "sensitivity": "approved public policy",
        },
    )
    assert source.status_code == 200
    source_payload = source.json()
    response = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source_payload["id"],
            "source_key": source_payload["source_key"],
            "title": title,
            "content": content,
            "category": category,
            "source_domain": "alte.edu.ge",
            "sensitivity": "approved public policy",
            "keywords": keywords,
            "status": "approved",
            "language": "en",
        },
    )
    assert response.status_code == 200


def assert_no_crm_records(session_factory) -> None:
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def conversation_by_id(session_factory, conversation_id: str) -> Conversation:
    rows = fetch_all(session_factory, select(Conversation).where(Conversation.id == conversation_id))
    assert len(rows) == 1
    return rows[0]


def test_phase_9at_source_group_configs_have_active_files():
    assert source_group_config("academic_calendar_2025_2026")["source_files"]
    assert source_group_config("admissions_rules")["source_files"]
    assert source_group_config("finance_sources")["source_files"]
    assert source_group_config("library_sources")["source_files"]
    assert source_group_config("it_support_sources")["source_files"]
    assert source_group_config("career_sources")["source_files"]
    assert source_group_config("library_sources")["exact_answer_allowed"] is True
    assert source_group_config("it_support_sources")["exact_answer_allowed"] is True


def test_phase_9at_calendar_and_admissions_route_to_expected_source_groups():
    calendar = classify_knowledge_route("როდის იწყება კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია?")
    admissions = classify_knowledge_route("ბაკალავრიატზე ჩასაბარებლად რა საბუთებია საჭირო?")

    assert calendar.primary_source_group == "academic_calendar_2025_2026"
    assert admissions.primary_source_group == "admissions_rules"


def test_phase_9at_cs_spring_registration_source_backed_no_generic_fallback(client, session_factory, monkeypatch):
    seed_official_source(client)
    patch_ai(monkeypatch, intent="deadline_question")
    session = start_session(client)

    payload = send_message(client, session, "როდის იწყება კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "9" in payload["reply"] and "14" in payload["reply"]
    assert "30" in payload["reply"]
    assert "AI service is temporarily unavailable" not in payload["reply"]
    assert payload["should_handover"] is False
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is False
    assert_no_crm_records(session_factory)


def test_phase_9at_admission_documents_source_backed_no_generic_fallback(client, session_factory, monkeypatch):
    seed_official_source(client)
    patch_ai(monkeypatch, intent="admission_interest")
    session = start_session(client)

    payload = send_message(client, session, "მაგისტრატურაზე ჩასაბარებლად რა დოკუმენტებია საჭირო?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "CV" in payload["reply"] or "დიპლომ" in payload["reply"]
    assert "AI service is temporarily unavailable" not in payload["reply"]
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert_no_crm_records(session_factory)


def test_phase_9at_weak_selected_document_routes_use_targeted_approved_sources(client, session_factory, monkeypatch):
    weak_sources = [
        {
            "source_key": "selected_alte_45_doc_34_097_jtv38r4nf8",
            "title": "Dean's List Award Terms and Conditions",
            "category": "finance",
            "content": "Dean's List Award Terms and Conditions describe approved financial support and grant eligibility.",
            "keywords": "Dean's List Award state grant social grant financial support scholarship funding rule",
            "question": "What does the Dean's List grant policy say?",
            "expected_department": "finance",
        },
        {
            "source_key": "selected_alte_45_doc_24_068_trphmmn9xg",
            "title": "Library provision",
            "category": "library",
            "content": "The library provision describes library services, resources, books, and electronic databases.",
            "keywords": "library provision library resources books electronic databases catalog",
            "question": "How can I use library resources?",
            "expected_department": "library",
        },
        {
            "source_key": "selected_alte_45_doc_38_106_3cvbwtpgx5",
            "title": "Information technology management policy",
            "category": "it_policy",
            "content": "The information technology management policy covers IT infrastructure, technical access, platform support, and EMIS support routing.",
            "keywords": "information technology management policy infrastructure EMIS student portal platform support technical access",
            "question": "What does the IT policy say about EMIS platform support?",
            "expected_department": "it_support",
        },
        {
            "source_key": "selected_alte_45_doc_39_115_c8hejj7ftx",
            "title": "IRO Policy",
            "category": "iro_policy",
            "content": "IRO Policy describes the International Relations Office, international cooperation, exchange, and mobility coordination.",
            "keywords": "IRO Policy international relations office international cooperation mobility exchange",
            "question": "What does the IRO Policy cover?",
            "expected_department": "international",
        },
        {
            "source_key": "selected_alte_45_doc_44_122_vj966ioesx",
            "title": "EDI Policy",
            "category": "edi_policy",
            "content": "EDI Policy covers equality, diversity, inclusion, and equal treatment principles.",
            "keywords": "EDI Policy equality diversity inclusion equal treatment",
            "question": "What does the EDI Policy cover?",
            "expected_department": "student_services",
        },
        {
            "source_key": "selected_alte_45_doc_42_120_kyxh61fecu",
            "title": "Alte Sustainability Strategy",
            "category": "sustainability",
            "content": "Alte Sustainability Strategy covers sustainable development priorities and sustainability reporting.",
            "keywords": "sustainability strategy sustainable development sustainability report",
            "question": "What does the sustainability strategy cover?",
            "expected_department": "student_services",
        },
    ]
    for item in weak_sources:
        seed_selected_source(
            client,
            source_key=item["source_key"],
            title=item["title"],
            category=item["category"],
            content=item["content"],
            keywords=item["keywords"],
        )
    seed_official_source(client)
    patch_ai(monkeypatch, intent="general_info", language="en")

    for item in weak_sources:
        session = start_session(client, language="en")
        payload = send_message(client, session, item["question"], language="en")

        assert payload["answer_source_status"] == "answered_from_approved_source"
        assert payload["department_key"] == item["expected_department"]
        assert payload["should_handover"] is False
        assert any(item["source_key"] in source for source in payload["used_sources"])
        assert not any("phase_9at_official_source" in source for source in payload["used_sources"])
    assert_no_crm_records(session_factory)


def test_phase_9at_unsupported_fake_scholarship_and_tuition_do_not_match_sources(client, session_factory, monkeypatch):
    seed_official_source(client)
    patch_ai(monkeypatch, intent="finance_question")
    session = start_session(client)

    scholarship = send_message(client, session, "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?")
    tuition = send_message(client, session, "ზუსტად რა ღირს 2031 წლის AI კოსმოსური პროგრამის სწავლა?")

    assert scholarship["answer_source_status"] == "no_approved_source_found"
    assert scholarship["should_handover"] is True
    assert tuition["answer_source_status"] == "no_approved_source_found"
    assert tuition["should_handover"] is True
    assert "70%" not in scholarship["reply"]
    assert "ლარი" not in tuition["reply"]
    assert_no_crm_records(session_factory)


def test_phase_9at_it_emis_fallback_persists_handover(client, session_factory, monkeypatch):
    patch_ai(monkeypatch, intent="technical_support")
    session = start_session(client)

    payload = send_message(client, session, "emis.alte.edu.ge-ში ვერ შევდივარ")

    assert payload["answer_source_status"] == "no_approved_source_found"
    assert payload["department_key"] == "it_support"
    assert payload["should_handover"] is True
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is True
    assert_no_crm_records(session_factory)


def test_phase_9at_informational_and_wait_policies_remain_safe(client, session_factory, monkeypatch):
    seed_official_source(client)
    patch_ai(monkeypatch, intent="general_info")
    session = start_session(client)

    info = send_message(client, session, "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?")
    wait = client.post(
        f"/chat/handover/{session['conversation_id']}",
        json={
            "session_id": session["session_id"],
            "selected_department": "programs",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": "მინდა ოპერატორს დაველოდო",
        },
    )

    assert info["should_handover"] is False
    assert wait.status_code == 200
    assert wait.json()["status"] == "waiting_for_operator"
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is True
    assert_no_crm_records(session_factory)


def test_phase_9at_no_mojibake_and_public_launch_no_go():
    files = [
        PROJECT_ROOT / "backend" / "app" / "data" / "evaluation" / "phase_9as_full_knowledge_qa.json",
        PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "áƒ" not in text
        assert "�" not in text
    public = PUBLIC_LAUNCH.read_text(encoding="utf-8").lower()
    assert "public_launch_decision=go" not in public
    assert "no-go" in public
