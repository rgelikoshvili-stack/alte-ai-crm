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
async def get_sources(
    source_key: str | None = None,
    status: str | None = None,
    source_type: str | None = None,
    category: str | None = None,
    language: str | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await list_knowledge_sources(
        db,
        source_key=source_key,
        status=status,
        source_type=source_type,
        category=category,
        language=language,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.post("/snippets", response_model=KnowledgeSnippetRead)
async def create_snippet(payload: KnowledgeSnippetCreate, db: AsyncSession = Depends(get_db)):
    return await create_knowledge_snippet(db, payload)


@router.get("/snippets/search", response_model=list[KnowledgeSearchResponse])
async def search_snippets(
    q: str | None = None,
    query: str | None = None,
    language: str | None = None,
    category: str | None = None,
    source_domain: str | None = None,
    sensitivity: str | None = None,
    program: str | None = None,
    program_name: str | None = None,
    approved_only: bool = True,
    include_stale: bool = False,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    results = await search_knowledge_snippets(
        db,
        query=q or query or "",
        language=language,
        category=category,
        source_domain=source_domain,
        sensitivity=sensitivity,
        program_name=program or program_name,
        approved_only=approved_only,
        include_stale=include_stale,
        limit=limit,
    )
    return [
        {
            "snippet": item.snippet,
            "source": item.source,
            "score": item.score,
            "source_status": item.source_status,
            "is_stale": item.is_stale,
        }
        for item in results
    ]
