from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

SourceType = Literal["manual", "website_snapshot", "pdf", "faq", "policy", "program_page"]
SourceStatus = Literal["draft", "approved", "archived"]
KnowledgeLanguage = Literal["ka", "en"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class KnowledgeSourceCreate(BaseModel):
    source_key: str | None = None
    title: str
    source_type: SourceType
    status: SourceStatus = "draft"
    language: KnowledgeLanguage
    source_url: str | None = None
    source_domain: str | None = None
    category: str | None = None
    sensitivity: str | None = None
    review_required: bool = False
    stale_after_days: int | None = None
    owner: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None


class KnowledgeSourceRead(ORMModel):
    id: str
    source_key: str | None
    title: str
    source_type: str
    status: str
    language: str
    source_url: str | None
    source_domain: str | None
    category: str | None
    sensitivity: str | None
    review_required: bool
    stale_after_days: int | None
    owner: str | None
    approved_by: str | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KnowledgeSourceUpdate(BaseModel):
    source_key: str | None = None
    title: str | None = None
    source_type: SourceType | None = None
    status: SourceStatus | None = None
    language: KnowledgeLanguage | None = None
    source_url: str | None = None
    source_domain: str | None = None
    category: str | None = None
    sensitivity: str | None = None
    review_required: bool | None = None
    stale_after_days: int | None = None
    owner: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None


class KnowledgeSnippetCreate(BaseModel):
    source_id: str
    source_key: str | None = None
    title: str
    content: str
    category: str
    source_domain: str | None = None
    sensitivity: str | None = "low"
    review_required: bool = False
    stale_after_days: int | None = None
    content_hash: str | None = None
    program_name: str | None = None
    keywords: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    status: SourceStatus = "draft"
    language: KnowledgeLanguage


class KnowledgeSnippetRead(ORMModel):
    id: str
    source_id: str
    source_key: str | None
    title: str
    content: str
    category: str
    source_domain: str | None
    sensitivity: str | None
    review_required: bool
    stale_after_days: int | None
    content_hash: str | None
    program_name: str | None
    keywords: str | None
    effective_from: date | None
    effective_to: date | None
    status: str
    language: str
    created_at: datetime
    updated_at: datetime


class KnowledgeSnippetUpdate(BaseModel):
    source_key: str | None = None
    title: str | None = None
    content: str | None = None
    category: str | None = None
    source_domain: str | None = None
    sensitivity: str | None = None
    review_required: bool | None = None
    stale_after_days: int | None = None
    content_hash: str | None = None
    program_name: str | None = None
    keywords: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    status: SourceStatus | None = None
    language: KnowledgeLanguage | None = None


class KnowledgeSearchResponse(BaseModel):
    snippet: KnowledgeSnippetRead
    source: KnowledgeSourceRead
    score: int
    source_status: str
    is_stale: bool = False


class KnowledgeSearchQuery(BaseModel):
    query: str
    language: KnowledgeLanguage | None = None
    category: str | None = None
    source_domain: str | None = None
    sensitivity: str | None = None
    program_name: str | None = None
    approved_only: bool = True
    include_stale: bool = False


KnowledgeAskStatus = Literal["answered", "clarification_needed", "unsupported", "refused"]
KnowledgeAskMode = Literal["public", "internal"]


class KnowledgeAskRequest(BaseModel):
    question: str
    language: KnowledgeLanguage | None = None
    source_group: str | None = None
    program: str | None = None
    mode: KnowledgeAskMode = "public"


class KnowledgeAskResponse(BaseModel):
    answer: str
    status: KnowledgeAskStatus
    source_group: str | None = None
    public_source_label: str | None = None
    confidence: float
    clarification_options: list[str] = []
    used_claude: bool = False


WebsiteFreshnessClass = Literal["variable", "stable", "unknown"]
WebsiteSyncStatus = Literal["draft", "approved", "rejected"]
WebsiteApprovedStatus = Literal["approved", "archived"]
WebsiteSyncMode = Literal["single_url"]


class WebsiteSyncSourceCreate(BaseModel):
    name: str
    base_url: str
    allowed_paths: list[str] = []
    source_group_hint: str | None = None
    enabled: bool = True


class WebsiteSyncSourceRead(BaseModel):
    id: str
    name: str
    base_url: str
    allowed_paths: list[str] = []
    source_group_hint: str | None = None
    enabled: bool
    created_at: datetime
    updated_at: datetime
    last_preview_run_id: str | None = None
    last_preview_at: datetime | None = None


class WebsiteSyncPreviewRequest(BaseModel):
    source_id: str
    url: str
    mode: WebsiteSyncMode = "single_url"
    limit: int | None = None
    dry_run: bool = True


class WebsiteSyncChunkPreview(BaseModel):
    index: int
    text: str
    content_hash: str


class WebsiteSyncPreviewRunRead(BaseModel):
    run_id: str
    source_id: str
    status: WebsiteSyncStatus = "draft"
    source_url: str
    canonical_url: str | None = None
    page_title: str | None = None
    language: KnowledgeLanguage | Literal["unknown"] = "unknown"
    content_hash: str
    extracted_text_preview: str
    chunks_count: int
    chunks: list[WebsiteSyncChunkPreview] = []
    source_group_guess: str | None = None
    freshness_class: WebsiteFreshnessClass
    risk_flags: list[str] = []
    public_usable: bool = False
    created_at: datetime


class WebsiteSyncDiffRead(BaseModel):
    run: WebsiteSyncPreviewRunRead
    run_id: str | None = None
    source_url: str | None = None
    canonical_url: str | None = None
    page_title: str | None = None
    status: str | None = None
    detected_changes: list[str] = []
    conflicts: list[str] = []
    approval_status: str = "draft_review"
    approval_allowed: bool = False
    rejection_allowed: bool = False
    archive_available: bool = False
    risk_flags: list[str] = []
    freshness_class: WebsiteFreshnessClass | None = None
    source_group_guess: str | None = None
    public_usable: bool = False
    chunks_preview: list[WebsiteSyncChunkPreview] = []
    old_approved_content: list["WebsiteApprovedChunkRead"] = []
    added_lines: list[str] = []
    removed_lines: list[str] = []
    unchanged_summary: str | None = None
    content_hash_changed: bool = False


class WebsiteApprovedChunkRead(BaseModel):
    approved_chunk_id: str
    run_id: str
    source_id: str
    source_url: str
    canonical_url: str | None = None
    page_title: str | None = None
    language: KnowledgeLanguage | Literal["unknown"] = "unknown"
    content_hash: str
    approved_at: datetime
    approved_by: str
    version: str
    source_group: str | None = None
    freshness_class: WebsiteFreshnessClass
    priority: int = 100
    status: WebsiteApprovedStatus = "approved"
    chunk_text: str
    chunk_index: int
    risk_flags: list[str] = []
    public_usable: bool = True
    clean_source_label: str


class WebsiteSyncApproveResponse(BaseModel):
    run_id: str
    status: str
    approved_count: int
    public_usable: bool
    source_labels: list[str] = []


class WebsiteSyncRejectResponse(BaseModel):
    run_id: str
    status: str
    public_usable: bool = False


class WebsiteSyncRollbackResponse(BaseModel):
    version_id: str
    status: str
    archived_count: int
    public_usable: bool = False


class KnowledgeReviewItem(BaseModel):
    snippet: KnowledgeSnippetRead
    source: KnowledgeSourceRead
    is_stale: bool
    reasons: list[str]


class OperatorReplyKnowledgeCandidateCreate(BaseModel):
    created_by: str | None = "operator"
    category: str | None = None
    sensitivity: str | None = "medium"
    review_required: bool = True


class OperatorReplyKnowledgeCandidateRead(BaseModel):
    status: str
    created: bool
    message_id: str
    conversation_id: str
    source: KnowledgeSourceRead
    snippet: KnowledgeSnippetRead
