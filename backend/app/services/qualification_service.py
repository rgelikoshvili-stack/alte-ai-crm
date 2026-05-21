from app.schemas.chat import AIAnalysisResult
from app.schemas.qualification import LeadQualificationResult


def build_qualification(message: str, analysis: AIAnalysisResult) -> LeadQualificationResult:
    contact = analysis.extracted_contact
    name = " ".join(part for part in [contact.first_name, contact.last_name] if part) or None
    intent = map_qualification_intent(message, analysis)
    urgency = detect_urgency(message)
    handover_requested = analysis.intent == "human_request"
    program_present = bool(analysis.program)
    contact_present = bool(contact.phone or contact.email)
    high_intent = intent in {"application", "admission_requirements"}

    score = 10
    if contact_present:
        score += 35
    if program_present:
        score += 25
    if high_intent:
        score += 15
    if urgency == "high":
        score += 15
    if handover_requested:
        score += 10
    score = min(score, 100)

    handover_required = handover_requested or score >= 80
    handover_reason = None
    if handover_requested:
        handover_reason = "human_requested"
    elif score >= 80:
        handover_reason = "high_intent_lead"

    status = "new"
    if handover_requested:
        status = "needs_human"
    elif score >= 80:
        status = "hot"
    elif score >= 60:
        status = "qualified"
    elif score >= 30:
        status = "researching"

    next_action = "ask_contact_details"
    if handover_required:
        next_action = "route_to_consultant"
    elif not program_present:
        next_action = "ask_preferred_program"
    elif not contact_present:
        next_action = "ask_phone_or_email"
    elif status in {"qualified", "hot"}:
        next_action = "create_follow_up_task"

    return LeadQualificationResult(
        name=name,
        phone=contact.phone,
        email=contact.email,
        preferred_program=analysis.program,
        intent=intent,
        urgency=urgency,
        language=analysis.language,
        lead_score=score,
        qualification_status=status,
        handover_required=handover_required,
        handover_reason=handover_reason,
        recommended_next_action=next_action,
    )


def apply_qualification_to_lead_create(data: dict, qualification: LeadQualificationResult) -> dict:
    data.update(
        {
            "qualification_intent": qualification.intent,
            "urgency": qualification.urgency,
            "lead_score": qualification.lead_score,
            "qualification_status": qualification.qualification_status,
            "handover_required": qualification.handover_required,
            "handover_reason": qualification.handover_reason,
            "recommended_next_action": qualification.recommended_next_action,
        }
    )
    if qualification.lead_score >= 60 and data.get("priority") == "normal":
        data["priority"] = "high"
    return data


def map_qualification_intent(message: str, analysis: AIAnalysisResult) -> str:
    lowered = message.lower()
    if analysis.intent == "human_request":
        return "human_help"
    if any(word in lowered for word in ["ფასი", "ღირს", "გადასახადი", "tuition", "fee"]):
        return "tuition_fee"
    if any(word in lowered for word in ["სტიპენდია", "scholarship", "grant"]):
        return "scholarship"
    if any(word in lowered for word in ["ცხრილი", "schedule", "calendar"]):
        return "schedule"
    if any(word in lowered for word in ["დარეგისტრირება", "apply", "application", "ჩარიცხვა"]):
        return "application"
    if any(word in lowered for word in ["მოთხოვნ", "requirements", "საბუთ"]):
        return "admission_requirements"
    if analysis.program:
        return "program_info"
    return "unknown"


def detect_urgency(message: str) -> str:
    lowered = message.lower()
    if any(phrase in lowered for phrase in ["დღეს მინდა დარეგისტრირება", "სასწრაფოდ", "call me", "apply now"]):
        return "high"
    if any(phrase in lowered for phrase in ["მალე", "soon", "this week"]):
        return "medium"
    return "low"
