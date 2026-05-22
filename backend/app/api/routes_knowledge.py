from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeSearchResponse,
    KnowledgeReviewItem,
    KnowledgeSnippetCreate,
    KnowledgeSnippetRead,
    KnowledgeSnippetUpdate,
    KnowledgeSourceCreate,
    KnowledgeSourceRead,
    KnowledgeSourceUpdate,
)
from app.services.knowledge_service import (
    approve_knowledge_snippet,
    archive_knowledge_snippet,
    create_knowledge_snippet,
    create_knowledge_source,
    list_knowledge_review_queue,
    list_knowledge_sources,
    search_knowledge_snippets,
    update_knowledge_snippet,
    update_knowledge_source,
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


@router.patch("/sources/{source_id}", response_model=KnowledgeSourceRead)
async def patch_source(source_id: str, payload: KnowledgeSourceUpdate, db: AsyncSession = Depends(get_db)):
    source = await update_knowledge_source(db, source_id, payload)
    if source is None:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return source


@router.post("/snippets", response_model=KnowledgeSnippetRead)
async def create_snippet(payload: KnowledgeSnippetCreate, db: AsyncSession = Depends(get_db)):
    return await create_knowledge_snippet(db, payload)


@router.get("/review-queue", response_model=list[KnowledgeReviewItem])
async def review_queue(
    status: str | None = None,
    category: str | None = None,
    language: str | None = None,
    sensitivity: str | None = None,
    review_required: bool | None = None,
    stale: bool | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await list_knowledge_review_queue(
        db,
        status=status,
        category=category,
        language=language,
        sensitivity=sensitivity,
        review_required=review_required,
        stale=stale,
        limit=limit,
        offset=offset,
    )


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


@router.patch("/snippets/{snippet_id}", response_model=KnowledgeSnippetRead)
async def patch_snippet(snippet_id: str, payload: KnowledgeSnippetUpdate, db: AsyncSession = Depends(get_db)):
    snippet = await update_knowledge_snippet(db, snippet_id, payload)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Knowledge snippet not found")
    return snippet


@router.patch("/snippets/{snippet_id}/approve", response_model=KnowledgeSnippetRead)
async def approve_snippet(snippet_id: str, approved_by: str | None = "knowledge-admin", db: AsyncSession = Depends(get_db)):
    snippet = await approve_knowledge_snippet(db, snippet_id, approved_by=approved_by)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Knowledge snippet not found")
    return snippet


@router.patch("/snippets/{snippet_id}/archive", response_model=KnowledgeSnippetRead)
async def archive_snippet(snippet_id: str, db: AsyncSession = Depends(get_db)):
    snippet = await archive_knowledge_snippet(db, snippet_id)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Knowledge snippet not found")
    return snippet
