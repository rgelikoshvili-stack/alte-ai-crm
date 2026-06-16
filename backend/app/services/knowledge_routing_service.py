from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge"
DEPARTMENT_MAP_PATH = DATA_DIR / "department_topic_source_map.json"
SOURCE_GROUPS_PATH = DATA_DIR / "source_groups.json"

DEPARTMENT_ALIASES = {
    "international": "international_admissions",
    "medicine": "medicine_md",
    "student_services": "study_process",
    "general": "human_operator",
}

GENERIC_CLARIFICATION_KA = "ზუსტად რომ გიპასუხოთ, გთხოვთ დააზუსტოთ — რომელი საკითხი გაინტერესებთ?"
GENERIC_CLARIFICATION_EN = "To answer accurately, please clarify which topic you mean."
GENERIC_OPTIONS_KA = ["მიღება", "პროგრამები", "სწავლის საფასური", "სტუდენტის სტატუსი"]
GENERIC_OPTIONS_EN = ["Admissions", "Programs", "Tuition/Finance", "Student status"]

PROGRAMS_CLARIFICATION_KA = (
    "რომელ პროგრამაზე გსურთ ინფორმაცია — ბაკალავრიატზე, მაგისტრატურაზე, მედიცინა/MD-ზე თუ საერთაშორისო მიღებაზე?"
)
PROGRAMS_CLARIFICATION_EN = (
    "Which program do you mean: bachelor, master, Medicine/MD, or international admissions?"
)
FINANCE_CLARIFICATION_KA = (
    "გადახდებზე რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: სწავლის საფასური გაინტერესებთ, "
    "გადახდის გრაფიკი თუ ფინანსურ დეპარტამენტთან დაკავშირება?"
)
FINANCE_CLARIFICATION_EN = (
    "To answer about payments, please clarify: tuition, payment schedule, or contacting the finance department?"
)
STATUS_CLARIFICATION_KA = (
    "სტუდენტის სტატუსთან დაკავშირებით რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: შეჩერება, აღდგენა, "
    "შეწყვეტა თუ მობილობა გაინტერესებთ?"
)
STATUS_CLARIFICATION_EN = (
    "To answer about student status, please clarify: suspension, restoration, termination, or mobility?"
)

BROAD_GENERIC_KA = {
    "სწავლა მაინტერესებს",
    "დახმარება მინდა",
    "ინფორმაცია მინდა",
    "მაინტერესებს",
    "კონსულტაცია მინდა",
}
BROAD_GENERIC_EN = {"i need information", "i need help", "help", "interested", "study"}
BROAD_PROGRAMS_KA = {"პროგრამები მაინტერესებს", "პროგრამა მაინტერესებს", "რა პროგრამებია"}
BROAD_PROGRAMS_EN = {"programs", "programs interested", "i am interested in programs"}
BROAD_FINANCE_KA = {"გადახდებზე მაინტერესებს", "გადახდა მაინტერესებს", "გადასახადებზე მაინტერესებს"}
BROAD_FINANCE_EN = {"payments", "payment", "tuition payment"}
BROAD_STATUS_KA = {"სტატუსზე მაქვს კითხვა", "სტატუსი მაინტერესებს", "სტატუსზე კითხვა მაქვს"}
BROAD_STATUS_EN = {"student status", "status question"}

EXPLICIT_INTERNATIONAL_MARKERS = [
    "international",
    "foreign",
    "visa",
    "india",
    "foreign education",
    "უცხოელი",
    "საერთაშორისო",
    "უცხოეთის",
    "უცხოეთში",
    "ვიზა",
    "ინდოეთი",
]

CS_SPRING_CALENDAR_MARKERS_KA = [
    "კომპიუტერული მეცნიერება",
    "კომპიუტერული მეცნიერების",
    "გაზაფხულის სემესტრი",
    "გაზაფხულის სემესტრის",
    "რეგისტრაცია",
    "რეგისტრაციის",
    "სემესტრის დაწყება",
]
CS_SPRING_CALENDAR_MARKERS_EN = [
    "computer science",
    "spring semester",
    "registration",
    "semester start",
]


@dataclass(frozen=True)
class KnowledgeRouteDecision:
    department_id: str
    department_label: str
    source_groups: list[str]
    primary_source_group: str | None
    clarification_required: bool
    clarification_question: str | None
    clarification_options: list[str]
    language: str
    confidence: float
    reason: str


