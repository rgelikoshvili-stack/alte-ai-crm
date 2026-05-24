from __future__ import annotations

from dataclasses import dataclass


DEPARTMENT_LABELS = {
    "admissions": "Admissions",
    "international": "International Admissions",
    "finance": "Finance",
    "medicine": "Medicine / MD",
    "student_services": "Student Services",
    "it_support": "IT Support",
    "general": "General / Operator",
}

SELECTED_DEPARTMENT_ALIASES = {
    "admission": "admissions",
    "admissions": "admissions",
    "programs": "admissions",
    "program": "admissions",
    "finance": "finance",
    "tuition": "finance",
    "funding": "finance",
    "international": "international",
    "international_admissions": "international",
    "join": "international",
    "medicine": "medicine",
    "medicine_md": "medicine",
    "md": "medicine",
    "student_services": "student_services",
    "student": "student_services",
    "it": "it_support",
    "it_support": "it_support",
    "technical": "it_support",
    "human": "general",
    "operator": "general",
    "general": "general",
}

KEYWORDS = {
    "international": [
        "international",
        "foreign",
        "visa",
        "relocation",
        "india",
        "nigeria",
        "pakistan",
        "nepal",
        "bangladesh",
        "country",
        "city",
        "join.alte",
        "საერთაშორისო",
        "უცხოელი",
        "ვიზა",
        "რელოკაცია",
        "ინდოეთი",
        "ნიგერია",
        "პაკისტანი",
        "ნეპალი",
        "ბანგლადეში",
    ],
    "medicine": [
        "medicine",
        "medical",
        "md",
        "dentistry",
        "doctor",
        "clinical",
        "მედიცინა",
        "სამედიცინო",
        "ექიმი",
        "სტომატოლოგია",
        "კლინიკური",
    ],
    "finance": [
        "tuition",
        "study cost",
        "fee",
        "fees",
        "price",
        "payment",
        "scholarship",
        "grant",
        "loan",
        "funding",
        "ფასი",
        "ღირს",
        "საფასური",
        "სწავლა",
        "გადახდა",
        "სტიპენდია",
        "გრანტი",
        "დაფინანსება",
        "სესხი",
    ],
    "admissions": [
        "admission",
        "admissions",
        "apply",
        "application",
        "enrollment",
        "bachelor",
        "master",
        "program",
        "deadline",
        "intake",
        "calendar",
        "registration",
        "document",
        "documents",
        "requirements",
        "მიღება",
        "ჩარიცხვა",
        "აბიტურიენტი",
        "ბაკალავრი",
        "მაგისტრი",
        "პროგრამა",
        "ვადა",
        "კალენდარი",
        "რეგისტრაცია",
        "საბუთი",
        "საბუთები",
        "დოკუმენტი",
    ],
    "student_services": [
        "library",
        "career",
        "club",
        "clubs",
        "ombudsman",
        "mentor",
        "student life",
        "ბიბლიოთეკა",
        "კარიერა",
        "კლუბი",
        "ომბუდსმენი",
        "მენტორი",
        "სტუდენტური",
    ],
    "it_support": [
        "portal",
        "login",
        "emis",
        "technical",
        "website not working",
        "account",
        "password",
        "პორტალი",
        "ტექნიკური",
        "შესვლა",
        "პაროლი",
        "საიტი",
    ],
}

INTENT_TO_DEPARTMENT = {
    "admission_interest": "admissions",
    "consultation_request": "admissions",
    "international_admission": "international",
    "medicine_admission": "medicine",
    "finance_question": "finance",
    "deadline_question": "admissions",
    "student_service": "student_services",
    "technical_support": "it_support",
    "human_request": "general",
}

SENSITIVE_TERMS = [
    "tuition",
    "fee",
    "price",
    "scholarship",
    "grant",
    "deadline",
    "document",
    "requirement",
    "medicine",
    "md",
    "international",
    "visa",
    "relocation",
    "legal",
    "საფასური",
    "ფასი",
    "სტიპენდია",
    "გრანტი",
    "ვადა",
    "საბუთ",
    "მოთხოვნ",
    "მედიცინ",
    "საერთაშორისო",
    "ვიზა",
    "რელოკაცია",
]

UNKNOWN_TERMS = [
    "unknown",
    "do not know",
    "don't know",
    "cannot answer",
    "not sure",
    "არ ვიცი",
    "ვერ გიპასუხებთ",
    "ვერ დავადასტურებ",
]


@dataclass(frozen=True)
class DepartmentRoutingResult:
    department: str
    department_key: str
    reason: str
    handover_required: bool
    confidence_reason: str
    sensitive_topic: bool


