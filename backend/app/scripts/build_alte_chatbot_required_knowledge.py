"""Build a chatbot-ready KB package from the required Alte documents only.

This script intentionally does not write to the database. It reads the local
Alte document export, selects only student/applicant-facing sources, repairs
the exported text encoding, deduplicates repeated Georgian/English duplicates,
and writes final JSONL/Markdown/source files for review and later import.
"""

from __future__ import annotations

import hashlib
import json
import re
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_DIR = Path(
    r"C:\Users\Acer\Documents\Codex\2026-05-19"
    r"\unexpected-status-403-forbidden-detail-code\alte_documents"
)
OUTPUT_DIR = REPO_ROOT / "backend" / "app" / "knowledge_seed" / "alte_chatbot_required_knowledge"
REVIEWER_CSV_PATH = REPO_ROOT / "backend" / "reports" / "alte_chatbot_required_knowledge_reviewer_queue.csv"


@dataclass(frozen=True)
class RequiredSource:
    source_key: str
    title: str
    topic: str
    department: str
    answer_policy: str
    student_facing: bool
    local_path: str
    canonical_questions: tuple[str, ...]


REQUIRED_SOURCES: tuple[RequiredSource, ...] = (
    RequiredSource(
        "program_catalog",
        "საგანმანათლებლო პროგრამების კატალოგი",
        "საგანმანათლებლო პროგრამები",
        "programs",
        "direct_if_explicit_else_handover",
        True,
        r"alte_documents\files\001_1.pdf",
        (
            "რა პროგრამები აქვს ალტე უნივერსიტეტს?",
            "რა ენაზე ისწავლება პროგრამა?",
            "რამდენი ECTS აქვს პროგრამას?",
            "რა წინაპირობებია პროგრამაზე ჩარიცხვისთვის?",
        ),
    ),
    RequiredSource(
        "academic_calendar",
        "აკადემიური კალენდარი 2025-2026",
        "აკადემიური კალენდარი",
        "academic_registry",
        "direct_with_official_channel_caveat",
        True,
        r"alte_documents\files\078_2025-2026.pdf",
        (
            "როდის იწყება სემესტრი?",
            "როდის არის ადმინისტრაციული რეგისტრაცია?",
            "როდის ტარდება შუალედური ან დასკვნითი გამოცდები?",
        ),
    ),
    RequiredSource(
        "study_process_regulation",
        "სასწავლო პროცესის მარეგულირებელი წესი",
        "სასწავლო პროცესი",
        "student_services",
        "conservative_for_personal_cases",
        True,
        r"alte_documents\files\056_RNsWsBG0Ma.pdf",
        (
            "როგორ რეგულირდება სასწავლო პროცესი?",
            "როგორ ხდება სტუდენტის სტატუსის შეჩერება ან აღდგენა?",
            "რა წესებია შეფასებასთან და გამოცდებთან დაკავშირებით?",
        ),
    ),
    RequiredSource(
        "bachelor_regulation",
        "ბაკალავრიატის დებულება",
        "ბაკალავრიატი",
        "admissions",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\059_RXIWmpwEt8.pdf",
        (
            "რა არის ბაკალავრიატზე ჩარიცხვის წესი?",
            "რა დოკუმენტები შეიძლება დასჭირდეს ბაკალავრიატის სტუდენტს?",
        ),
    ),
    RequiredSource(
        "master_regulation",
        "მაგისტრატურის დებულება",
        "მაგისტრატურა",
        "admissions",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\061_bMk2BHfX6z.pdf",
        (
            "რა არის მაგისტრატურაზე ჩარიცხვის წესი?",
            "საჭიროა თუ არა საერთო სამაგისტრო გამოცდა?",
        ),
    ),
    RequiredSource(
        "exam_regulation",
        "გამოცდების ჩატარების დებულება",
        "გამოცდები",
        "academic_registry",
        "conservative_for_personal_cases",
        True,
        r"alte_documents\files\077_.pdf",
        (
            "როგორ ტარდება გამოცდები?",
            "რა ხდება გამოცდაზე არგამოცხადების შემთხვევაში?",
            "როგორ ხდება გამოცდის შედეგის გასაჩივრება?",
        ),
    ),
    RequiredSource(
        "ects_recognition",
        "ECTS კრედიტების აღიარების წესი",
        "კრედიტების აღიარება",
        "academic_registry",
        "handover_for_exact_credit_decision",
        True,
        r"alte_documents\files\054_YcEblusTVZ.pdf",
        (
            "როგორ ხდება კრედიტების აღიარება?",
            "მობილობისას კრედიტები ჩამეთვლება?",
        ),
    ),
    RequiredSource(
        "individual_study_plan",
        "ინდივიდუალური სასწავლო გეგმის წესი",
        "ინდივიდუალური სასწავლო გეგმა",
        "academic_registry",
        "conservative_for_personal_cases",
        True,
        r"alte_documents\files\063_RRPR4gLRZ4.pdf",
        (
            "რა არის ინდივიდუალური სასწავლო გეგმა?",
            "ვის შეუძლია ინდივიდუალური სასწავლო გეგმის მოთხოვნა?",
        ),
    ),
    RequiredSource(
        "e_learning",
        "ელექტრონული სწავლების ადმინისტრირების წესი",
        "ელექტრონული სწავლება",
        "student_services",
        "direct_general_handover_technical",
        True,
        r"alte_documents\files\058_lCBeyC0gSb.pdf",
        (
            "როგორ რეგულირდება ელექტრონული სწავლება?",
            "ვის მივმართო ელექტრონულ სწავლებასთან დაკავშირებულ პრობლემაზე?",
        ),
    ),
    RequiredSource(
        "plagiarism",
        "პლაგიატის წესი",
        "აკადემიური კეთილსინდისიერება",
        "academic_registry",
        "direct_general_handover_case",
        True,
        r"alte_documents\files\065_QlAZe56OHS.pdf",
        (
            "რა ითვლება პლაგიატად?",
            "რა სანქციებია პლაგიატის შემთხვევაში?",
        ),
    ),
    RequiredSource(
        "financial_support",
        "ფინანსური მხარდაჭერის მექანიზმების წესი",
        "ფინანსური მხარდაჭერა",
        "finance",
        "conservative_handover_for_eligibility",
        True,
        r"alte_documents\files\067_-07.04.26.pdf",
        (
            "რა ფინანსური მხარდაჭერის მექანიზმებია?",
            "შესაძლებელია სწავლის საფასურის გადანაწილება?",
            "ვის მივმართო დაფინანსების საკითხზე?",
        ),
    ),
    RequiredSource(
        "state_social_grants",
        "სახელმწიფო სასწავლო გრანტები და სოციალური პროგრამა",
        "სახელმწიფო და სოციალური გრანტები",
        "finance",
        "conservative_handover_for_eligibility",
        True,
        r"alte_documents\files\072_hTOQuhgor4.pdf",
        (
            "ვის ეკუთვნის სოციალური პროგრამის დაფინანსება?",
            "სად უნდა დავრეგისტრირდე სოციალური დაფინანსებისთვის?",
            "რა ხდება თუ სამინისტროს გადაწყვეტილებას ველოდები?",
        ),
    ),
    RequiredSource(
        "finance_department_routing",
        "საფინანსო დეპარტამენტის დებულება",
        "ფინანსური საკითხების დეპარტამენტი",
        "finance",
        "handover_for_personal_finance_case",
        True,
        r"alte_documents\files\021_vtW1PMLU2V.pdf",
        (
            "ვის მივმართო სწავლის საფასურის ან გადახდის საკითხზე?",
            "რა საკითხებს განიხილავს საფინანსო დეპარტამენტი?",
        ),
    ),
    RequiredSource(
        "deans_grant",
        "დეკანის გრანტის წესი",
        "დეკანის გრანტი",
        "finance",
        "conservative_handover_for_eligibility",
        True,
        r"alte_documents\files\096_au4xEQ3RLj.pdf",
        (
            "რა არის დეკანის გრანტი?",
            "რა პირობებით ინიშნება დეკანის გრანტი?",
        ),
    ),
    RequiredSource(
        "student_service",
        "სტუდენტთა მომსახურების წესი",
        "სტუდენტთა მომსახურება",
        "student_services",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\094_69lz6nfM5T.pdf",
        (
            "რა სერვისებს სთავაზობს უნივერსიტეტი სტუდენტებს?",
            "ვის მივმართო სტუდენტურ სერვისებზე?",
        ),
    ),
    RequiredSource(
        "study_process_student_services_department",
        "სასწავლო პროცესისა და სტუდენტური სერვისების დეპარტამენტის დებულება",
        "სტუდენტური სერვისების დეპარტამენტი",
        "student_services",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\023_V9uUBO5ycd.pdf",
        (
            "რომელი დეპარტამენტი მეხმარება სასწავლო პროცესის საკითხებზე?",
            "ვის მივმართო სტუდენტურ სერვისებზე ან სასწავლო პროცესის პრობლემაზე?",
        ),
    ),
    RequiredSource(
        "student_rights",
        "სტუდენტთა უფლებების დაცვის მექანიზმები",
        "სტუდენტის უფლებები",
        "student_services",
        "direct_general_handover_complaint",
        True,
        r"alte_documents\files\095_LHzTgcc2Rc.pdf",
        (
            "როგორ იცავს უნივერსიტეტი სტუდენტის უფლებებს?",
            "სად შემიძლია საჩივრის ან განცხადების შეტანა?",
        ),
    ),
    RequiredSource(
        "ombudsman",
        "სტუდენტური ომბუდსმენის დებულება",
        "ომბუდსმენი",
        "student_services",
        "direct_general_handover_complaint",
        True,
        r"alte_documents\files\080_73ut09R5Pa.pdf",
        (
            "რას აკეთებს სტუდენტური ომბუდსმენი?",
            "როდის უნდა მივმართო ომბუდსმენს?",
        ),
    ),
    RequiredSource(
        "student_self_government",
        "სტუდენტური თვითმმართველობის დებულება",
        "სტუდენტური თვითმმართველობა",
        "student_services",
        "direct_general",
        True,
        r"alte_documents\files\082_6tvL7mhYc7.pdf",
        (
            "რა არის სტუდენტური თვითმმართველობა?",
            "როგორ მონაწილეობს სტუდენტი თვითმმართველობაში?",
        ),
    ),
    RequiredSource(
        "library_rules",
        "ბიბლიოთეკით სარგებლობის წესები",
        "ბიბლიოთეკა",
        "library",
        "direct_general",
        True,
        r"alte_documents\files\086_e1Y852YO2T.pdf",
        (
            "როგორ ვისარგებლო ბიბლიოთეკით?",
            "რა წესებია ბიბლიოთეკაში?",
        ),
    ),
    RequiredSource(
        "special_needs_service",
        "სპეციალური საჭიროების მქონე პირთა მომსახურების წესი",
        "სპეციალური საჭიროების მქონე პირთა მომსახურება",
        "student_services",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\088_Wmnayjohgb.pdf",
        (
            "რა მხარდაჭერა აქვს სპეციალური საჭიროების მქონე სტუდენტს?",
            "ვის მივმართო ადაპტაციის ან მხარდაჭერის მოთხოვნით?",
        ),
    ),
    RequiredSource(
        "career_alumni_service",
        "კარიერული განვითარების და კურსდამთავრებულთა მომსახურების წესი",
        "კარიერა და კურსდამთავრებულები",
        "career",
        "direct_general",
        True,
        r"alte_documents\files\092_UM4rez8Sgq.pdf",
        (
            "რა კარიერულ სერვისებს სთავაზობს უნივერსიტეტი სტუდენტებს?",
            "რა სერვისებია კურსდამთავრებულებისთვის?",
        ),
    ),
    RequiredSource(
        "international_affairs_department",
        "საერთაშორისო ურთიერთობების დეპარტამენტის დებულება",
        "საერთაშორისო სტუდენტები და ურთიერთობები",
        "international",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\027_BuGH59sVB6.pdf",
        (
            "ვის მივმართო საერთაშორისო სტუდენტობის ან საერთაშორისო ურთიერთობების საკითხზე?",
            "რომელი დეპარტამენტი მუშაობს საერთაშორისო ურთიერთობებზე?",
        ),
    ),
    RequiredSource(
        "it_service_department",
        "ინფორმაციული ტექნოლოგიების სამსახურის დებულება",
        "IT მხარდაჭერა",
        "it_support",
        "handover_for_technical_issue",
        True,
        r"alte_documents\files\033_elnTmWV7e8.pdf",
        (
            "ვის მივმართო პორტალზე ან ტექნიკურ პრობლემაზე?",
            "რომელი სამსახური უზრუნველყოფს IT მხარდაჭერას?",
        ),
    ),
    RequiredSource(
        "case_management_rule",
        "საქმისწარმოების წესი",
        "ფორმალური კომუნიკაცია და განცხადებები",
        "student_services",
        "direct_general_handover_personal",
        True,
        r"alte_documents\files\009_8HZmR5i6sh.pdf",
        (
            "როგორ ხდება ოფიციალური განცხადების ან დოკუმენტის წარდგენა?",
            "რა წესით მიმდინარეობს უნივერსიტეტთან ფორმალური კომუნიკაცია?",
        ),
    ),
    RequiredSource(
        "generative_ai_policy",
        "გენერაციული AI გამოყენების პოლიტიკა",
        "გენერაციული AI",
        "academic_registry",
        "direct_general_handover_case",
        True,
        r"alte_documents\files\131_yM6EMjQz9I.pdf",
        (
            "როგორ შეიძლება გენერაციული AI-ის გამოყენება?",
            "რა წესებია AI-ის გამოყენებაზე სასწავლო პროცესში?",
        ),
    ),
    RequiredSource(
        "university_provision",
        "უნივერსიტეტის ძირითადი დებულება",
        "უნივერსიტეტის დებულება",
        "student_services",
        "direct_general",
        True,
        r"alte_documents\files\051_JdliNRJQtI.pdf",
        (
            "რა არის ალტე უნივერსიტეტის ძირითადი სტრუქტურა?",
            "რომელი სკოლები ფუნქციონირებს უნივერსიტეტში?",
        ),
    ),
    RequiredSource(
        "business_school_provision",
        "ბიზნესის სკოლის დებულება",
        "სკოლის დებულება",
        "programs",
        "direct_general",
        True,
        r"alte_documents\files\049_YmB8rB2KY6.pdf",
        ("რა არის ბიზნესის სკოლის ძირითადი ფუნქცია?",),
    ),
    RequiredSource(
        "medicine_school_provision",
        "მედიცინის საერთაშორისო სკოლის დებულება",
        "სკოლის დებულება",
        "programs",
        "direct_general",
        True,
        r"alte_documents\files\047_GHvSFJeBo1.pdf",
        ("რა არის მედიცინის საერთაშორისო სკოლის ძირითადი ფუნქცია?",),
    ),
    RequiredSource(
        "law_social_school_provision",
        "სამართლისა და სოციალურ მეცნიერებათა სკოლის დებულება",
        "სკოლის დებულება",
        "programs",
        "direct_general",
        True,
        r"alte_documents\files\045_hWoGmPto2T.pdf",
        ("რა არის სამართლისა და სოციალურ მეცნიერებათა სკოლის ძირითადი ფუნქცია?",),
    ),
    RequiredSource(
        "it_school_provision",
        "საინფორმაციო ტექნოლოგიების სკოლის დებულება",
        "სკოლის დებულება",
        "programs",
        "direct_general",
        True,
        r"alte_documents\files\043_IyhKQqQDfX.pdf",
        ("რა არის საინფორმაციო ტექნოლოგიების სკოლის ძირითადი ფუნქცია?",),
    ),
    RequiredSource(
        "ethics_code",
        "ეთიკის კოდექსი",
        "ეთიკა",
        "student_services",
        "direct_general_handover_case",
        True,
        r"alte_documents\files\074_vQyJ19AYWH.pdf",
        (
            "რა წესებს ადგენს ეთიკის კოდექსი?",
            "რა ვალდებულებები აქვს სტუდენტს ეთიკის კოდექსით?",
        ),
    ),
)


