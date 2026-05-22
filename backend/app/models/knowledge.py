from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.crm import TimestampMixin, utc_now, uuid_str


class KnowledgeSource(TimestampMixin, Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    source_key: Mapped[str | None] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="draft", nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    source_domain: Mapped[str | None] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(120), index=True)
    sensitivity: Mapped[str | None] = mapped_column(String(32))
    review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stale_after_days: Mapped[int | None] = mapped_column(Integer)
    owner: Mapped[str | None] = mapped_column(String(255))
    approved_by: Mapped[str | None] = mapped_column(String(255))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class KnowledgeSnippet(TimestampMixin, Base):
    __tablename__ = "knowledge_snippets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    source_key: Mapped[str | None] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    source_domain: Mapped[str | None] = mapped_column(String(255), index=True)
    sensitivity: Mapped[str | None] = mapped_column(String(32), default="low")
    review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stale_after_days: Mapped[int | None] = mapped_column(Integer)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    program_name: Mapped[str | None] = mapped_column(String(255))
    keywords: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(64), default="draft", nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)


class RetrievalResult:
    def __init__(
        self,
        snippet: KnowledgeSnippet,
        source: KnowledgeSource,
        score: int,
        source_status: str,
        is_stale: bool = False,
    ):
        self.snippet = snippet
        self.source = source
        self.score = score
        self.source_status = source_status
        self.is_stale = is_stale