@lru_cache(maxsize=1)
def load_department_topic_source_map() -> dict:
    return json.loads(DEPARTMENT_MAP_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_source_groups() -> dict:
    return json.loads(SOURCE_GROUPS_PATH.read_text(encoding="utf-8"))


def classify_knowledge_route(
    message: str,
    *,
    selected_department: str | None = None,
    source_domain: str | None = None,
) -> KnowledgeRouteDecision:
    language = detect_language(message)
    lowered = " ".join((message or "").lower().split())
    selected = normalize_department_id(selected_department)

    broad = broad_clarification(lowered, language)
    if broad:
        department_id, question, options = broad
        department = department_entry(department_id)
        return KnowledgeRouteDecision(
            department_id=department_id,
            department_label=label_for_department(department, language),
            source_groups=list(department.get("source_groups", [])),
            primary_source_group=first_source_group(department),
            clarification_required=True,
            clarification_question=question,
            clarification_options=options,
            language=language,
            confidence=1.0,
            reason="broad_question_requires_clarification",
        )

    scores = score_departments(lowered)
    if selected:
        scores[selected] = scores.get(selected, 0) + 2
    if source_domain == "join.alte.edu.ge" and "international_admissions" in scores and not has_explicit_international_context(lowered):
        scores["international_admissions"] = 0
    if not scores:
        department_id = selected or "admissions"
        reason = "default_or_selected_department"
        confidence = 0.55
    else:
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        department_id, top_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0
        confidence = min(0.99, 0.55 + (top_score * 0.12))
        reason = "department_keyword_score"
        if top_score <= 1 and second_score == top_score and is_generic_short_question(lowered) and not has_contact_or_handover_context(lowered):
            department = department_entry(department_id)
            question, options = generic_clarification(language)
            return KnowledgeRouteDecision(
                department_id=department_id,
                department_label=label_for_department(department, language),
                source_groups=list(department.get("source_groups", [])),
                primary_source_group=first_source_group(department),
                clarification_required=True,
                clarification_question=question,
                clarification_options=options,
                language=language,
                confidence=0.5,
                reason="multiple_close_department_scores",
            )

    department = department_entry(department_id)
    source_groups = list(department.get("source_groups", []))
    primary_source_group = choose_primary_source_group(department_id, lowered, source_groups)
    return KnowledgeRouteDecision(
        department_id=department_id,
        department_label=label_for_department(department, language),
        source_groups=source_groups,
        primary_source_group=primary_source_group,
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language=language,
        confidence=confidence,
        reason=reason,
    )


def detect_language(message: str) -> str:
    return "ka" if any("\u10a0" <= char <= "\u10ff" for char in message or "") else "en"


def normalize_department_id(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"admission", "admissions"}:
        return "admissions"
    if normalized in {"program", "programs"}:
        return "programs"
    if normalized in {"finance", "tuition", "funding"}:
        return "finance"
    if normalized in {"study_process", "status", "mobility", "exams", "ects"}:
        return "study_process"
    if normalized in {"academic_calendar", "calendar"}:
        return "academic_calendar"
    if normalized in {"international", "international_admissions"}:
        return "international_admissions"
    if normalized in {"medicine", "medicine_md", "md"}:
        return "medicine_md"
    if normalized in {"library"}:
        return "library"
    if normalized in {"career"}:
        return "career"
    if normalized in {"it", "it_support", "technical"}:
        return "it_support"
    if normalized in {"human", "operator", "general"}:
        return "human_operator"
    return DEPARTMENT_ALIASES.get(normalized)


def broad_clarification(lowered: str, language: str) -> tuple[str, str, list[str]] | None:
    if has_contact_or_handover_context(lowered):
        return None
    phase_10a = phase_10a_broad_clarification(lowered, language)
    if phase_10a:
        return phase_10a
    normalized = normalize_broad_question_text(lowered)
    if normalized in {
        "გამოცდები როდის არის",
        "რეგისტრაცია როდის არის",
        "სემესტრი როდის იწყება",
        "როდის არის რეგისტრაციის პერიოდი აკადემიურ კალენდარში",
        "როდის იწყება სემესტრი",
        "როდის არის შუალედური ან დასკვნითი გამოცდები",
    }:
        return (
            "academic_calendar",
            "გთხოვთ დააზუსტოთ: რომელი პროგრამის ჯგუფი, რომელი სემესტრი და რომელი მოვლენა გაინტერესებთ?",
            ["ბაკალავრიატი Computer Science-ის გარდა", "Computer Science", "მაგისტრატურა", "ერთსაფეხურიანი"],
        )
    if normalized == "გამოცდებზე მაინტერესებს":
        return (
            "study_process",
            "გთხოვთ დააზუსტოთ: გამოცდების თარიღები გაინტერესებთ, გამოცდაზე დაშვების წესი, შეფასება თუ გადაბარება?"
            if language == "ka"
            else "Please clarify: do you mean exam dates, final-exam admission rules, assessment, or retake rules?",
            ["გამოცდების თარიღები", "დაშვების წესი", "შეფასება", "გადაბარება"]
            if language == "ka"
            else ["Exam dates", "Admission rules", "Assessment", "Retake rules"],
        )
    if normalized in {"პროგრამის კრედიტები მაინტერესებს", "რამდენი კრედიტია პროგრამა"}:
        return (
            "programs",
            "რომელ პროგრამას გულისხმობთ? რომელი პროგრამის კრედიტები გაინტერესებთ — ბაკალავრიატი, მაგისტრატურა, მედიცინა / MD, სტომატოლოგია თუ კონკრეტული პროგრამა?"
            if language == "ka"
            else "Which program credits do you mean: bachelor, master, Medicine / MD, dentistry, or a specific program?",
            ["ბაკალავრიატი (240 ECTS)", "მაგისტრატურა (120 ECTS)", "მედიცინა / MD", "სტომატოლოგია", "კონკრეტული პროგრამა"]
            if language == "ka"
            else ["Bachelor", "Master", "Medicine / MD", "Dentistry", "Specific program"],
        )
    if normalized == "მიღება მაინტერესებს":
        return (
            "admissions",
            "გთხოვთ დააზუსტოთ: ბაკალავრიატი, მაგისტრატურა, საერთაშორისო მიღება, საბუთები თუ გამოცდების გარეშე ჩარიცხვა გაინტერესებთ?"
            if language == "ka"
            else "Please clarify: bachelor admission, master admission, international admission, documents, or admission without exams?",
            ["ბაკალავრიატი", "მაგისტრატურა", "საერთაშორისო მიღება", "საბუთები", "გამოცდების გარეშე ჩარიცხვა"]
            if language == "ka"
            else ["Bachelor", "Master", "International admission", "Documents", "Admission without exams"],
        )
    if normalized == "სტატუსზე კითხვა მაქვს":
        return (
            "study_process",
            "სტუდენტის სტატუსთან დაკავშირებით რა გაინტერესებთ — შეჩერება, აღდგენა, შეწყვეტა თუ მობილობა?"
            if language == "ka"
            else "Which student status topic do you mean: suspension, restoration, termination, or mobility?",
            ["შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"]
            if language == "ka"
            else ["Suspension", "Restoration", "Termination", "Mobility"],
        )
    if normalized in BROAD_PROGRAMS_KA or normalized in BROAD_PROGRAMS_EN:
        return (
            "programs",
            PROGRAMS_CLARIFICATION_KA if language == "ka" else PROGRAMS_CLARIFICATION_EN,
            ["ბაკალავრიატი", "მაგისტრატურა", "მედიცინა / MD", "საერთაშორისო მიღება"]
            if language == "ka"
            else ["Bachelor", "Master", "Medicine / MD", "International admissions"],
        )
    if normalized in BROAD_FINANCE_KA or normalized in BROAD_FINANCE_EN:
        return (
            "finance",
            FINANCE_CLARIFICATION_KA if language == "ka" else FINANCE_CLARIFICATION_EN,
            ["სწავლის საფასური", "გადახდის გრაფიკი", "ფინანსურ დეპარტამენტთან დაკავშირება"]
            if language == "ka"
            else ["Tuition", "Payment schedule", "Contact finance department"],
        )
    if normalized in BROAD_STATUS_KA or normalized in BROAD_STATUS_EN:
        return (
            "study_process",
            STATUS_CLARIFICATION_KA if language == "ka" else STATUS_CLARIFICATION_EN,
            ["შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"]
            if language == "ka"
            else ["Suspension", "Restoration", "Termination", "Mobility"],
        )
    if is_admissions_question(lowered) and is_generic_short_question(lowered):
        department = department_entry("admissions")
        return (
            "admissions",
            GENERIC_CLARIFICATION_KA if language == "ka" else GENERIC_CLARIFICATION_EN,
            list(department.get("clarification_options_ka" if language == "ka" else "clarification_options_en", [])),
        )
    if normalized == "კრედიტები მაინტერესებს":
        return (
            "programs",
            "ზუსტად რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: რომელი საფეხურის ან პროგრამის კრედიტები გაინტერესებთ?",
            ["ბაკალავრიატი", "მაგისტრატურა", "ერთსაფეხურიანი", "კონკრეტული პროგრამა"]
            if language == "ka"
            else ["Bachelor", "Master", "One-cycle", "Specific program"],
        )
    if normalized in {
        "კატალოგში პროგრამაზე ინფორმაცია მაინტერესებს",
        "პროგრამის შესახებ ინფორმაცია მაინტერესებს",
    }:
        return (
            "programs",
            "გთხოვთ დააზუსტოთ, რომელი პროგრამა გაინტერესებთ ან რომელი დეტალი გჭირდებათ: კრედიტები, ენა, კვალიფიკაცია თუ სასწავლო გეგმა?",
            ["კრედიტები", "სწავლების ენა", "კვალიფიკაცია", "სასწავლო გეგმა"]
            if language == "ka"
            else ["Credits", "Teaching language", "Qualification", "Study plan"],
        )
    if normalized in BROAD_GENERIC_KA or normalized in BROAD_GENERIC_EN:
        question, options = generic_clarification(language)
        return ("admissions", question, options)
    return None


def phase_10a_broad_clarification(lowered: str, language: str) -> tuple[str, str, list[str]] | None:
    is_ka = language == "ka" or any("\u10a0" <= char <= "\u10ff" for char in lowered or "")
    normalized = " ".join((lowered or "").strip().lower().split()).strip(" ?!.,;:")
    if normalized in {"\u10d3\u10d0\u10db\u10d4\u10ee\u10db\u10d0\u10e0\u10d4", "\u10d3\u10d0\u10ee\u10db\u10d0\u10e0\u10d4\u10d1\u10d0 \u10db\u10d8\u10dc\u10d3\u10d0"}:
        return (
            "general",
            "\u10e0\u10dd\u10db\u10d4\u10da \u10e1\u10d0\u10d9\u10d8\u10d7\u10ee\u10d6\u10d4 \u10d2\u10ed\u10d8\u10e0\u10d3\u10d4\u10d1\u10d0\u10d7 \u10d3\u10d0\u10ee\u10db\u10d0\u10e0\u10d4\u10d1\u10d0?",
            [
                "\u10db\u10d8\u10e6\u10d4\u10d1\u10d0 / Admissions",
                "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
                "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8",
                "\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10d4\u10d1\u10d8 / \u10d2\u10e0\u10d0\u10dc\u10e2\u10d4\u10d1\u10d8",
                "\u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10e3\u10e0\u10d8 \u10e1\u10d4\u10e0\u10d5\u10d8\u10e1\u10d4\u10d1\u10d8",
                "\u10dd\u10de\u10d4\u10e0\u10d0\u10e2\u10dd\u10e0\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d0",
            ],
        )
    if normalized in {"i need help", "help me", "help"}:
        return (
            "general",
            "Which topic do you need help with?",
            ["Admissions", "Academic calendar", "Programs", "Finance / grants", "Student services", "Talk to an operator"],
        )
    unsupported_or_exact_context = any(
        marker in lowered
        for marker in [
            "2027",
            "2028",
            "2031",
            "space campus",
            "cosmic campus",
            "current",
            "this year",
            "exact",
            "exactly",
            "\u10d9\u10dd\u10e1\u10db\u10dd\u10e1",
            "\u10db\u10d8\u10db\u10d3\u10d8\u10dc\u10d0\u10e0",
            "\u10ec\u10d4\u10da\u10e1",
            "\u10d6\u10e3\u10e1\u10e2",
        ]
    )
    if unsupported_or_exact_context:
        return None

    has_calendar_program = any(
        marker in lowered
        for marker in [
            "bachelor",
            "master",
            "computer science",
            "medicine",
            "one-cycle",
            "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0",
            "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0",
            "\u10d9\u10dd\u10db\u10de\u10d8\u10e3\u10e2\u10d4\u10e0",
            "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc",
            "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0",
        ]
    )
    has_policy_context = any(
        marker in lowered
        for marker in [
            "requirement",
            "requirements",
            "document",
            "documents",
            "procedure",
            "policy",
            "rule",
            "rules",
            "\u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc",
            "\u10e1\u10d0\u10d1\u10e3\u10d7",
            "\u10d3\u10dd\u10d9\u10e3\u10db\u10d4\u10dc\u10e2",
            "\u10de\u10e0\u10dd\u10ea\u10d4\u10d3\u10e3\u10e0",
            "\u10ec\u10d4\u10e1",
        ]
    )
    has_specific_calendar_fact = any(
        marker in lowered
        for marker in [
            "holiday",
            "holidays",
            "midterm",
            "retake",
            "retakes",
            "\u10e8\u10e3\u10d0\u10da\u10d4\u10d3\u10e3\u10e0",
            "\u10d2\u10d0\u10d3\u10d0\u10d1\u10d0\u10e0",
            "\u10e3\u10e5\u10db\u10d4",
            "\u10d0\u10e0\u10d3\u10d0\u10d3\u10d4\u10d2",
        ]
    )
    has_catalog_summary_context = any(
        marker in lowered
        for marker in [
            "distribution",
            "fields",
            "contains",
            "include",
            "includes",
            "catalog field",
            "\u10e0\u10dd\u10d2\u10dd\u10e0 \u10dc\u10d0\u10ec\u10d8\u10da\u10d3\u10d4\u10d1",
            "\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d4\u10d1\u10d8\u10e1 \u10db\u10d8\u10ee\u10d4\u10d3\u10d5\u10d8\u10d7",
            "\u10e0\u10d0 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0\u10e1 \u10e8\u10d4\u10d8\u10ea\u10d0\u10d5\u10e1",
            "\u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10d8 \u10d7\u10d8\u10d7\u10dd\u10d4\u10e3\u10da",
        ]
    )

    if (
        any(marker in lowered for marker in ["registration", "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8"])
        and not has_calendar_program
        and not has_policy_context
    ):
        if is_ka:
            return (
                "academic_calendar",
                "\u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0, \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1 \u10ef\u10d2\u10e3\u10e4\u10d8\u10e1 \u10db\u10d8\u10ee\u10d4\u10d3\u10d5\u10d8\u10d7, \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
                [
                    "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8\u10e1 \u10d0\u10d3\u10db\u10d8\u10dc\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10e3\u10da\u10d8 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0",
                    "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0",
                    "Computer Science-\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0",
                    "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d8\u10e1 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0",
                    "\u10e9\u10d0\u10d1\u10d0\u10e0\u10d4\u10d1\u10d8\u10e1/Admissions \u10de\u10e0\u10dd\u10ea\u10d4\u10e1\u10d8",
                ],
            )
        return (
            "academic_calendar",
            "Which registration do you mean?",
            ["Bachelor administrative registration", "Bachelor academic registration", "Computer Science registration", "Master registration", "Admissions process"],
        )

    broad_tuition_prompt = normalized in {
        "how much is tuition",
        "\u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8 \u10e0\u10d0\u10db\u10d3\u10d4\u10dc\u10d8\u10d0",
    }
    if broad_tuition_prompt and not any(
        marker in lowered
        for marker in [
            "bachelor",
            "master",
            "medicine",
            "international",
            "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0",
            "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0",
            "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc",
            "\u10e1\u10d0\u10d4\u10e0\u10d7\u10d0\u10e8\u10dd\u10e0\u10d8\u10e1",
        ]
    ):
        if is_ka:
            return (
                "finance",
                "\u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1 \u10d0\u10dc \u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
                ["\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8", "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0", "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc\u10d0/\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10d0\u10dc\u10d8", "\u10e1\u10d0\u10d4\u10e0\u10d7\u10d0\u10e8\u10dd\u10e0\u10d8\u10e1\u10dd \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8", "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d8\u10e1 \u10de\u10d8\u10e0\u10dd\u10d1\u10d4\u10d1\u10d8"],
            )
        return (
            "finance",
            "Which program or level tuition do you mean?",
            ["Bachelor", "Master", "Medicine / one-cycle", "International student", "Payment terms"],
        )

    has_grant_marker = any(marker in lowered for marker in ["grant", "scholarship", "funding", "\u10d2\u10e0\u10d0\u10dc\u10e2", "\u10e1\u10e2\u10d8\u10de\u10d4\u10dc\u10d3", "\u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1"])
    broad_grant_prompt = any(marker in lowered for marker in ["how do i get", "how can i get", "\u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd"])
    specific_grant_context = any(
        marker in lowered
        for marker in [
            "state grant",
            "social grant",
            "dean",
            "financial support",
            "policy",
            "details",
            "available",
            "what does",
            "what financial",
            "\u10e1\u10d0\u10ee\u10d4\u10da\u10db\u10ec\u10d8\u10e4\u10dd",
            "\u10e1\u10dd\u10ea\u10d8\u10d0\u10da",
            "\u10e0\u10d0 \u10d0\u10e0\u10d8\u10e1",
        ]
    )
    if has_grant_marker and broad_grant_prompt and not specific_grant_context:
        if is_ka:
            return (
                "finance",
                "\u10e0\u10dd\u10db\u10d4\u10da \u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10d4\u10d1\u10d0\u10d6\u10d4 \u10d2\u10e1\u10e3\u10e0\u10d7 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0?",
                [
                    "\u10e1\u10d0\u10ee\u10d4\u10da\u10db\u10ec\u10d8\u10e4\u10dd \u10d2\u10e0\u10d0\u10dc\u10e2\u10d8",
                    "\u10e8\u10d8\u10d3\u10d0 \u10e1\u10e2\u10d8\u10de\u10d4\u10dc\u10d3\u10d8\u10d0/\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10e3\u10e0\u10d8 \u10db\u10ee\u10d0\u10e0\u10d3\u10d0\u10ed\u10d4\u10e0\u10d0",
                    "\u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8\u10e1 \u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d8\u10e1 \u10de\u10d8\u10e0\u10dd\u10d1\u10d4\u10d1\u10d8",
                    "\u10e1\u10d0\u10d4\u10e0\u10d7\u10d0\u10e8\u10dd\u10e0\u10d8\u10e1\u10dd \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d4\u10d1\u10d8\u10e1\u10d7\u10d5\u10d8\u10e1 \u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10d4\u10d1\u10d0",
                ],
            )
        return (
            "finance",
            "Which funding topic do you mean?",
            ["State grant", "Internal scholarship / financial support", "Tuition payment terms", "Funding for international students"],
        )

    has_teaching_language_context = any(
        marker in lowered
        for marker in [
            "teaching language",
            "language",
            "\u10e1\u10ec\u10d0\u10d5\u10da\u10d4\u10d1\u10d8\u10e1 \u10d4\u10dc\u10d0",
            "\u10e0\u10d0 \u10d4\u10dc\u10d0",
        ]
    )
    if not has_teaching_language_context and not has_catalog_summary_context and any(marker in lowered for marker in ["programs", "programmes", "program catalog", "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1", "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d6"]):
        if not any(
            marker in lowered
            for marker in [
                "bachelor",
                "master",
                "one-cycle",
                "english",
                "computer science",
                "medicine",
                "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0",
                "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0",
                "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0",
                "\u10d8\u10dc\u10d2\u10da\u10d8\u10e1",
                "\u10d9\u10dd\u10db\u10de\u10d8\u10e3\u10e2\u10d4\u10e0",
                "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc",
            ]
        ):
            if is_ka:
                return (
                    "programs",
                    "\u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10e1 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7? \u10e0\u10dd\u10db\u10d4\u10da \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4 \u10d2\u10e1\u10e3\u10e0\u10d7 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0?",
                    ["\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8", "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0", "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10d0\u10dc\u10d8", "\u10d8\u10dc\u10d2\u10da\u10d8\u10e1\u10e3\u10e0\u10d4\u10dc\u10dd\u10d5\u10d0\u10dc\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8", "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc\u10d0 / MD", "\u10e1\u10d0\u10d4\u10e0\u10d7\u10d0\u10e8\u10dd\u10e0\u10d8\u10e1\u10dd \u10db\u10d8\u10e6\u10d4\u10d1\u10d0"],
                )
            return (
                "programs",
                "Which level of programs are you interested in?",
                ["Bachelor", "Master", "One-cycle", "English-language programs"],
            )

    if any(marker in lowered for marker in ["calendar", "academic calendar", "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0"]) and not has_calendar_program and not has_specific_calendar_fact:
        if is_ka:
            return (
                "academic_calendar",
                "\u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1 \u10d0\u10dc \u10e1\u10d4\u10db\u10d4\u10e1\u10e2\u10e0\u10d8\u10e1 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
                ["\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8", "Computer Science", "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0", "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10d0\u10dc\u10d8", "\u10d9\u10dd\u10dc\u10d9\u10e0\u10d4\u10e2\u10e3\u10da\u10d8 \u10d7\u10d0\u10e0\u10d8\u10e6\u10d8 / \u10d2\u10d0\u10db\u10dd\u10ea\u10d3\u10d0 / \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0"],
            )
        return (
            "academic_calendar",
            "Which program or semester calendar do you mean?",
            ["Bachelor", "Computer Science", "Master", "One-cycle", "Specific date / exam / registration"],
        )

    return None


def normalize_broad_question_text(lowered: str) -> str:
    text = " ".join((lowered or "").strip().lower().split())
    return text.strip(" ?!.,;:؟؛")


def generic_clarification(language: str) -> tuple[str, list[str]]:
    if language == "ka":
        return GENERIC_CLARIFICATION_KA, GENERIC_OPTIONS_KA
    return GENERIC_CLARIFICATION_EN, GENERIC_OPTIONS_EN


def score_departments(lowered: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    for department in load_department_topic_source_map()["departments"]:
        department_id = department["department_id"]
        keywords = department.get("keywords_ka", []) + department.get("keywords_en", [])
        score = sum(1 for keyword in keywords if keyword.lower() in lowered)
        if score:
            scores[department_id] = score
    if "emis" in lowered or "ვერ შევდივარ" in lowered:
        scores["it_support"] = scores.get("it_support", 0) + 3
    if "ბიბლიოთეკ" in lowered or "library" in lowered:
        scores["library"] = scores.get("library", 0) + 3
    if "ფინანსურ დეპარტამენტ" in lowered or "სწავლის საფასურ" in lowered:
        scores["finance"] = scores.get("finance", 0) + 3
    if "ჩავირიცხ" in lowered or "ჩაბარ" in lowered or "ჩარიცხ" in lowered:
        scores["admissions"] = scores.get("admissions", 0) + 3
    if "apply" in lowered or "admission" in lowered or "enrollment" in lowered:
        scores["admissions"] = scores.get("admissions", 0) + 3
    if "საბუთ" in lowered or "დოკუმენტ" in lowered or "document" in lowered:
        scores["admissions"] = scores.get("admissions", 0) + 2
    if "ოპერატორ" in lowered or "operator" in lowered or "human" in lowered or "დაკავშირ" in lowered:
        scores["human_operator"] = scores.get("human_operator", 0) + 4
    if "finance" in lowered or "ფინანსურ" in lowered or "სწავლის საფასურ" in lowered:
        scores["finance"] = scores.get("finance", 0) + 5
    if is_exam_rule_question(lowered):
        scores["study_process"] = scores.get("study_process", 0) + 10
        scores["academic_calendar"] = max(0, scores.get("academic_calendar", 0) - 4)
    if is_credit_recognition_question(lowered):
        scores["study_process"] = scores.get("study_process", 0) + 10
        scores["admissions"] = max(0, scores.get("admissions", 0) - 4)
    if is_teaching_language_question(lowered):
        scores["programs"] = scores.get("programs", 0) + 8
        scores["admissions"] = max(0, scores.get("admissions", 0) - 2)
    if is_english_program_requirements_question(lowered):
        scores["international_admissions"] = scores.get("international_admissions", 0) + 10
        scores["programs"] = max(0, scores.get("programs", 0) - 2)
    if is_computer_science_spring_calendar_question(lowered):
        scores["academic_calendar"] = scores.get("academic_calendar", 0) + 8
        scores["admissions"] = max(0, scores.get("admissions", 0) - 2)
    if is_calendar_question(lowered):
        scores["academic_calendar"] = scores.get("academic_calendar", 0) + 6
        scores["admissions"] = max(0, scores.get("admissions", 0) - 2)
        scores["programs"] = max(0, scores.get("programs", 0) - 2)
    if is_admissions_question(lowered):
        scores["admissions"] = scores.get("admissions", 0) + 6
        scores["programs"] = max(0, scores.get("programs", 0) - 2)
    if is_it_support_question(lowered):
        scores["it_support"] = scores.get("it_support", 0) + 8
    if is_career_question(lowered):
        scores["career"] = scores.get("career", 0) + 8
    if is_grants_or_finance_policy_question(lowered):
        scores["finance"] = scores.get("finance", 0) + 8
    if is_library_question(lowered):
        scores["library"] = scores.get("library", 0) + 8
    if is_iro_policy_question(lowered):
        scores["international_admissions"] = scores.get("international_admissions", 0) + 8
    if is_edi_or_sustainability_policy_question(lowered):
        scores["student_services"] = scores.get("student_services", 0) + 8
    if has_explicit_international_context(lowered):
        scores["international_admissions"] = scores.get("international_admissions", 0) + 8
        scores["admissions"] = max(0, scores.get("admissions", 0) - 2)
        scores["medicine_md"] = max(0, scores.get("medicine_md", 0) - 2)
    if any(marker in lowered for marker in ["medicine", "medical", "md", "მედიც", "სამედიცინო"]):
        scores["medicine_md"] = scores.get("medicine_md", 0) + 5
    return scores


def has_contact_or_handover_context(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "email",
            "@",
            "+995",
            "phone",
            "apply",
            "admission",
            "ჩარიცხ",
            "ჩაბარ",
            "ოპერატორ",
            "დაკავშირ",
            "operator",
            "human",
        ]
    )


def is_generic_short_question(lowered: str) -> bool:
    tokens = [token.strip("?!.,") for token in lowered.split() if token.strip("?!.,")]
    generic_tokens = {"მაინტერესებს", "კითხვა", "მინდა", "ინფორმაცია", "help", "information", "question"}
    return 0 < len(tokens) <= 2 and any(token in generic_tokens for token in tokens)


def has_explicit_international_context(lowered: str) -> bool:
    return any(marker in lowered for marker in EXPLICIT_INTERNATIONAL_MARKERS)


def is_computer_science_spring_calendar_question(lowered: str) -> bool:
    has_program = any(marker in lowered for marker in ["კომპიუტერული მეცნიერ", "computer science"])
    has_spring = any(marker in lowered for marker in ["გაზაფხულის სემესტ", "spring semester"])
    has_calendar_action = any(marker in lowered for marker in ["რეგისტრ", "სემესტრის დაწყ", "registration", "semester start"])
    return has_program and has_spring and has_calendar_action and is_academic_calendar_priority_question(lowered)


def is_exam_rule_question(lowered: str) -> bool:
    has_exam = any(marker in lowered for marker in ["exam", "retake", "make-up", "make up", "assessment"])
    has_rule = any(marker in lowered for marker in ["rule", "admission", "handled", "works", "how"])
    georgian_exam = any(marker in lowered for marker in ["გამოცდ", "გადაბარ", "დასკვნით"])
    georgian_rule = any(marker in lowered for marker in ["წეს", "დაშვ", "როგორ"])
    asks_when = any(marker in lowered for marker in ["when", "date", "calendar", "როდის", "áƒ áƒáƒ“áƒ˜áƒ¡"])
    return ((has_exam and has_rule) or (georgian_exam and georgian_rule)) and not asks_when


def is_credit_recognition_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "credit recognition",
            "recognition of credit",
            "recognized credits",
            "კრედიტების აღიარ",
            "კრედიტის აღიარ",
            "áƒ™áƒ áƒ”áƒ“áƒ˜áƒ¢áƒ”áƒ‘áƒ˜áƒ¡ áƒáƒ¦áƒ˜áƒáƒ ",
            "áƒ™áƒ áƒ”áƒ“áƒ˜áƒ¢áƒ˜áƒ¡ áƒáƒ¦áƒ˜áƒáƒ ",
        ]
    )