def repair_text(value: str) -> str:
    """Repair UTF-8 Georgian text that was exported as mojibake."""
    if not isinstance(value, str):
        return value
    try:
        repaired = value.encode("latin1").decode("utf-8")
    except UnicodeEncodeError:
        repaired = value
    except UnicodeDecodeError:
        repaired = value
    return normalize_text(repaired)


def normalize_text(value: str) -> str:
    value = value.replace("\ufeff", " ")
    value = value.replace("\u00a0", " ")
    value = value.replace("â€™", "'").replace("â€œ", '"').replace("â€", '"')
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def compact_for_hash(value: str) -> str:
    return re.sub(r"\W+", "", value.lower(), flags=re.UNICODE)


def split_for_chatbot(text: str, max_chars: int = 2600) -> list[str]:
    """Split exported document text into reviewable chatbot-sized sections."""
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        return [text] if text.strip() else []

    sections: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if len(paragraph) > max_chars:
            if current:
                sections.append("\n\n".join(current).strip())
                current = []
                current_len = 0
            lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
            buffer: list[str] = []
            buffer_len = 0
            for line in lines:
                if buffer and buffer_len + len(line) + 1 > max_chars:
                    sections.append("\n".join(buffer).strip())
                    buffer = []
                    buffer_len = 0
                buffer.append(line)
                buffer_len += len(line) + 1
            if buffer:
                sections.append("\n".join(buffer).strip())
            continue

        next_len = current_len + len(paragraph) + 2
        looks_like_heading = len(paragraph) <= 90 and "\n" not in paragraph and not paragraph.endswith(".")
        if current and (next_len > max_chars or (looks_like_heading and current_len > 900)):
            sections.append("\n\n".join(current).strip())
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph) + 2

    if current:
        sections.append("\n\n".join(current).strip())
    return [section for section in sections if len(section) >= 80]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_chunks(source_dir: Path) -> list[dict]:
    chunks_path = source_dir / "alte_documents_chunks.jsonl"
    rows = []
    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                row["title"] = repair_text(row.get("title", ""))
                row["category"] = repair_text(row.get("category", ""))
                row["section"] = repair_text(row.get("section", ""))
                row["text"] = repair_text(row.get("text", ""))
                rows.append(row)
    return rows


