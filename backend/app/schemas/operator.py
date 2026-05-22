from datetime import datetime

from pydantic import BaseModel

from app.schemas.crm import (
    AuditLogRead,
    ConversationRead,
    CustomerRead,
    DepartmentRead,
    LeadRead,
    LeadStageHistoryRead,
    MessageRead,
    PipelineRead,
    PipelineStageRead,
    TaskRead,
)


class CountItem(BaseModel):
    key: str | None
    count: int


class InboxListItem(BaseModel):
    conversation_id: str
    channel: str
    status: str
    language: str
    human_handover: bool
    ai_handled: bool
    customer_id: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    lead_id: str | None = None
    lead_status: str | None = None
    lead_priority: str | None = None
    last_message_text: str | None = None
    last_message_sender_type: str | None = None
    last_message_at: datetime | None = None
    created_at: datetime


class ConversationDetail(BaseModel):
    conversation: ConversationRead
    customer: CustomerRead | None = None
    lead: LeadRead | None = None
    messages: list[MessageRead]
    summary: str | None = None
    human_handover: bool
    ai_handled: bool


class LeadListItem(BaseModel):
    lead_id: str
    customer_id: str
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    interest_area: str | None = None
    program: str | None = None
    status: str
    priority: str
    source_channel: str | None = None
    source_domain: str | None = None
    is_international_priority: bool
    medical_track: bool
    department_id: str | None = None
    stage_id: str | None = None
    created_at: datetime
    updated_at: datetime


class LeadDetail(BaseModel):
    lead: LeadRead
    customer: CustomerRead | None = None
    department: DepartmentRead | None = None
    assigned_user: dict | None = None
    stage: PipelineStageRead | None = None
    conversations: list[ConversationRead]
    tasks: list[TaskRead]
    stage_history: list[LeadStageHistoryRead]
    audit_events: list[AuditLogRead]


class TaskListItem(BaseModel):
    task_id: str
    title: str
    status: str
    priority: str
    due_date: datetime | None = None
    completed_at: datetime | None = None
    lead_id: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    department_id: str | None = None
    assigned_user_id: str | None = None
    created_at: datetime


class PipelineBoardLead(BaseModel):
    lead_id: str
    customer_name: str | None = None
    priority: str
    program: str | None = None
    created_at: datetime


class PipelineBoardStage(BaseModel):
    stage_id: str
    name: str
    order: int
    lead_count: int
    leads: list[PipelineBoardLead]


class PipelineBoard(BaseModel):
    pipeline: PipelineRead
    stages: list[PipelineBoardStage]


class DashboardOverview(BaseModel):
    total_customers: int
    total_leads: int
    open_leads: int
    won_leads: int
    lost_leads: int
    total_conversations: int
    human_handover_count: int
    open_tasks: int
    overdue_tasks: int
    leads_by_stage: list[CountItem]
    leads_by_channel: list[CountItem]
    leads_by_priority: list[CountItem]
    latest_conversations: list[InboxListItem]
    latest_tasks: list[TaskListItem]
