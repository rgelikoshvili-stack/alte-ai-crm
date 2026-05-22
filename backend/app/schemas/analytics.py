from pydantic import BaseModel

from app.schemas.operator import CountItem


class AnalyticsOverview(BaseModel):
    total_leads: int
    hot_leads: int
    qualified_leads: int
    average_lead_score: float
    total_conversations: int
    human_handover_count: int
    open_tasks: int
    overdue_tasks: int
    knowledge_no_source_count: int
    answered_from_source_count: int


class LeadAnalytics(BaseModel):
    leads_by_status: list[CountItem]
    leads_by_priority: list[CountItem]
    leads_by_source_domain: list[CountItem]
    leads_by_program: list[CountItem]
    leads_by_country: list[CountItem]
    leads_by_qualification_status: list[CountItem]
    international_priority_count: int
    medical_track_count: int


class SlaAnalytics(BaseModel):
    open_tasks: int
    overdue_tasks: int
    due_today_tasks: int
    completed_tasks: int
    urgent_open_tasks: int
    human_handover_count: int
    open_handover_conversations: int


class KnowledgeAnalytics(BaseModel):
    total_sources: int
    sources_by_status: list[CountItem]
    sources_by_language: list[CountItem]
    total_snippets: int
    snippets_by_status: list[CountItem]
    stale_snippets: int
    no_approved_source_events: int
    answered_from_source_events: int


class AiAnalytics(BaseModel):
    total_ai_messages: int
    average_confidence: float
    intents: list[CountItem]
    answer_source_statuses: list[CountItem]
    handover_recommended_count: int

