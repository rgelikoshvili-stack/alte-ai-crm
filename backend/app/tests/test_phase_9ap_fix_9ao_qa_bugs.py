from __future__ import annotations

from pathlib import Path

from app.services.chat_service import official_academic_rules_regression_reply
from app.services.knowledge_routing_service import classify_knowledge_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_CHAT = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx"
WIDGET_CHAT = PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx"
TEST_STRINGS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx"
WIDGET_STRINGS = PROJECT_ROOT / "widget" / "variants" / "pro-v2-strings.jsx"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
MOJIBAKE_MARKER = "\u00e1\u0192"
CS_QUESTION = "როდის იწყება კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია?"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def start_session(client, language: str = "ka") -> dict:
    response = client.post("/chat/session/start", json={"source_domain": "join.alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def seed_calendar_source(client) -> None:
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": "academic_calendar_geo_2025_2026",
            "title": "Academic calendar 2025-2026",
            "source_type": "pdf",
            "status": "approved",
            "language": "ka",
            "source_domain": "official_academic_rules",
            "category": "academic_rules",
            "sensitivity": "official academic rule / academic calendar",
        },
    )
    assert source.status_code == 200
    source_payload = source.json()
    snippet = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source_payload["id"],
            "source_key": source_payload["source_key"],
            "title": "Computer Science spring registration row",
            "content": (
                "კომპიუტერული მეცნიერების პროგრამების გაზაფხულის სემესტრი: "
                "აკადემიური/ადმინისტრაციული რეგისტრაცია 9 - 14 მარტი; "
                "გაზაფხულის სემესტრის დაწყება 30 მარტი."
            ),
            "category": "academic_rules",
            "source_domain": "official_academic_rules",
            "sensitivity": "official academic rule / academic calendar",
            "keywords": (
                "კომპიუტერული მეცნიერება Computer Science გაზაფხულის სემესტრი "
                "რეგისტრაცია 9 14 მარტი 30 მარტი semester start"
            ),
            "status": "approved",
            "language": "ka",
        },
    )
    assert snippet.status_code == 200


def ask(client, message: str) -> dict:
    session = start_session(client)
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_phase_9ap_computer_science_spring_registration_source_backed_answer(client):
    seed_calendar_source(client)

    payload = ask(client, CS_QUESTION)

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert payload["source_group"] == "academic_calendar_2025_2026"
    assert "9" in payload["reply"]
    assert "14" in payload["reply"]
    assert "30" in payload["reply"]
    assert "მარტ" in payload["reply"]
    assert "AI სერვისთან კავშირი შეფერხებულია" not in payload["reply"]
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def test_phase_9ap_calendar_source_routing():
    decision = classify_knowledge_route(CS_QUESTION, source_domain="join.alte.edu.ge")

    assert decision.department_id == "academic_calendar"
    assert decision.primary_source_group == "academic_calendar_2025_2026"
    assert decision.clarification_required is False


def test_phase_9ap_calendar_regression_reply_is_deterministic():
    reply = official_academic_rules_regression_reply(CS_QUESTION, "ka")

    assert reply is not None
    assert "9-14" in reply
    assert "30" in reply
    assert "მარტ" in reply
    assert "AI სერვისთან კავშირი შეფერხებულია" not in reply


def test_phase_9ap_ui_medicine_label_spacing():
    combined = "\n".join(read(path) for path in [TEST_STRINGS, WIDGET_STRINGS])

    assert "მედიცინა / MD" in combined
    assert "Medicine / MD" in combined
    assert "მედიცინა/MD" not in combined


def test_phase_9ap_contact_textarea_prefills_latest_user_question_first():
    combined = "\n".join(read(path) for path in [TEST_CHAT, WIDGET_CHAT])

    assert "latestUserText() || m.text" in combined
    assert "m.text || latestUserText()" not in combined
    assert "setLeadMessageDraft(messageText || '')" in combined
    assert "თქვენი კითხვა / შეტყობინება" in read(TEST_STRINGS)
    assert "თქვენი კითხვა / შეტყობინება" in read(WIDGET_STRINGS)
    assert MOJIBAKE_MARKER not in combined


def test_phase_9ap_safety_no_launch_no_keys_no_contact_execution():
    public = read(PUBLIC_LAUNCH).lower()
    frontend = "\n".join(read(path) for path in [TEST_CHAT, WIDGET_CHAT, TEST_STRINGS, WIDGET_STRINGS])

    assert "public_launch_decision=go" not in public
    assert "no-go" in public
    assert "api.anthropic.com" not in frontend
    assert "ANTHROPIC_API_KEY" not in frontend
    assert "sk-ant" not in frontend
    assert MOJIBAKE_MARKER not in frontend
