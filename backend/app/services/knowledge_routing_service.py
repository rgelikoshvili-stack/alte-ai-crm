from __future__ import annotations

import json
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
    if lowered in BROAD_PROGRAMS_KA or lowered in BROAD_PROGRAMS_EN:
        return (
            "programs",
            PROGRAMS_CLARIFICATION_KA if language == "ka" else PROGRAMS_CLARIFICATION_EN,
            ["ბაკალავრიატი", "მაგისტრატურა", "მედიცინა / MD", "საერთაშორისო მიღება"]
            if language == "ka"
            else ["Bachelor", "Master", "Medicine / MD", "International admissions"],
        )
    if lowered in BROAD_FINANCE_KA or lowered in BROAD_FINANCE_EN:
        return (
            "finance",
            FINANCE_CLARIFICATION_KA if language == "ka" else FINANCE_CLARIFICATION_EN,
            ["სწავლის საფასური", "გადახდის გრაფიკი", "ფინანსურ დეპარტამენტთან დაკავშირება"]
            if language == "ka"
            else ["Tuition", "Payment schedule", "Contact finance department"],
        )
    if lowered in BROAD_STATUS_KA or lowered in BROAD_STATUS_EN:
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
    if lowered in BROAD_GENERIC_KA or lowered in BROAD_GENERIC_EN:
        question, options = generic_clarification(language)
        return ("admissions", question, options)
    return None


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
    return has_program and has_spring and has_calendar_action


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
    if is_credit_volume_question(lowered) or is_teaching_language_question(lowered):
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
    if any(marker in lowered for marker in ["computer science language", "computer science languages", "კომპიუტერული მეცნიერების პროგრამა"]) and any(
        marker in lowered for marker in ["language", "languages", "ენა", "ენებზე", "geo", "eng"]
    ):
        return True
    return any(marker in lowered for marker in ["distributed by level", "distribution by level", "levels distribution", "საფეხურების მიხედვით", "როგორ ნაწილდება"])


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
    return any(
        marker in lowered
        for marker in [
            "კალენდ",
            "რეგისტრ",
            "სემესტ",
            "შუალედ",
            "დასკვნით",
            "გადაბარ",
            "არდადეგ",
            "calendar",
            "registration",
            "semester",
            "midterm",
            "final exam",
            "retake",
            "holiday",
        ]
    )


def is_admissions_question(lowered: str) -> bool:
    if is_credit_recognition_question(lowered) or is_teaching_language_question(lowered):
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
            "required document",
            "documents",
            "national exam",
            "foreign applicant",
            "foreign education",
            "recognition",
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
        ]
    )


def is_library_question(lowered: str) -> bool:
    return any(marker in lowered for marker in ["library", "library resources", "database", "catalog", "books"])


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
    if is_exam_rule_question(lowered):
        return "exams_and_assessment" if "exams_and_assessment" in source_groups else source_groups[0]
    if is_credit_recognition_question(lowered):
        return "student_status_and_mobility" if "student_status_and_mobility" in source_groups else source_groups[0]
    if is_credit_volume_question(lowered):
        return "official_academic_rules" if "official_academic_rules" in source_groups else source_groups[0]
    if is_teaching_language_question(lowered):
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
