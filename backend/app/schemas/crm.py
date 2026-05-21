from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

UserRole = Literal[
    "admin",
    "manager",
    "admissions_user",
    "international_admissions_user",
    "finance_user",
    "student_services_user",
    "operator",
]
LeadStatus = Literal["new", "open", "in_progress", "won", "lost", "closed"]
Priority = Literal["low", "normal", "high", "urgent"]
Channel = Literal["website_chat", "whatsapp", "messenger", "instagram", "email", "manual"]
Language = Literal["ka", "en", "unknown"]
SenderType = Literal["user", "ai", "operator", "system"]
TaskStatus = Literal["open", "in_progress", "completed", "cancelled"]
DeadlineType = Literal["enrollment", "exam", "grant", "event", "academic_calendar", "other"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None
    default_queue: str | None = None
    is_active: bool = True


class DepartmentRead(ORMModel):
    id: str
    name: str
    description: str | None
    default_queue: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CustomerCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    country: str | None = None
    city: str | None = None
    source_channel: Channel | None = None
    consent_status: str | None = None


class CustomerRead(ORMModel):
    id: str
    first_name: str | None
    last_name: str | None
    phone: str | None
    email: str | None
    country: str | None
    city: str | None
    source_channel: str | None
    consent_status: str | None
    created_at: datetime
    updated_at: datetime


class PipelineCreate(BaseModel):
    name: str
    department_id: str | None = None
    is_active: bool = True


class PipelineRead(ORMModel):
    id: str
    name: str
    department_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PipelineStageCreate(BaseModel):
    pipeline_id: str
    name: str
    order: int
    is_final: bool = False
    is_lost: bool = False


class PipelineStageRead(ORMModel):
    id: str
    pipeline_id: str
    name: str
    order: int
    is_final: bool
    is_lost: bool
    created_at: datetime
    updated_at: datetime


class LeadCreate(BaseModel):
    customer_id: str
    interest_area: str | None = None
    program: str | None = None
    department_id: str | None = None
    assigned_user_id: str | None = None
    stage_id: str | None = None
    status: LeadStatus = "new"
    priority: Priority = "normal"
    source_channel: Channel | None = None
    source_domain: Literal["alte.edu.ge", "join.alte.edu.ge"] | None = None
    campaign_tag: str | None = None
    is_international_priority: bool = False
    medical_track: bool = False
    intake_period: str | None = None
    relocation_needed: bool = False
    qualification_intent: str | None = None
    urgency: str | None = None
    lead_score: int | None = None
    qualification_status: str | None = None
    handover_required: bool = False
    handover_reason: str | None = None
    recommended_next_action: str | None = None


class LeadUpdate(BaseModel):
    interest_area: str | None = None
    program: str | None = None
    department_id: str | None = None
    assigned_user_id: str | None = None
    status: LeadStatus | None = None
    priority: Priority | None = None
    campaign_tag: str | None = None
    is_international_priority: bool | None = None
    medical_track: bool | None = None
    intake_period: str | None = None
    relocation_needed: bool | None = None
    qualification_intent: str | None = None
    urgency: str | None = None
    lead_score: int | None = None
    qualification_status: str | None = None
    handover_required: bool | None = None
    handover_reason: str | None = None
    recommended_next_action: str | None = None


class LeadStageChange(BaseModel):
    stage_id: str | None
    changed_by: str | None = None


class LeadRead(ORMModel):
    id: str
    customer_id: str
    interest_area: str | None
    program: str | None
    department_id: str | None
    assigned_user_id: str | None
    stage_id: str | None
    status: str
    priority: str
    source_channel: str | None
    source_domain: str | None
    campaign_tag: str | None
    is_international_priority: bool
    medical_track: bool
    intake_period: str | None
    relocation_needed: bool
    qualification_intent: str | None
    urgency: str | None
    lead_score: int | None
    qualification_status: str | None
    handover_required: bool
    handover_reason: str | None
    recommended_next_action: str | None
    created_at: datetime
    updated_at: datetime


class ConversationCreate(BaseModel):
    customer_id: str | None = None
    lead_id: str | None = None
    channel: Channel
    status: str = "open"
    language: Language = "unknown"
    ai_handled: bool = False
    human_handover: bool = False
    summary: str | None = None


class ConversationRead(ORMModel):
    id: str
    customer_id: str | None
    lead_id: str | None
    channel: str
    status: str
    language: str
    ai_handled: bool
    human_handover: bool
    summary: str | None
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    sender_type: SenderType
    text: str
    channel_message_id: str | None = None
    metadata_json: dict[str, Any] | None = None


class MessageRead(ORMModel):
    id: str
    conversation_id: str
    sender_type: str
    text: str
    channel_message_id: str | None
    metadata_json: dict[str, Any] | None
    created_at: datetime


class InboxItem(BaseModel):
    conversation: ConversationRead
    customer: CustomerRead | None
    lead: LeadRead | None
    last_message: MessageRead | None


class TaskCreate(BaseModel):
    lead_id: str | None = None
    customer_id: str | None = None
    assigned_user_id: str | None = None
    department_id: str | None = None
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: Priority = "normal"
    status: TaskStatus = "open"


class TaskUpdate(BaseModel):
    assigned_user_id: str | None = None
    department_id: str | None = None
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None


class TaskRead(ORMModel):
    id: str
    lead_id: str | None
    customer_id: str | None
    assigned_user_id: str | None
    department_id: str | None
    title: str
    description: str | None
    due_date: datetime | None
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class LeadStageHistoryRead(ORMModel):
    id: str
    lead_id: str
    from_stage_id: str | None
    to_stage_id: str | None
    changed_by: str | None
    changed_at: datetime


class AuditLogRead(ORMModel):
    id: str
    actor_type: str
    actor_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    metadata_json: dict[str, Any] | None
    created_at: datetime


class DeadlineCreate(BaseModel):
    deadline_type: DeadlineType
    title: str
    deadline_date: date
    program: str | None = None
    is_active: bool = True
    source_id: str | None = None


class DeadlineUpdate(BaseModel):
    deadline_type: DeadlineType | None = None
    title: str | None = None
    deadline_date: date | None = None
    program: str | None = None
    is_active: bool | None = None
    source_id: str | None = None


class DeadlineRead(ORMModel):
    id: str
    deadline_type: str
    title: str
    deadline_date: date
    program: str | None
    is_active: bool
    source_id: str | None
    created_at: datetime
    updated_at: datetime