def is_teaching_language_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "teaching language",
            "language of instruction",
            "program language",
            "სწავლების ენა",
            "რა ენაზე",
            "áƒ¡áƒ¬áƒáƒ•áƒšáƒ”áƒ‘áƒ˜áƒ¡ áƒ”áƒœáƒ",
            "áƒ áƒ áƒ”áƒœáƒáƒ–áƒ”",
        ]
    )


def is_credit_volume_question(lowered: str) -> bool:
    has_credit = any(marker in lowered for marker in ["ects", "credit", "credits", "კრედიტ"])
    has_level = any(
        marker in lowered
        for marker in [
            "bachelor",
            "master",
            "medicine",
            "dentistry",
            "one-cycle",
            "one cycle",
            "საბაკალავრო",
            "ბაკალავრიატ",
            "სამაგისტრო",
            "მაგისტრატურ",
            "მედიცინ",
            "სტომატოლოგ",
            "ერთსაფეხურ",
        ]
    )
    return has_credit and has_level


def is_calendar_date_or_schedule_question(lowered: str) -> bool:
    has_time = any(marker in lowered for marker in ["when", "date", "schedule", "calendar", "როდის", "თარიღ", "განრიგ", "კალენდ"])
    has_calendar_topic = any(marker in lowered for marker in ["exam", "final", "midterm", "retake", "გამოცდ", "დასკვნით", "შუალედ", "გადაბარ"])
    return has_time and has_calendar_topic


