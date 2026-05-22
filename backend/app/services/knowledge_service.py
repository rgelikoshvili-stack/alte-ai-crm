from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.mock_retriever import retrieve_snippets
from app.models import KnowledgeSnippet, KnowledgeSource
from app.schemas.knowledge import KnowledgeSnippetCreate, KnowledgeSourceCreate


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
    query = select(KnowledgeSource).where(KnowledgeSource.status != "archived").order_by(KnowledgeSource.created_at.desc())
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