def make_question(source: RequiredSource, chunk_index: int, chunk_text: str) -> str:
    if chunk_index < len(source.canonical_questions):
        return source.canonical_questions[chunk_index]
    heading = first_heading(chunk_text)
    if heading:
        return f"{source.topic}: რა წერია ნაწილში - {heading}?"
    return f"{source.topic}: რა ინფორმაციაა მოცემული წყაროში #{chunk_index + 1}?"


def first_heading(text: str) -> str:
    for line in text.splitlines():
        candidate = line.strip(" .:-")
        if 6 <= len(candidate) <= 120 and not re.fullmatch(r"[\d\s.,:;/-]+", candidate):
            return candidate
    return ""


def answer_from_chunk(source: RequiredSource, text: str) -> str:
    caveat = ""
    if source.department in {"finance", "academic_registry"} or "handover" in source.answer_policy:
        caveat = (
            "\n\nშენიშვნა: ინდივიდუალური შემთხვევის, უფლებამოსილების, დაფინანსების, "
            "კრედიტის აღიარების ან ოფიციალური გადაწყვეტილების დასადასტურებლად მომხმარებელი "
            "უნდა გადამისამართდეს შესაბამის დეპარტამენტთან."
        )
    return f"{text}{caveat}"


def iter_required_records(source_dir: Path) -> tuple[list[dict], list[dict]]:
    chunks = load_chunks(source_dir)
    source_by_path = {src.local_path: src for src in REQUIRED_SOURCES}
    seen: set[str] = set()
    records: list[dict] = []
    skipped: list[dict] = []
    counters: dict[str, int] = {}

    for row in chunks:
        local_path = row.get("local_path")
        source = source_by_path.get(local_path)
        if not source:
            continue
        text = row.get("text", "")
        if len(text) < 80:
            continue
        for segment in split_for_chatbot(text):
            content_key = hashlib.sha256(compact_for_hash(segment[:5000]).encode("utf-8")).hexdigest()
            if content_key in seen:
                skipped.append(
                    {
                        "local_path": local_path,
                        "title": source.title,
                        "reason": "duplicate_content",
                        "chunk_index": row.get("chunk_index"),
                    }
                )
                continue
            seen.add(content_key)
            index = counters.get(source.source_key, 0)
            counters[source.source_key] = index + 1
            source_id = f"alte_required_{source.source_key}_{index + 1:03d}"
            records.append(
                {
                    "source_id": source_id,
                    "question": make_question(source, index, segment),
                    "answer": answer_from_chunk(source, segment),
                    "topic": source.topic,
                    "department": source.department,
                    "language": "ka",
                    "source_title": source.title,
                    "source_file": Path(source.local_path).name,
                    "source_local_path": source.local_path,
                    "source_url": row.get("source_url"),
                    "section": row.get("section") or source.topic,
                    "chunk_index": index,
                    "answer_policy": source.answer_policy,
                    "handover_recommended": "handover" in source.answer_policy,
                    "student_facing": source.student_facing,
                    "keywords": sorted(set([source.topic, source.department, source.title])),
                }
            )

    return records, skipped