def is_program_catalog_question(lowered: str) -> bool:
    if (is_credit_volume_question(lowered) or is_teaching_language_question(lowered)) and not is_program_catalog_explicit_scope(lowered):
        return False
    if is_academic_calendar_priority_question(lowered):
        return False
    if is_calendar_date_or_schedule_question(lowered):
        return False
    if any(
        marker in lowered
        for marker in [
            "ბიბლიოთეკ",
            "library",
            "book",
            "books",
            "database",
            "databases",
            "electronic resource",
            "მიღებ",
            "საბუთ",
            "ჩარიცხვ",
            "admission",
            "enrollment",
            "document",
            "გრანტ",
            "დაფინანს",
            "finance",
            "financial",
            "scholarship",
            "grant",
            "it დახმარ",
            "emis",
            "portal",
            "technical support",
        ]
    ):
        return False
    if any(marker in lowered for marker in ["program catalog", "higher education program catalog", "პროგრამების კატალოგ"]):
        return True
    if "კატალოგ" in lowered and any(marker in lowered for marker in ["პროგრამ", "საგანმანათლებლო"]):
        return True
    if any(
        marker in lowered
        for marker in [
            "how many programs",
            "number of programs",
            "programs in total",
            "total programs",
            "bachelor programs",
            "master programs",
            "one-cycle programs",
            "program list",
            "რამდენი საგანმანათლებლო პროგრამა",
            "რამდენი პროგრამა",
            "პროგრამები სულ",
            "საბაკალავრო პროგრამები",
            "სამაგისტრო პროგრამები",
            "ერთსაფეხურიანი პროგრამები",
        ]
    ):
        return True
    if "ჩამომითვალე" in lowered and any(
        marker in lowered
        for marker in [
            "პროგრამ",
            "საგანმანათლებლო",
            "საბაკალავრო",
            "სამაგისტრო",
            "ერთსაფეხურ",
            "კვალიფიკაცია",
            "სამართლის",
            "კომპიუტერული მეცნიერების",
        ]
    ):
        return True
    if any(
        marker in lowered
        for marker in [
            "program qualification",
            "qualification does",
            "law bachelor qualification",
            "law master qualification",
            "რა კვალიფიკაციას",
            "სამართლის საბაკალავრო",
            "სამართლის სამაგისტრო",
            "პროგრამის კვალიფიკაცია",
        ]
    ):
        return True
    if "computer science" in lowered and any(marker in lowered for marker in ["language", "languages"]) and any(marker in lowered for marker in ["catalog", "program"]):
        return True
    if any(marker in lowered for marker in ["computer science language", "computer science languages", "კომპიუტერული მეცნიერების პროგრამა"]) and any(
        marker in lowered for marker in ["language", "languages", "ენა", "ენებზე", "geo", "eng"]
    ):
        return True
    return any(marker in lowered for marker in ["distributed by level", "distribution by level", "levels distribution", "საფეხურების მიხედვით", "როგორ ნაწილდება"])


