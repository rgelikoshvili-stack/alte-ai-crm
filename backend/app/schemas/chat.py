from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.qualification import LeadQualificationResult
from app.schemas.crm import Priority

Language = Literal["ka", "en", "unknown"]


class ExtractedContact(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    country: str | None = None
    city: str | None = None


class AIAnalysisResult(BaseModel):
    reply: str
    language: Language = "unknown"
    intent: str
    confidence: float
    should_create_lead: bool
    should_handover: bool
    department: str | None = None
    priority: Priority = "normal"
    missing_fields: list[str] = Field(default_factory=list)
    extracted_contact: ExtractedContact = Field(default_factory=ExtractedContact)
    interest_area: str | None = None
    program: str | None = None
    program_language: str | None = None
    source_domain: str | None = None
    conversation_summary: str | None = None
    used_sources: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    qualification: LeadQualificationResult = Field(default_factory=LeadQualificationResult)


class ChatSessionStartRequest(BaseModel):
    source_domain: str | None = "alte.edu.ge"
    language: Language = "unknown"


class ChatSessionStartResponse(BaseModel):
    conversation_id: str
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    source_domain: str | None = None


class ChatMessageRequest(BaseModel):
    conversation_id: str
    message: str
    session_id: str | None = None
    source_domain: str | None = "alte.edu.ge"


class ChatMessageResponse(BaseModel):
    conversation_id: str
    reply: str
    intent: str
    confidence: float
    should_create_lead: bool
    should_handover: bool
    created_lead_id: str | None = None
    created_task_id: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    lead_score: int | None = None
    qualification_status: str | None = None
    handover_reason: str | None = None
    recommended_next_action: str | None = None
