from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeAskRequest,
    KnowledgeAskResponse,
    KnowledgeSearchResponse,
    KnowledgeReviewItem,
    KnowledgeSnippetCreate,
    KnowledgeSnippetRead,
    KnowledgeSnippetUpdate,
    KnowledgeSourceCreate,
    KnowledgeSourceRead,
    KnowledgeSourceUpdate,
    OperatorReplyKnowledgeCandidateCreate,
    OperatorReplyKnowledgeCandidateRead,
    WebsiteApprovedChunkRead,
    WebsiteSyncApproveResponse,
    WebsiteSyncDiffRead,
    WebsiteSyncPreviewRequest,
    WebsiteSyncPreviewRunRead,
    WebsiteSyncRejectResponse,
    WebsiteSyncRollbackResponse,
    WebsiteSyncSourceCreate,
    WebsiteSyncSourceRead,
)
from app.services.knowledge_service import (
    ask_knowledge_deterministic,
    approve_knowledge_snippet,
    archive_knowledge_snippet,
    create_operator_reply_knowledge_candidate,
    create_knowledge_snippet,
    create_knowledge_source,
    list_knowledge_review_queue,
    list_knowledge_sources,
    search_knowledge_snippets,
    update_knowledge_snippet,
    update_knowledge_source,
)
from app.services.website_sync_preview_service import (
    approve_website_run,
    archive_approved_website_version,
    create_website_source,
    get_website_diff,
    list_approved_website_chunks,
    list_website_runs,
    list_website_sources,
    reject_website_run,
    run_preview_sync,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
api_router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@api_router.post("/ask", response_model=KnowledgeAskResponse)
async def ask_knowledge(payload: KnowledgeAskRequest, db: AsyncSession = Depends(get_db)):
    return await ask_knowledge_deterministic(db, payload)


@api_router.post("/sync/website/sources", response_model=WebsiteSyncSourceRead)
async def create_website_sync_source(payload: WebsiteSyncSourceCreate):
    try:
        return create_website_source(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/sync/website/sources", response_model=list[WebsiteSyncSourceRead])
async def get_website_sync_sources():
    return list_website_sources()


@api_router.post("/sync/website/preview", response_model=WebsiteSyncPreviewRunRead)
async def preview_website_sync(payload: WebsiteSyncPreviewRequest):
    try:
        return run_preview_sync(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/sync/website/runs", response_model=list[WebsiteSyncPreviewRunRead])
async def get_website_sync_runs():
    return list_website_runs()


@api_router.get("/sync/website/diff/{run_id}", response_model=WebsiteSyncDiffRead)
async def get_website_sync_diff(run_id: str):
    diff = get_website_diff(run_id)
    if diff is None:
        raise HTTPException(status_code=404, detail="Website sync preview run not found")
    return diff


@api_router.post("/sync/website/approve/{run_id}", response_model=WebsiteSyncApproveResponse)
async def approve_website_sync_run(run_id: str):
    try:
        return approve_website_run(run_id, approved_by="local_admin")
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@api_router.post("/sync/website/reject/{run_id}", response_model=WebsiteSyncRejectResponse)
async def reject_website_sync_run(run_id: str):
    try:
        return reject_website_run(run_id)
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@api_router.get("/sync/website/approved", response_model=list[WebsiteApprovedChunkRead])
async def get_approved_website_sync_chunks():
    return list_approved_website_chunks()


@api_router.post("/sync/website/rollback/{version_id}", response_model=WebsiteSyncRollbackResponse)
async def rollback_website_sync_version(version_id: str):
    try:
        return archive_approved_website_version(version_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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


@router.post("/operator-reply-candidates/{message_id}", response_model=OperatorReplyKnowledgeCandidateRead)
async def create_operator_reply_candidate(
    message_id: str,
    payload: OperatorReplyKnowledgeCandidateCreate | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        candidate = await create_operator_reply_knowledge_candidate(
            db,
            message_id,
            created_by=(payload.created_by if payload else "operator"),
            category=(payload.category if payload else None),
            sensitivity=(payload.sensitivity if payload else "medium"),
            review_required=(payload.review_required if payload else True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if candidate is None:
        raise HTTPException(status_code=404, detail="Operator message not found")
    return candidate


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