def is_program_catalog_explicit_scope(lowered: str) -> bool:
    if "catalog" in lowered and any(marker in lowered for marker in ["program", "computer science", "bachelor", "master", "one-cycle", "one cycle"]):
        return True
    return any(
        marker in lowered
        for marker in [
            "program catalog",
            "higher education program catalog",
            "პროგრამების კატალოგ",
            "კატალოგის მიხედვით",
            "კატალოგში",
        ]
    )


def is_english_program_requirements_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "english-language program",
            "english language program",
            "english program requirements",
            "english-language admission",
            "english language admission",
        ]
    )


def is_calendar_question(lowered: str) -> bool:
    if is_exam_rule_question(lowered):
        return False
    if is_academic_calendar_priority_question(lowered):
        return True
    return has_english_word_marker(lowered, ["academic calendar", "calendar", "schedule"]) or any(marker in lowered for marker in ["აკადემიური კალენდარი", "კალენდარი", "განრიგი"])


def has_english_word_marker(lowered: str, markers: list[str]) -> bool:
    for marker in markers:
        pattern = re.escape(marker).replace(r"\ ", r"\s+")
        if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", lowered):
            return True
    return False


def is_academic_calendar_priority_question(lowered: str) -> bool:
    if is_exam_rule_question(lowered):
        return False
    english_explicit_calendar_context = [
        "academic calendar",
        "calendar",
        "schedule",
    ]
    georgian_explicit_calendar_context = [
        "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3",
        "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3",
        "\u10d2\u10d0\u10dc\u10e0\u10d8\u10d2\u10d8",
    ]
    english_date_time_markers = [
        "when",
        "date",
        "dates",
        "start",
        "starts",
        "begin",
        "begins",
        "start date",
        "semester start",
        "exam date",
        "final date",
        "midterm date",
        "holiday dates",
        "final exams",
        "midterm exams",
        "holidays",
        "vacation",
    ]
    georgian_date_time_markers = [
        "\u10e0\u10dd\u10d3\u10d8\u10e1",
        "\u10e0\u10dd\u10d3\u10d8\u10d3\u10d0\u10dc",
        "\u10e0\u10dd\u10d3\u10d4\u10db\u10d3\u10d4",
        "\u10d7\u10d0\u10e0\u10d8\u10e6",
        "\u10d7\u10d0\u10e0\u10d8\u10e6\u10d4\u10d1\u10d8",
        "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3",
        "\u10d2\u10d0\u10dc\u10e0\u10d8\u10d2",
        "\u10d8\u10ec\u10e7\u10d4\u10d1\u10d0",
        "\u10d3\u10d0\u10ec\u10e7\u10d4\u10d1\u10d0",
        "\u10d3\u10d0\u10e1\u10e0\u10e3\u10da\u10d4\u10d1\u10d0",
        "\u10e0\u10d8\u10ea\u10ee\u10d5\u10e8\u10d8",
        "\u10e0\u10dd\u10db\u10d4\u10da \u10d3\u10e6\u10d4\u10e1",
    ]
    english_calendar_topics = [
        "semester",
        "registration",
        "exam",
        "midterm",
        "final",
        "retake",
        "holiday",
        "vacation",
        "bachelor",
        "master",
        "one-cycle",
        "one cycle",
        "computer science",
    ]
    georgian_calendar_topics = [
        "\u10e1\u10d4\u10db\u10d4\u10e1\u10e2\u10e0",
        "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0",
        "\u10d2\u10d0\u10db\u10dd\u10ea\u10d3",
        "\u10e8\u10e3\u10d0\u10da\u10d4\u10d3",
        "\u10d3\u10d0\u10e1\u10d9\u10d5\u10dc\u10d8\u10d7",
        "\u10d2\u10d0\u10d3\u10d0\u10d1\u10d0\u10e0",
        "\u10d0\u10e0\u10d3\u10d0\u10d3\u10d4\u10d2",
        "\u10e3\u10e5\u10db\u10d4",
        "\u10e1\u10d0\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0",
        "\u10e1\u10d0\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0",
        "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0",
    ]
    english_exclusion_terms = [
        "requirement",
        "requirements",
        "admission",
        "admissions",
        "eligibility",
        "documents",
        "document",
        "needed documents",
        "procedure",
        "rule",
        "rules",
        "policy",
        "how to register",
        "application requirements",
    ]
    georgian_exclusion_terms = [
        "\u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc\u10d0",
        "\u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc\u10d4\u10d1\u10d8",
        "\u10db\u10d8\u10e6\u10d4\u10d1\u10d0",
        "\u10e9\u10d0\u10e0\u10d8\u10ea\u10ee\u10d5\u10d0",
        "\u10e1\u10d0\u10d1\u10e3\u10d7\u10d4\u10d1\u10d8",
        "\u10d3\u10dd\u10d9\u10e3\u10db\u10d4\u10dc\u10e2\u10d4\u10d1\u10d8",
        "\u10e1\u10d0\u10ed\u10d8\u10e0\u10dd \u10d3\u10dd\u10d9\u10e3\u10db\u10d4\u10dc\u10e2\u10d4\u10d1\u10d8",
        "\u10de\u10e0\u10dd\u10ea\u10d4\u10d3\u10e3\u10e0\u10d0",
        "\u10ec\u10d4\u10e1\u10d8",
        "\u10ec\u10d4\u10e1\u10d4\u10d1\u10d8",
        "\u10de\u10dd\u10da\u10d8\u10e2\u10d8\u10d9\u10d0",
        "\u10e0\u10dd\u10d2\u10dd\u10e0 \u10d3\u10d0\u10d5\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d8\u10e0\u10d3\u10d4",
        "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d8\u10e1 \u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc\u10d4\u10d1\u10d8",
    ]
    has_explicit_context = has_english_word_marker(lowered, english_explicit_calendar_context) or any(marker in lowered for marker in georgian_explicit_calendar_context)
    has_date_time = has_english_word_marker(lowered, english_date_time_markers) or any(marker in lowered for marker in georgian_date_time_markers)
    has_calendar_topic = has_english_word_marker(lowered, english_calendar_topics) or any(marker in lowered for marker in georgian_calendar_topics)
    has_exclusion = has_english_word_marker(lowered, english_exclusion_terms) or any(marker in lowered for marker in georgian_exclusion_terms)
    if has_exclusion and not has_explicit_context and not has_date_time:
        return False
    return (has_explicit_context or has_date_time) and has_calendar_topic


