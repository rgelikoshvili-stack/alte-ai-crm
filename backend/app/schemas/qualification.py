from typing import Literal

from pydantic import BaseModel

QualificationIntent = Literal[
    "program_info",
    "admission_requirements",
    "tuition_fee",
    "scholarship",
    "schedule",
    "application",
    "human_help",
    "unknown",
]
Urgency = Literal["low", "medium", "high"]
QualificationStatus = Literal["new", "researching", "qualified", "hot", "needs_human"]


class LeadQualificationResult(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    preferred_program: str | None = None
    intent: QualificationIntent = "unknown"
    urgency: Urgency = "low"
    language: Literal["ka", "en", "unknown"] = "unknown"
    lead_score: int = 10
    qualification_status: QualificationStatus = "new"
    handover_required: bool = False
    handover_reason: str | None = None
    recommended_next_action: str = "ask_clarifying_question"
