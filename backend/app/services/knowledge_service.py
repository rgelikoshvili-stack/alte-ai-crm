from datetime import date, datetime, timedelta
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.mock_retriever import retrieve_snippets
from app.models import Conversation, KnowledgeSnippet, KnowledgeSource, Message
from app.schemas.knowledge import KnowledgeSnippetCreate, KnowledgeSnippetUpdate, KnowledgeSourceCreate, KnowledgeSourceUpdate
from app.services.audit_service import audit_event


async def create_knowledge_source(db: AsyncSession, payload: KnowledgeSourceCreate) -> KnowledgeSource:
    source = KnowledgeSource(**payload.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


async def list_knowledge_sources(
    db: AsyncSession,
    *,
    source_key: str | None = None,
    status: str | None = None,
    source_type: str | None = None,
    category: str | None = None,
    language: str | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[KnowledgeSource]:
    query = select(KnowledgeSource).order_by(KnowledgeSource.created_at.desc())
    if not status:
        query = query.where(KnowledgeSource.status != "archived")
    if source_key:
        query = query.where(KnowledgeSource.source_key == source_key)
    if status:
        query = query.where(KnowledgeSource.status == status)
    if source_type:
        query = query.where(KnowledgeSource.source_type == source_type)
    if category:
        query = query.where(KnowledgeSource.category == category)
    if language:
        query = query.where(KnowledgeSource.language == language)
    if q:
        needle = f"%{q}%"
        query = query.where(KnowledgeSource.title.like(needle))
    return (await db.scalars(query.offset(offset).limit(limit))).all()


async def create_knowledge_snippet(db: AsyncSession, payload: KnowledgeSnippetCreate) -> KnowledgeSnippet:
    snippet = KnowledgeSnippet(**payload.model_dump())
    db.add(snippet)
    await db.commit()
    await db.refresh(snippet)
    return snippet


async def create_operator_reply_knowledge_candidate(
    db: AsyncSession,
    message_id: str,
    *,
    created_by: str | None = "operator",
    category: str | None = None,
    sensitivity: str | None = "medium",
    review_required: bool = True,
) -> dict | None:
    message = await db.get(Message, message_id)
    if message is None:
        return None
    if message.sender_type != "operator":
        raise ValueError("Only operator replies can become knowledge candidates")
    conversation = await db.get(Conversation, message.conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    source_key = f"operator_reply:{message.id}"
    existing_source = await db.scalar(select(KnowledgeSource).where(KnowledgeSource.source_key == source_key))
    if existing_source:
        existing_snippet = await db.scalar(select(KnowledgeSnippet).where(KnowledgeSnippet.source_id == existing_source.id))
        if existing_snippet is None:
            raise ValueError("Existing source has no candidate snippet")
        return {
            "status": "operator_reply_knowledge_candidate_exists",
            "created": False,
            "message_id": message.id,
            "conversation_id": conversation.id,
            "source": existing_source,
            "snippet": existing_snippet,
        }

    previous_user_message = await find_previous_user_message(db, message)
    language = normalize_candidate_language(conversation.language, message.text)
    metadata = previous_user_message.metadata_json if previous_user_message and previous_user_message.metadata_json else {}
    source_domain = metadata.get("source_domain")
    selected_department = metadata.get("selected_department")
    selected_topic = metadata.get("selected_topic")
    candidate_category = category or selected_department or "operator_answer"
    question = previous_user_message.text if previous_user_message else "Operator answer without matching visitor question"
    title = truncate_text(f"Operator answer candidate: {question}", 255)
    content = f"Visitor question:\n{question}\n\nOperator answer:\n{message.text}"

    source = KnowledgeSource(
        source_key=source_key,
        title=title,
        source_type="faq",
        status="draft",
        language=language,
        source_url=None,
        source_domain=source_domain,
        category=candidate_category,
        sensitivity=sensitivity,
        review_required=review_required,
        owner=created_by,
    )
    db.add(source)
    await db.flush()
    snippet = KnowledgeSnippet(
        source_id=source.id,
        source_key=source_key,
        title=title,
        content=content,
        category=candidate_category,
        source_domain=source_domain,
        sensitivity=sensitivity,
        review_required=review_required,
        stale_after_days=90,
        content_hash=sha256(content.encode("utf-8")).hexdigest(),
        program_name=selected_topic,
        keywords=build_candidate_keywords(question, message.text, selected_department, selected_topic),
        status="draft",
        language=language,
    )
    db.add(snippet)
    await db.flush()
    await audit_event(
        db,
        action="operator_reply_knowledge_candidate_created",
        entity_type="knowledge_snippet",
        entity_id=snippet.id,
        actor_type="operator",
        actor_id=created_by,
        metadata_json={
            "conversation_id": conversation.id,
            "message_id": message.id,
            "source_id": source.id,
            "selected_department": selected_department,
            "selected_topic": selected_topic,
        },
    )
    await db.commit()
    await db.refresh(source)
    await db.refresh(snippet)
    return {
        "status": "operator_reply_knowledge_candidate_created",
        "created": True,
        "message_id": message.id,
        "conversation_id": conversation.id,
        "source": source,
        "snippet": snippet,
    }


async def update_knowledge_source(
    db: AsyncSession,
    source_id: str,
    payload: KnowledgeSourceUpdate,
) -> KnowledgeSource | None:
    source = await db.get(KnowledgeSource, source_id)
    if source is None:
        return None
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(source, field, value)
    await audit_event(
        db,
        action="knowledge_source_updated",
        entity_type="knowledge_source",
        entity_id=source.id,
        metadata_json={"changed_fields": sorted(changes.keys())},
    )
    await db.commit()
    await db.refresh(source)
    return source


async def update_knowledge_snippet(
    db: AsyncSession,
    snippet_id: str,
    payload: KnowledgeSnippetUpdate,
) -> KnowledgeSnippet | None:
    snippet = await db.get(KnowledgeSnippet, snippet_id)
    if snippet is None:
        return None
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(snippet, field, value)
    await audit_event(
        db,
        action="knowledge_snippet_updated",
        entity_type="knowledge_snippet",
        entity_id=snippet.id,
        metadata_json={"changed_fields": sorted(changes.keys())},
    )
    await db.commit()
    await db.refresh(snippet)
    return snippet


async def approve_knowledge_snippet(
    db: AsyncSession,
    snippet_id: str,
    *,
    approved_by: str | None = "knowledge-admin",
) -> KnowledgeSnippet | None:
    snippet = await db.get(KnowledgeSnippet, snippet_id)
    if snippet is None:
        return None
    snippet.status = "approved"
    snippet.review_required = False
    source = await db.get(KnowledgeSource, snippet.source_id)
    if source and source.status == "draft":
        source.status = "approved"
        source.approved_by = approved_by
        source.approved_at = datetime.now().astimezone()
    await audit_event(
        db,
        action="knowledge_snippet_approved",
        entity_type="knowledge_snippet",
        entity_id=snippet.id,
        metadata_json={"source_id": snippet.source_id, "approved_by": approved_by},
    )
    await db.commit()
    await db.refresh(snippet)
    return snippet


async def archive_knowledge_snippet(db: AsyncSession, snippet_id: str) -> KnowledgeSnippet | None:
    snippet = await db.get(KnowledgeSnippet, snippet_id)
    if snippet is None:
        return None
    snippet.status = "archived"
    await audit_event(
        db,
        action="knowledge_snippet_archived",
        entity_type="knowledge_snippet",
        entity_id=snippet.id,
        metadata_json={"source_id": snippet.source_id},
    )
    await db.commit()
    await db.refresh(snippet)
    return snippet


async def list_knowledge_review_queue(
    db: AsyncSession,
    *,
    status: str | None = None,
    category: str | None = None,
    language: str | None = None,
    sensitivity: str | None = None,
    review_required: bool | None = None,
    stale: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    rows = (
        await db.execute(
            select(KnowledgeSnippet, KnowledgeSource)
            .join(KnowledgeSource, KnowledgeSnippet.source_id == KnowledgeSource.id)
            .where(KnowledgeSource.status != "archived")
            .order_by(KnowledgeSnippet.updated_at.desc())
        )
    ).all()
    items: list[dict] = []
    today = date.today()
    for snippet, source in rows:
        if not status and snippet.status == "archived":
            continue
        if status and snippet.status != status and source.status != status:
            continue
        if category and snippet.category != category and source.category != category:
            continue
        if language and snippet.language != language:
            continue
        if sensitivity and sensitivity not in {snippet.sensitivity, source.sensitivity}:
            continue
        item_stale = is_stale(snippet, today)
        if stale is not None and item_stale is not stale:
            continue
        item_review_required = bool(snippet.review_required or source.review_required)
        if review_required is not None and item_review_required is not review_required:
            continue
        reasons = review_reasons(snippet, source, item_stale)
        if not reasons:
            continue
        items.append({"snippet": snippet, "source": source, "is_stale": item_stale, "reasons": reasons})
    return items[offset : offset + limit]


async def search_knowledge_snippets(
    db: AsyncSession,
    *,
    query: str,
    language: str | None = None,
    category: str | None = None,
    source_domain: str | None = None,
    sensitivity: str | None = None,
    program_name: str | None = None,
    approved_only: bool = True,
    include_stale: bool = False,
    limit: int = 10,
):
    return await retrieve_snippets(
        db,
        query=query,
        language=language,
        category=category,
        source_domain=source_domain,
        sensitivity=sensitivity,
        program_name=program_name,
        approved_only=approved_only,
        include_stale=include_stale,
        limit=limit,
    )


def review_reasons(snippet: KnowledgeSnippet, source: KnowledgeSource, stale: bool) -> list[str]:
    reasons: list[str] = []
    if snippet.status != "approved":
        reasons.append(f"snippet_status_{snippet.status}")
    if source.status != "approved":
        reasons.append(f"source_status_{source.status}")
    if snippet.review_required or source.review_required:
        reasons.append("review_required")
    if stale:
        reasons.append("source_stale")
    if "high" in {snippet.sensitivity, source.sensitivity}:
        reasons.append("high_sensitivity")
    return reasons


def is_stale(snippet: KnowledgeSnippet, today: date) -> bool:
    if snippet.effective_to and snippet.effective_to < today:
        return True
    if snippet.stale_after_days is None:
        return False
    baseline = snippet.effective_from or as_date(snippet.updated_at) or as_date(snippet.created_at)
    return bool(baseline and baseline + timedelta(days=snippet.stale_after_days) < today)


def as_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


async def find_previous_user_message(db: AsyncSession, operator_message: Message) -> Message | None:
    return await db.scalar(
        select(Message)
        .where(
            Message.conversation_id == operator_message.conversation_id,
            Message.sender_type == "user",
            Message.created_at <= operator_message.created_at,
        )
        .order_by(Message.created_at.desc())
    )


def normalize_candidate_language(conversation_language: str | None, text: str) -> str:
    if conversation_language in {"ka", "en"}:
        return conversation_language
    return "ka" if any("\u10a0" <= char <= "\u10ff" for char in text) else "en"


def truncate_text(value: str, limit: int) -> str:
    compact = " ".join(value.split())
    return compact if len(compact) <= limit else f"{compact[: limit - 3]}..."


def build_candidate_keywords(
    question: str,
    answer: str,
    selected_department: str | None,
    selected_topic: str | None,
) -> str:
    words = [selected_department, selected_topic]
    for text in [question, answer]:
        words.extend(word.strip(".,!?;:()[]{}\"'").lower() for word in text.split()[:24])
    unique = []
    for word in words:
        if word and word not in unique:
            unique.append(word)
    return ", ".join(unique[:32])
