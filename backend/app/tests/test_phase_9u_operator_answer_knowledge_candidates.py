import asyncio
import importlib
from pathlib import Path

from sqlalchemy import select

from app.models import Conversation, KnowledgeSnippet, KnowledgeSource, Message
from app.schemas.crm import ConversationCreate, MessageCreate
from app.services.conversation_service import create_conversation, create_message

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def test_phase_9u_verifier_importability():
    module = importlib.import_module("app.scripts.verify_phase_9u_operator_answer_knowledge_candidates")
    assert hasattr(module, "run_checks")


def test_operator_reply_candidate_creates_draft_review_required_source_and_snippet(client, session_factory):
    async def seed_conversation():
        async with session_factory() as db:
            conversation = await create_conversation(
                db,
                ConversationCreate(channel="website_chat", language="ka", human_handover=True),
            )
            user_message = await create_message(
                db,
                conversation.id,
                MessageCreate(
                    sender_type="user",
                    text="რა ღირს სწავლა?",
                    metadata_json={
                        "source_domain": "alte.edu.ge",
                        "selected_department": "finance",
                        "selected_topic": "tuition",
                    },
                ),
            )
            operator_message = await create_message(
                db,
                conversation.id,
                MessageCreate(sender_type="operator", text="ზუსტი საფასური უნდა დადასტურდეს ფინანსურ სამსახურთან."),
            )
            return conversation.id, user_message.id, operator_message.id

    conversation_id, _user_id, operator_message_id = asyncio.run(seed_conversation())

    response = client.post(
        f"/knowledge/operator-reply-candidates/{operator_message_id}",
        json={"created_by": "operator-test"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operator_reply_knowledge_candidate_created"
    assert data["created"] is True
    assert data["conversation_id"] == conversation_id
    assert data["source"]["status"] == "draft"
    assert data["source"]["review_required"] is True
    assert data["source"]["source_type"] == "faq"
    assert data["source"]["category"] == "finance"
    assert data["snippet"]["status"] == "draft"
    assert data["snippet"]["review_required"] is True
    assert data["snippet"]["source_domain"] == "alte.edu.ge"
    assert "რა ღირს სწავლა?" in data["snippet"]["content"]
    assert "ზუსტი საფასური" in data["snippet"]["content"]

    review_queue = client.get("/knowledge/review-queue?review_required=true").json()
    assert any(item["snippet"]["id"] == data["snippet"]["id"] for item in review_queue)

    sources = fetch_all(session_factory, select(KnowledgeSource))
    snippets = fetch_all(session_factory, select(KnowledgeSnippet))
    assert len(sources) == 1
    assert len(snippets) == 1


def test_operator_reply_candidate_is_idempotent(client, session_factory):
    async def seed_operator_reply():
        async with session_factory() as db:
            conversation = await create_conversation(db, ConversationCreate(channel="website_chat", language="en"))
            await create_message(
                db,
                conversation.id,
                MessageCreate(
                    sender_type="user",
                    text="What documents do international students need?",
                    metadata_json={"source_domain": "join.alte.edu.ge", "selected_department": "international"},
                ),
            )
            operator_message = await create_message(
                db,
                conversation.id,
                MessageCreate(sender_type="operator", text="Please verify the latest document checklist before sharing."),
            )
            return operator_message.id

    operator_message_id = asyncio.run(seed_operator_reply())

    first = client.post(f"/knowledge/operator-reply-candidates/{operator_message_id}", json={})
    second = client.post(f"/knowledge/operator-reply-candidates/{operator_message_id}", json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["snippet"]["id"] == second.json()["snippet"]["id"]
    assert second.json()["created"] is False
    assert len(fetch_all(session_factory, select(KnowledgeSource))) == 1
    assert len(fetch_all(session_factory, select(KnowledgeSnippet))) == 1


def test_operator_reply_candidate_rejects_non_operator_message(client, session_factory):
    async def seed_user_message():
        async with session_factory() as db:
            conversation = await create_conversation(db, ConversationCreate(channel="website_chat", language="en"))
            message = await create_message(
                db,
                conversation.id,
                MessageCreate(sender_type="user", text="Can I talk to an operator?"),
            )
            return message.id

    user_message_id = asyncio.run(seed_user_message())
    response = client.post(f"/knowledge/operator-reply-candidates/{user_message_id}", json={})

    assert response.status_code == 400
    assert "Only operator replies" in response.json()["detail"]


def test_phase_9u_docs_keep_learning_review_gated_and_launch_no_go():
    text = "\n".join(
        (PROJECT_ROOT / path).read_text(encoding="utf-8").lower()
        for path in [
            "docs/deployment/PHASE_9U_OPERATOR_ANSWER_KNOWLEDGE_CANDIDATES_RESULT.md",
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
    )
    assert "operator_answers_to_draft_review_queue_ready" in text
    assert "automatic learning from operator replies: no" in text
    assert "public_launch_decision=go" not in text
    assert "public launch complete" not in text


def test_phase_9u_no_frontend_provider_secrets():
    text = "\n".join(
        (PROJECT_ROOT / path).read_text(encoding="utf-8")
        for path in [
            "frontend/app.js",
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "widget/variants/pro-v2-modals.jsx",
        ]
    )
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL"]:
        assert forbidden not in text


def test_phase_9u_operator_ui_has_knowledge_candidate_action():
    text = (PROJECT_ROOT / "frontend/app.js").read_text(encoding="utf-8")
    assert "/knowledge/operator-reply-candidates/" in text
    assert "source_key: `operator_reply:${messageId}`" in text
    assert "knowledge-candidate-btn" in text
    assert "open-knowledge-candidate-btn" in text
    assert "candidate-status" in text
    assert "Create knowledge candidate" in text
    assert "Open review" in text
    assert "showOperatorAnswerDrafts" in text
    assert "approveKnowledgeSnippet" in text
    assert "archiveKnowledgeSnippet" in text
    assert "saveKnowledgeSnippetDraft" in text
    assert "knowledge-edit-textarea" in text
    assert "knowledge-meta-grid" in text
    assert "snippet-category-" in text
    assert "snippet-sensitivity-" in text
    assert "snippet-language-" in text
    assert "/knowledge/sources/${sourceId}" in text
    assert "Save draft" in text
    assert "/knowledge/snippets/${snippetId}" in text
    assert "renderKnowledgeReviewItem" in text
    assert "/knowledge/review-queue" in text
    assert "operatorKnowledgeFilterBtn" in (PROJECT_ROOT / "frontend/index.html").read_text(encoding="utf-8")
