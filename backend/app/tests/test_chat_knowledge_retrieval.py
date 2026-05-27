from app.schemas.chat import AIAnalysisResult
from app.schemas.qualification import LeadQualificationResult
from app.services.chat_service import apply_no_contact_lead_guard, build_source_backed_reply


def start_session(client, language="en"):
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def create_approved_source_and_snippet(client, *, title, content, category, keywords, language="en", program_name=None):
    source_response = client.post(
        "/knowledge/sources",
        json={"title": f"{title} Source", "source_type": "faq", "status": "approved", "language": language},
    )
    assert source_response.status_code == 200
    source = source_response.json()
    snippet_response = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "title": title,
            "content": content,
            "category": category,
            "program_name": program_name,
            "keywords": keywords,
            "status": "approved",
            "language": language,
        },
    )
    assert snippet_response.status_code == 200
    return snippet_response.json()


def test_chat_uses_approved_admission_snippet(client):
    create_approved_source_and_snippet(
        client,
        title="Business admission requirements",
        content="Business admission requires an application and documents.",
        category="admissions",
        keywords="business admission requirements application",
        program_name="Business",
    )
    session = start_session(client)

    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": "John Smith, 599444555, john.knowledge@example.com business admission requirements",
            "source_domain": "alte.edu.ge",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer_source_status"] == "answered_from_approved_source"
    assert data["used_sources"]


def test_chat_does_not_answer_unsupported_tuition_exactly(client):
    session = start_session(client, language="en")

    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": "What is the tuition fee?",
            "source_domain": "alte.edu.ge",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "finance_question"
    assert data["answer_source_status"] == "no_approved_source_found"
    assert "verified information" in data["reply"]


def test_chat_marks_no_approved_source_found_for_scholarship(client):
    session = start_session(client)

    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": "Do you have scholarship details?",
            "source_domain": "alte.edu.ge",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer_source_status"] == "no_approved_source_found"
    assert data["should_handover"] is True


def test_source_backed_reply_preserves_ai_answer_and_adds_source():
    analysis = AIAnalysisResult(
        reply="International students need to submit the required application documents.",
        language="en",
        intent="international_admission",
        confidence=0.9,
        should_create_lead=False,
        should_handover=False,
        qualification=LeadQualificationResult(intent="admission_requirements"),
    )

    reply = build_source_backed_reply(analysis, ["International admissions routing - EN"])

    assert "International students need to submit" in reply
    assert "Source: International admissions routing - EN." in reply
    assert "I found verified information" not in reply


def test_program_info_without_contact_does_not_append_contact_request():
    analysis = AIAnalysisResult(
        reply="Alte offers several programs. Which program would you like to compare?",
        language="en",
        intent="admission_interest",
        confidence=0.9,
        should_create_lead=True,
        should_handover=False,
        missing_fields=["phone_or_email"],
        qualification=LeadQualificationResult(intent="program_info", recommended_next_action="ask_phone_or_email"),
    )

    apply_no_contact_lead_guard(analysis)

    assert analysis.should_create_lead is False
    assert "phone_or_email" not in analysis.missing_fields
    assert "Please share your name" not in analysis.reply
    assert analysis.qualification.recommended_next_action == "answer_or_ask_followup"
