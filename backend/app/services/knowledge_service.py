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


async def list_knowledge_sources(db: AsyncSession) -> list[KnowledgeSource]:
    return (await db.scalars(select(KnowledgeSource).order_by(KnowledgeSource.created_at.desc()))).all()


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
    program_name: str | None = None,
    approved_only: bool = True,
):
    return await retrieve_snippets(
        db,
        query=query,
        language=language,
        category=category,
        program_name=program_name,
        approved_only=approved_only,
    )