def write_jsonl(records: Iterable[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_markdown(records: list[dict], path: Path) -> None:
    lines = [
        "# Alte Chatbot Required Knowledge",
        "",
        "ეს ფაილი აგებულია მხოლოდ chatbot-ისთვის საჭირო, სტუდენტზე/აბიტურიენტზე ორიენტირებული Alte-ის დოკუმენტებიდან.",
        "შიდა ადმინისტრაციული ან დუბლირებული წყაროები გამოტოვებულია, თუ სტუდენტს პირდაპირ არ სჭირდება.",
        "",
    ]
    current_topic = None
    for record in records:
        if record["topic"] != current_topic:
            current_topic = record["topic"]
            lines.extend([f"## {current_topic}", ""])
        answer = record["answer"]
        if len(answer) > 1600:
            answer = answer[:1600].rstrip() + "..."
        lines.extend(
            [
                f"### კითხვა: {record['question']}",
                "",
                f"**პასუხი:** {answer}",
                "",
                f"**წყარო:** {record['source_title']} (`{record['source_file']}`)",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sources(records: list[dict], skipped: list[dict], source_dir: Path, path: Path) -> None:
    records_by_source: dict[str, list[dict]] = {}
    for record in records:
        records_by_source.setdefault(record["source_local_path"], []).append(record)

    lines = [
        "# Alte Chatbot Required Sources",
        "",
        f"Source export directory: `{source_dir}`",
        "",
        "## გამოყენებული წყაროები",
        "",
    ]
    for source in REQUIRED_SOURCES:
        file_path = source_dir.parent / source.local_path
        count = len(records_by_source.get(source.local_path, []))
        digest = sha256_file(file_path) if file_path.exists() else "MISSING"
        lines.extend(
            [
                f"### {source.title}",
                "",
                f"- topic: `{source.topic}`",
                f"- department: `{source.department}`",
                f"- local_path: `{source.local_path}`",
                f"- sha256: `{digest}`",
                f"- generated_qas: `{count}`",
                f"- answer_policy: `{source.answer_policy}`",
                "",
            ]
        )
    lines.extend(["## გამოტოვების/გაერთიანების წესები", ""])
    lines.append("- დუბლირებული ქართული/ინგლისური ან ერთი და იგივე შინაარსის ფაილები გაერთიანდა ერთ ქართულ source-of-truth ჩანაწერში.")
    lines.append("- პერსონალის მართვის, ფინანსური ანგარიშგების, რისკების, შიდა მართვის და სხვა შიდა ადმინისტრაციული დოკუმენტები არ ჩაიტვირთა.")
    lines.append("- სამართლებრივად/ფინანსურად/ინდივიდუალურ გადაწყვეტილებაზე დამოკიდებული საკითხები მონიშნულია conservative/handover პოლიტიკით.")
    lines.append("")
    lines.extend(["## დუბლირებული chunks", ""])
    if skipped:
        for item in skipped[:100]:
            lines.append(f"- {item['title']} / chunk {item['chunk_index']}: {item['reason']}")
    else:
        lines.append("- დუბლირებული chunk არ აღმოჩნდა შერჩეულ წყაროებში.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def suggested_decision(record: dict) -> str:
    policy = record["answer_policy"]
    if "finance" in record["department"] or "eligibility" in policy:
        return "APPROVE_CONSERVATIVE_OR_HANDOVER"
    if "handover" in policy or record["department"] == "academic_registry":
        return "APPROVE_CONSERVATIVE"
    return "APPROVE_PUBLIC"


def write_reviewer_csv(records: list[dict]) -> None:
    REVIEWER_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "source_id",
        "question",
        "source_title",
        "source_file",
        "topic",
        "department",
        "answer_policy",
        "handover_recommended",
        "suggested_decision",
        "reviewer_decision",
        "reviewer_comment",
    ]
    with REVIEWER_CSV_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "source_id": record["source_id"],
                    "question": record["question"],
                    "source_title": record["source_title"],
                    "source_file": record["source_file"],
                    "topic": record["topic"],
                    "department": record["department"],
                    "answer_policy": record["answer_policy"],
                    "handover_recommended": record["handover_recommended"],
                    "suggested_decision": suggested_decision(record),
                    "reviewer_decision": "",
                    "reviewer_comment": "",
                }
            )


def main() -> None:
    source_dir = DEFAULT_SOURCE_DIR
    if not source_dir.exists():
        raise SystemExit(f"Source directory not found: {source_dir}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records, skipped = iter_required_records(source_dir)
    if not records:
        raise SystemExit("No required knowledge records were generated.")

    jsonl_path = OUTPUT_DIR / "alte_chatbot_required_knowledge.jsonl"
    md_path = OUTPUT_DIR / "alte_chatbot_required_knowledge.md"
    sources_path = OUTPUT_DIR / "alte_chatbot_required_sources.md"

    write_jsonl(records, jsonl_path)
    write_markdown(records, md_path)
    write_sources(records, skipped, source_dir, sources_path)
    write_reviewer_csv(records)

    by_topic: dict[str, int] = {}
    for record in records:
        by_topic[record["topic"]] = by_topic.get(record["topic"], 0) + 1

    print(
        json.dumps(
            {
                "status": "BUILT",
                "output_dir": str(OUTPUT_DIR.relative_to(REPO_ROOT)),
                "jsonl": str(jsonl_path.relative_to(REPO_ROOT)),
                "markdown": str(md_path.relative_to(REPO_ROOT)),
                "sources": str(sources_path.relative_to(REPO_ROOT)),
                "reviewer_csv": str(REVIEWER_CSV_PATH.relative_to(REPO_ROOT)),
                "records": len(records),
                "topics": by_topic,
                "duplicates_skipped": len(skipped),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