def resolve_department(
    *,
    message_text: str,
    ai_intent: str | None,
    ai_confidence: float | None,
    source_domain: str | None,
    selected_department: str | None,
    selected_topic: str | None,
    risk_flags: list[str] | None,
    used_sources: list[str] | None,
    language: str | None,
    ai_department: str | None = None,
) -> DepartmentRoutingResult:
    text = " ".join(
        item
        for item in [
            message_text or "",
            selected_topic or "",
            ai_intent or "",
            ai_department or "",
            source_domain or "",
        ]
        if item
    ).lower()
    selected_key = normalize_selected_department(selected_department)
    message_context = " ".join(item for item in [message_text or "", selected_topic or "", source_domain or ""] if item).lower()
    if selected_key == "international" and mentions_documents_or_admission(message_context):
        keyword_key = "international"
    elif any(keyword.lower() in message_context for keyword in KEYWORDS["medicine"]) and has_international_context(
        message_context, source_domain
    ):
        keyword_key = "medicine"
    else:
        keyword_key = keyword_department(text)
    intent_key = INTENT_TO_DEPARTMENT.get((ai_intent or "").lower())

    if is_human_request(text, ai_intent):
        department_key = selected_key or keyword_key or intent_key or "admissions"
        reason = "human_request_selected_or_inferred_department"
    elif keyword_key:
        department_key = keyword_key
        reason = "strong_message_keyword"
    elif selected_key:
        department_key = selected_key
        reason = "selected_sidebar_department"
    elif intent_key:
        department_key = intent_key
        reason = "ai_intent"
    elif source_domain == "join.alte.edu.ge":
        department_key = "international"
        reason = "join_domain_default"
    else:
        department_key = "admissions"
        reason = "default_admissions"

    if department_key == "admissions" and source_domain == "join.alte.edu.ge" and mentions_documents_or_admission(text):
        department_key = "international"
        reason = "join_domain_admissions_context"
    if department_key == "medicine" and has_international_context(text, source_domain):
        reason = "medicine_with_international_priority"

    sensitive_topic = has_sensitive_topic(text, risk_flags) or department_key in {"finance", "medicine", "international"}
    confidence = ai_confidence if ai_confidence is not None else 0.0
    source_missing = not used_sources and sensitive_topic
    low_confidence = confidence < 0.70
    unknown = is_unknown(text, risk_flags)
    human_request = is_human_request(text, ai_intent)
    handover_required = low_confidence or source_missing or sensitive_topic or unknown or human_request

    confidence_reason = "ok"
    if low_confidence:
        confidence_reason = "confidence_below_0_70"
    elif source_missing:
        confidence_reason = "source_missing_for_sensitive_topic"
    elif sensitive_topic:
        confidence_reason = "sensitive_topic_requires_confirmation"
    elif unknown:
        confidence_reason = "unknown_answer"
    elif human_request:
        confidence_reason = "human_request"

    return DepartmentRoutingResult(
        department=DEPARTMENT_LABELS[department_key],
        department_key=department_key,
        reason=reason,
        handover_required=handover_required,
        confidence_reason=confidence_reason,
        sensitive_topic=sensitive_topic,
    )


def normalize_selected_department(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return SELECTED_DEPARTMENT_ALIASES.get(normalized)


def keyword_department(text: str) -> str | None:
    matches: dict[str, int] = {}
    for key, keywords in KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text)
        if score:
            matches[key] = score
    if not matches:
        return None
    priority = ["finance", "medicine", "international", "it_support", "student_services", "admissions"]
    return sorted(matches, key=lambda key: (-matches[key], priority.index(key) if key in priority else 99))[0]


def has_sensitive_topic(text: str, risk_flags: list[str] | None) -> bool:
    flags = " ".join(risk_flags or []).lower()
    if any(flag in flags for flag in ["no_approved_source", "source_stale", "review_required", "low_confidence"]):
        return True
    return any(term in text for term in SENSITIVE_TERMS)


def is_human_request(text: str, ai_intent: str | None) -> bool:
    if (ai_intent or "").lower() == "human_request":
        return True
    return any(term in text for term in ["human", "operator", "consultant", "advisor", "ადამიან", "ოპერატორ", "კონსულტანტ"])


def is_unknown(text: str, risk_flags: list[str] | None) -> bool:
    flags = " ".join(risk_flags or []).lower()
    return any(flag in flags for flag in ["unknown", "ai_parse_failed"]) or any(term in text for term in UNKNOWN_TERMS)


def has_international_context(text: str, source_domain: str | None) -> bool:
    return source_domain == "join.alte.edu.ge" or any(term in text for term in KEYWORDS["international"])


def mentions_documents_or_admission(text: str) -> bool:
    return any(term in text for term in ["document", "requirements", "admission", "apply", "საბუთ", "დოკუმენტ", "მიღება"])