def is_admissions_question(lowered: str) -> bool:
    if is_credit_recognition_question(lowered) or is_teaching_language_question(lowered):
        return False
    if is_selected_official_control_topic(lowered):
        return False
    return any(
        marker in lowered
        for marker in [
            "მიღება",
            "ჩაბარ",
            "ჩარიცხ",
            "საბუთ",
            "დოკუმენტ",
            "ეროვნული გამოცდ",
            "უცხოეთში მიღებული განათლება",
            "უცხოელი",
            "admission",
            "apply",
            "application",
            "enrollment",
            "requirement",
            "requirements",
            "required document",
            "documents",
            "document",
            "procedure",
            "policy",
            "national exam",
            "foreign applicant",
            "foreign education",
            "recognition",
        ]
    )


def is_selected_official_control_topic(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "ომბუდსმენ",
            "უფლებ",
            "სპეციალური საჭირო",
            "სსმ",
            "პლაგიატ",
            "კეთილსინდისიერ",
            "სანქცი",
            "edi",
            "მდგრად",
            "ბიბლიოთეკ",
            "სტუდენტური სერვის",
            "სერვისებს იღებს სტუდენტი",
            "student services",
            "student rights",
            "academic integrity",
            "special needs",
            "sustainability",
            "edi policy",
        ]
    )


