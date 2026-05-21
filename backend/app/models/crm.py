from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def uuid_str() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    default_queue: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(64), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    country: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120))
    source_channel: Mapped[str | None] = mapped_column(String(64))
    consent_status: Mapped[str | None] = mapped_column(String(64))

    leads: Mapped[list["Lead"]] = relationship(back_populates="customer")


class Pipeline(TimestampMixin, Base):
    __tablename__ = "pipelines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PipelineStage(TimestampMixin, Base):
    __tablename__ = "pipeline_stages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    pipeline_id: Mapped[str] = mapped_column(ForeignKey("pipelines.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_lost: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    interest_area: Mapped[str | None] = mapped_column(String(255))
    program: Mapped[str | None] = mapped_column(String(255))
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    assigned_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    stage_id: Mapped[str | None] = mapped_column(ForeignKey("pipeline_stages.id"))
    status: Mapped[str] = mapped_column(String(64), default="new", nullable=False)
    priority: Mapped[str] = mapped_column(String(64), default="normal", nullable=False)
    source_channel: Mapped[str | None] = mapped_column(String(64))
    source_domain: Mapped[str | None] = mapped_column(String(255))
    campaign_tag: Mapped[str | None] = mapped_column(String(255))
    is_international_priority: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    medical_track: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    intake_period: Mapped[str | None] = mapped_column(String(64))
    relocation_needed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="leads")


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), index=True)
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id"), index=True)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="open", nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="unknown", nullable=False)
    ai_handled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    human_handover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(64), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    channel_message_id: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id"), index=True)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), index=True)
    assigned_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    priority: Mapped[str] = mapped_column(String(64), default="normal", nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="open", nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class LeadStageHistory(Base):
    __tablename__ = "lead_stage_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False, index=True)
    from_stage_id: Mapped[str | None] = mapped_column(ForeignKey("pipeline_stages.id"))
    to_stage_id: Mapped[str | None] = mapped_column(ForeignKey("pipeline_stages.id"))
    changed_by: Mapped[str | None] = mapped_column(String(36))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    actor_type: Mapped[str] = mapped_column(String(64), nullable=False, default="system")
    actor_id: Mapped[str | None] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class DeadlineTracking(TimestampMixin, Base):
    __tablename__ = "deadline_tracking"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    deadline_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    deadline_date: Mapped[date] = mapped_column(Date, nullable=False)
    program: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(36))
