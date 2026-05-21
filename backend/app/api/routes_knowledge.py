from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeSearchResponse,
    KnowledgeSnippetCreate,
    KnowledgeSnippetRead,
    KnowledgeSourceCreate,
    KnowledgeSourceRead,
)
from app.services.knowledge_service import (
    create_knowledge_snippet,
    create_knowledge_source,
    list_knowledge_sources,
    search_knowledge_snippets,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/sources", response_model=KnowledgeSourceRead)
async def create_source(payload: KnowledgeSourceCreate, db: AsyncSession = Depends(get_db)):
    return await create_knowledge_source(db, payload)


@router.get("/sources", response_model=list[KnowledgeSourceRead])
async def get_sources(db: AsyncSession = Depends(get_db)):
    return await list_knowledge_sources(db)


@router.post("/snippets", response_model=KnowledgeSnippetRead)
async def create_snippet(payload: KnowledgeSnippetCreate, db: AsyncSession = Depends(get_db)):
    return await create_knowledge_snippet(db, payload)


@router.get("/snippets/search", response_model=list[KnowledgeSearchResponse])
async def search_snippets(
    query: str,
    language: str | None = None,
    category: str | None = None,
    program_name: str | None = None,
    approved_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    results = await search_knowledge_snippets(
        db,
        query=query,
        language=language,
        category=category,
        program_name=program_name,
        approved_only=approved_only,
    )
    return [
        {"snippet": item.snippet, "source": item.source, "score": item.score, "source_status": item.source_status}
        for item in results
    ]