def is_career_question(lowered: str) -> bool:
    return any(marker in lowered for marker in ["კარიერ", "სტაჟირ", "დასაქმ", "career", "internship", "employment", "job"])


def is_grants_or_finance_policy_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "dean's list",
            "deans list",
            "state grant",
            "social grant",
            "grant",
            "scholarship",
            "funding rule",
            "financial support",
            "სახელმწიფო სასწავლო გრანტ",
            "სოციალური პროგრამ",
            "ფინანსური მხარდაჭერ",
            "ფინანსური დახმარ",
        ]
    )


def is_library_question(lowered: str) -> bool:
    return any(marker in lowered for marker in ["library", "library resources", "database", "catalog", "books", "ბიბლიოთეკ"])


def is_iro_policy_question(lowered: str) -> bool:
    return any(marker in lowered for marker in ["iro policy", "international relations office", "iro"])


def is_edi_or_sustainability_policy_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "edi policy",
            "equality diversity inclusion",
            "sustainability",
            "sustainable development",
            "sustainability strategy",
            "sustainability report",
            "მდგრად",
            "თანასწორ",
            "მრავალფერ",
            "ინკლუზ",
        ]
    )


def is_it_support_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "emis",
            "login",
            "password",
            "portal",
            "student portal",
            "it policy",
            "information technology",
            "platform support",
            "technical access",
            "áƒžáƒáƒ áƒ¢áƒáƒš",
            "áƒžáƒáƒ áƒáƒš",
            "áƒ•áƒ”áƒ  áƒ¨áƒ”áƒ•áƒ“áƒ˜áƒ•áƒáƒ ",
        ]
    )


