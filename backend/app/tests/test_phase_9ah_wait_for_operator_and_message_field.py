from __future__ import annotations

import asyncio
import importlib
import re
import subprocess
from pathlib import Path

from sqlalchemy import select

from app.models import Conversation, Customer, Lead, Message, Task


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_CHAT = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx"
TEST_MODALS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx"
TEST_STRINGS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx"
WIDGET_CHAT = PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx"
WIDGET_MODALS = PROJECT_ROOT / "widget" / "variants" / "pro-v2-modals.jsx"
WIDGET_STRINGS = PROJECT_ROOT / "widget" / "variants" / "pro-v2-strings.jsx"
BRIDGE = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
CHAT_SCHEMA = PROJECT_ROOT / "backend" / "app" / "schemas" / "chat.py"
CHAT_SERVICE = PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py"
OPERATOR_FRONTEND = PROJECT_ROOT / "frontend" / "app.js"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AH_WAIT_FOR_OPERATOR_AND_MESSAGE_FIELD_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def test_contact_modal_contains_question_message_textarea_labels() -> None:
    text = "\n".join(read(path) for path in [TEST_MODALS, TEST_STRINGS, WIDGET_MODALS, WIDGET_STRINGS])
    assert "თქვენი კითხვა / შეტყობინება" in text
    assert "Your question / message" in text
    assert "დაწერეთ თქვენი კითხვა ან მოკლე ტექსტი ოპერატორისთვის..." in text
    assert "Write your question or message for the operator..." in text
    assert "<textarea" in text
    assert "leadMessage" in text


def test_contact_payload_includes_message_field() -> None:
    text = "\n".join(read(path) for path in [TEST_MODALS, TEST_CHAT, WIDGET_MODALS, WIDGET_CHAT, BRIDGE, CHAT_SCHEMA])
    assert "message:" in text
    assert "message: contact?.message" in text
    assert "message: data.message || data.question || data.note || null" in text
    assert "message: str | None = None" in read(CHAT_SCHEMA)
    assert "question: str | None = None" in read(CHAT_SCHEMA)
    assert "note: str | None = None" in read(CHAT_SCHEMA)


def test_wait_for_operator_action_text_exists_in_ka_and_en() -> None:
    text = "\n".join(read(path) for path in [TEST_STRINGS, WIDGET_STRINGS, TEST_CHAT, WIDGET_CHAT])
    assert "დაელოდე ოპერატორს" in text
    assert "Wait for operator" in text
    assert "waiting_for_operator" in text
    assert "თქვენი მოთხოვნა გადაეცა ოპერატორს" in text
    assert "Your request has been sent to an operator" in text


def test_unsupported_answer_copy_exists_in_ka_and_en() -> None:
    text = read(CHAT_SERVICE)
    assert "ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე" in text
    assert "შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან" in text
    assert "I couldn't find an exact answer in the approved official sources" in text
    assert "I can connect you with the relevant operator" in text


def test_backend_waiting_handover_accepts_no_contact_without_creating_crm_records(client, session_factory) -> None:
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()
    response = client.post(
        f"/chat/handover/{session['conversation_id']}",
        json={
            "session_id": session["session_id"],
            "selected_department": "finance",
            "selected_topic": "tuition",
            "language": "ka",
            "source_domain": "alte.edu.ge",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": "სწავლის საფასურის გადახდის გრაფიკი მაინტერესებს",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "waiting_for_operator"
    assert payload["task_id"] is None
    conversations = fetch_all(session_factory, select(Conversation))
    assert conversations[0].status == "waiting_for_operator"
    assert conversations[0].human_handover is True
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []
    messages = fetch_all(session_factory, select(Message))
    assert any("გადახდის გრაფიკი" in message.text for message in messages)


def test_operator_inbox_exposes_waiting_status_and_department(client) -> None:
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()
    client.post(
        f"/chat/handover/{session['conversation_id']}",
        json={
            "session_id": session["session_id"],
            "selected_department": "library",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": "ბიბლიოთეკის რესურსები როგორ გამოვიყენო?",
        },
    )

    rows = client.get("/inbox", params={"human_handover": "true"}).json()
    item = next(row for row in rows if row["conversation_id"] == session["conversation_id"])
    assert item["status"] == "waiting_for_operator"
    assert item["waiting_status"] == "waiting_for_operator"
    assert item["selected_department"] == "library"
    assert "ბიბლიოთეკის რესურსები" in item["last_message_text"]


def test_operator_frontend_displays_waiting_badge_and_department() -> None:
    text = read(OPERATOR_FRONTEND)
    assert "Waiting for operator" in text
    assert "selected_department" in text
    assert "waiting_status" in text
    assert "Conversation ID" in text


def test_no_direct_phone_email_name_request_in_unsupported_copy() -> None:
    text = read(CHAT_SERVICE)
    no_source_fn = text[text.index("def build_no_source_reply") : text.index("def is_ambiguous_program_question")]
    forbidden = ["phone", "email", "name", "ტელეფონი", "ელ.ფოსტა", "სახელი"]
    assert not [word for word in forbidden if word.lower() in no_source_fn.lower()]


def test_public_launch_remains_no_go_and_no_mojibake() -> None:
    text = "\n".join(
        read(path)
        for path in [
            TEST_CHAT,
            TEST_MODALS,
            TEST_STRINGS,
            WIDGET_CHAT,
            WIDGET_MODALS,
            WIDGET_STRINGS,
            BRIDGE,
            CHAT_SERVICE,
            PUBLIC_LAUNCH,
        ]
    )
    assert "áƒ" not in text
    lowered = read(PUBLIC_LAUNCH).lower()
    assert "public_launch_decision=go" not in lowered
    assert "public launch: go" not in lowered
    assert "no-go" in lowered


def test_verifier_and_smoke_importability() -> None:
    verifier = importlib.import_module("app.scripts.verify_phase_9ah_wait_for_operator_and_message_field")
    smoke = importlib.import_module("app.scripts.production_phase_9ah_wait_for_operator_smoke")
    assert hasattr(verifier, "run_checks")
    assert hasattr(smoke, "main")


def test_env_and_local_secrets_not_tracked() -> None:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
