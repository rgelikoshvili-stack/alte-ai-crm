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