def department_entry(department_id: str) -> dict:
    departments = load_department_topic_source_map()["departments"]
    by_id = {item["department_id"]: item for item in departments}
    return by_id.get(department_id) or by_id["admissions"]


def label_for_department(department: dict, language: str) -> str:
    return department["department_label_ka"] if language == "ka" else department["department_label_en"]


def first_source_group(department: dict) -> str | None:
    groups = department.get("source_groups", [])
    return groups[0] if groups else None


def choose_primary_source_group(department_id: str, lowered: str, source_groups: list[str]) -> str | None:
    if not source_groups:
        return None
    if is_academic_calendar_priority_question(lowered):
        return "academic_calendar_2025_2026" if "academic_calendar_2025_2026" in source_groups else source_groups[0]
    if is_exam_rule_question(lowered):
        return "exams_and_assessment" if "exams_and_assessment" in source_groups else source_groups[0]
    if is_credit_recognition_question(lowered):
        return "student_status_and_mobility" if "student_status_and_mobility" in source_groups else source_groups[0]
    if is_credit_volume_question(lowered) and not is_program_catalog_explicit_scope(lowered):
        return "official_academic_rules" if "official_academic_rules" in source_groups else source_groups[0]
    if is_teaching_language_question(lowered) and not is_program_catalog_explicit_scope(lowered):
        return "official_academic_rules" if "official_academic_rules" in source_groups else source_groups[0]
    if is_program_catalog_question(lowered):
        return "program_catalog_sources" if "program_catalog_sources" in source_groups else source_groups[0]
    if is_english_program_requirements_question(lowered):
        return "international_admissions_sources" if "international_admissions_sources" in source_groups else source_groups[0]
    if department_id == "international_admissions" and any(marker in lowered for marker in ["medicine", "medical", "md", "english-language", "english language"]):
        return "international_admissions_sources" if "international_admissions_sources" in source_groups else source_groups[0]
    if department_id == "academic_calendar" or any(token in lowered for token in ["კალენდ", "რეგისტრ", "სემესტ", "calendar", "semester"]):
        return "academic_calendar_2025_2026" if "academic_calendar_2025_2026" in source_groups else source_groups[0]
    if department_id == "study_process":
        if any(token in lowered for token in ["გამოცდ", "gpa", "fx", "exam"]):
            return "exams_and_assessment"
        if any(token in lowered for token in ["სტატუს", "მობილ", "აღიარ", "status", "mobility", "recognition"]):
            return "student_status_and_mobility"
    if department_id == "admissions":
        return "admissions_rules" if "admissions_rules" in source_groups else source_groups[0]
    return source_groups[0]


def format_clarification_reply(decision: KnowledgeRouteDecision) -> str:
    question = decision.clarification_question or generic_clarification(decision.language)[0]
    if not decision.clarification_options:
        return question
    return f"{question}\n\n" + "\n".join(f"- {option}" for option in decision.clarification_options[:4])


def source_group_config(source_group_id: str | None) -> dict | None:
    if not source_group_id:
        return None
    groups = load_source_groups()["source_groups"]
    by_id = {item["id"]: item for item in groups}
    return by_id.get(source_group_id)
