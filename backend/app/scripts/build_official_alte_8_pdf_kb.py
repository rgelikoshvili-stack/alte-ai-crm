from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "official_alte_8_pdf_kb"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "official_alte_8_pdf_kb"
REPORTS_DIR = PROJECT_ROOT / "backend" / "reports"
JSONL_PATH = OUTPUT_DIR / "official_alte_8_pdf_kb_normalized.jsonl"
QUESTION_BANK_PATH = OUTPUT_DIR / "official_alte_8_pdf_supported_questions.jsonl"
TAXONOMY_PATH = OUTPUT_DIR / "topic_taxonomy.json"
ANSWER_POLICY_PATH = OUTPUT_DIR / "official_alte_8_pdf_answer_policy.json"
MANIFEST_PATH = EVIDENCE_DIR / "OFFICIAL_ALTE_8_PDF_SOURCE_MANIFEST.md"
REVIEWER_CSV_PATH = REPORTS_DIR / "official_alte_8_pdf_kb_reviewer_queue.csv"


@dataclass(frozen=True)
class SourceDoc:
    index: int
    source_file: str
    original_file: str
    title: str
    department: str
    secondary_department: str
    topic: str
    sensitivity: str
    review_required: bool
    public_answer_allowed: bool
    handover_recommended: bool
    answer_policy: str
    suggested_decision: str
    content_type: str = "official_policy_or_catalog"


DOCS: tuple[SourceDoc, ...] = (
    SourceDoc(1, "01_program_catalog.pdf", "1.pdf", "Higher Education Program Catalog", "programs", "admissions", "programs", "low", False, True, False, "direct", "APPROVE_PUBLIC"),
    SourceDoc(2, "02_academic_calendar_2025_2026.pdf", "2025-2026.pdf", "Academic Calendar 2025-2026", "academic_registry", "student_services", "academic_calendar", "medium", True, False, True, "handover_if_uncertain", "APPROVE_CONSERVATIVE"),
    SourceDoc(3, "03_financial_support_mechanisms_2026_04_07.pdf", "-07.04.26.pdf", "Financial Support Mechanisms", "finance", "admissions", "finance", "high", True, False, True, "conservative", "HANDOVER_IF_UNCERTAIN"),
    SourceDoc(4, "04_state_social_grants.pdf", "hTOQuhgor4.pdf", "State Study Grants / Social Program", "finance", "admissions", "state_grants", "high", True, False, True, "conservative", "HANDOVER_IF_UNCERTAIN"),
    SourceDoc(5, "05_bachelor_regulation.pdf", "RXIWmpwEt8.pdf", "Bachelor's Regulation", "admissions", "academic_registry", "bachelor_regulation", "medium", False, True, True, "handover_if_uncertain", "APPROVE_CONSERVATIVE"),
    SourceDoc(6, "06_master_regulation.pdf", "bMk2BHfX6z.pdf", "Master's Regulation", "admissions", "academic_registry", "master_regulation", "medium", False, True, True, "handover_if_uncertain", "APPROVE_CONSERVATIVE"),
    SourceDoc(7, "07_ects_credit_recognition.pdf", "YcEblusTVZ.pdf", "Recognition of ECTS Credits", "academic_registry", "admissions", "mobility_and_credit_recognition", "medium", True, False, True, "handover_if_uncertain", "HANDOVER_IF_UNCERTAIN"),
    SourceDoc(8, "08_study_process_regulation.pdf", "RNsWsBG0Ma.pdf", "Study Process Regulation", "student_services", "academic_registry", "study_process", "medium", True, False, True, "handover_if_uncertain", "HANDOVER_IF_UNCERTAIN"),
)


TAXONOMY = {
    "programs": {"department": "programs"},
    "admissions": {"department": "admissions"},
    "academic_calendar": {"department": "academic_registry"},
    "finance": {"department": "finance"},
    "state_grants": {"department": "finance"},
    "bachelor_regulation": {"department": "admissions"},
    "master_regulation": {"department": "admissions"},
    "mobility_and_credit_recognition": {"department": "academic_registry"},
    "study_process": {"department": "student_services"},
    "student_status": {"department": "academic_registry"},
    "exams": {"department": "academic_registry"},
    "tuition": {"department": "finance"},
    "formal_communication": {"department": "student_services"},
    "student_rights_obligations": {"department": "student_services"},
}


ANSWER_POLICY = {
    "programs": {
        "policy": "direct",
        "public_answer_allowed": True,
        "rules": ["Answer general program facts directly from the catalog.", "Route to Admissions/Programs if a detail is missing or conflicting."],
    },
    "academic_calendar": {
        "policy": "handover_if_uncertain",
        "public_answer_allowed": False,
        "caveat_ka": "გთხოვთ, საბოლოო დადასტურებისთვის გადაამოწმოთ უნივერსიტეტის ოფიციალურ არხზე.",
        "rules": ["Use exact date ranges from the 2025-2026 calendar.", "Route personalized schedule questions to Academic Registry."],
    },
    "finance": {
        "policy": "conservative",
        "public_answer_allowed": False,
        "rules": ["Do not guarantee eligibility or financing.", "Route personal qualification/payment cases to Finance."],
    },
    "state_grants": {
        "policy": "conservative",
        "public_answer_allowed": False,
        "rules": ["Explain the general process.", "Do not guarantee ministry decisions.", "Route personal eligibility to Finance/Admissions."],
    },
    "bachelor_regulation": {
        "policy": "handover_if_uncertain",
        "public_answer_allowed": True,
        "rules": ["General admission rules may be answered.", "Personal cases, document validation, and deadlines route to Admissions."],
    },
    "master_regulation": {
        "policy": "handover_if_uncertain",
        "public_answer_allowed": True,
        "rules": ["General admission rules may be answered.", "Personal cases, document validation, and deadlines route to Admissions."],
    },
    "mobility_and_credit_recognition": {
        "policy": "handover_if_uncertain",
        "public_answer_allowed": False,
        "rules": ["Explain general recognition principles.", "Never guarantee exact credit recognition.", "Route transcript review to Academic Registry."],
    },
    "study_process": {
        "policy": "handover_if_uncertain",
        "public_answer_allowed": False,
        "rules": ["Answer general rules.", "Route personal status/exam/tuition decisions to Academic Registry or Student Services."],
    },
    "not_found": {
        "policy": "handover_if_uncertain",
        "reply_ka": "ამ საკითხზე ზუსტი ინფორმაცია მოცემულ ოფიციალურ დოკუმენტებში ვერ ვიპოვე.",
    },
}


QUESTION_TEMPLATES = {
    "programs": [
        ("ka", "რა პროგრამები აქვს ალტე უნივერსიტეტს?"),
        ("ka", "რამდენი კრედიტია სამართლის პროგრამა?"),
        ("ka", "რა ენაზე ისწავლება ფსიქოლოგია?"),
        ("en", "Does Alte have medicine in English?"),
        ("en", "How many ECTS is the medicine program?"),
    ],
    "academic_calendar": [
        ("ka", "როდის იწყება შემოდგომის სემესტრი?"),
        ("ka", "როდის არის ადმინისტრაციული რეგისტრაცია?"),
        ("ka", "როდის არის შუალედური გამოცდები?"),
        ("en", "When do final exams start?"),
    ],
    "finance": [
        ("ka", "შესაძლებელია სწავლის საფასურის გადანაწილება?"),
        ("ka", "რა არის დეკანის გრანტი?"),
        ("ka", "ვის ეკუთვნის 50%-იანი ან 100%-იანი დაფინანსება?"),
        ("en", "Can I pay tuition in installments?"),
    ],
    "state_grants": [
        ("ka", "სოციალური გრანტი ვის ეკუთვნის?"),
        ("ka", "სად უნდა დავრეგისტრირდე სოციალური დაფინანსებისთვის?"),
        ("ka", "დადებითი პასუხის შემთხვევაში თანხა როგორ ბრუნდება?"),
        ("en", "How does the state social grant process work?"),
    ],
    "bachelor_regulation": [
        ("ka", "ბაკალავრიატში ჩასარიცხად რა მჭირდება?"),
        ("ka", "შესაძლებელია გამოცდების გარეშე ჩარიცხვა?"),
        ("en", "What documents are needed for bachelor admission?"),
    ],
    "master_regulation": [
        ("ka", "მაგისტრატურაში ჩასარიცხად რა საბუთებია საჭირო?"),
        ("ka", "საჭიროა საერთო სამაგისტრო გამოცდა?"),
        ("en", "What are the admission requirements for master's programs?"),
    ],
    "mobility_and_credit_recognition": [
        ("ka", "სხვა უნივერსიტეტიდან გადმოსვლისას კრედიტებს მიღიარებენ?"),
        ("ka", "როგორ ხდება კრედიტების აღიარება?"),
        ("en", "Can my credits be recognized if I transfer?"),
    ],
    "study_process": [
        ("ka", "სტუდენტის სტატუსის შეჩერება როგორ ხდება?"),
        ("ka", "სტატუსის აღდგენა როგორ ხდება?"),
        ("ka", "სწავლის საფასურის გადახდაზე რა წესია?"),
        ("ka", "როგორ ხდება ფორმალური კომუნიკაცია?"),
        ("en", "How can student status be restored?"),
    ],
}


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_pages(path: Path) -> list[dict]:
    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = normalize_text(page.extract_text() or "")
        pages.append({"page": index, "text": text})
    return pages


def detect_subtopic(text: str, default: str) -> str:
    first_lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in first_lines[:6]:
        if 4 <= len(line) <= 120 and not re.match(r"^\d+$", line):
            return line[:120]
    return default


def keywords_for(doc: SourceDoc, text: str) -> list[str]:
    base = {doc.topic, doc.department, doc.secondary_department, doc.title.lower()}
    for word in re.findall(r"[A-Za-zა-ჰ0-9][A-Za-zა-ჰ0-9\-]{2,}", text):
        if len(base) >= 18:
            break
        if any(ch.isdigit() for ch in word) or word.lower() in {"ects", "pdf"} or len(word) > 5:
            base.add(word[:40].lower())
    return sorted(base)


def split_page_text(text: str) -> list[str]:
    if not text:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]
    chunks: list[str] = []
    buffer: list[str] = []
    words = 0
    for para in paragraphs:
        para_words = len(para.split())
        heading_like = len(para) < 120 and bool(re.search(r"(თავი|მუხლი|პროგრამა|სემესტრი|რეგისტრაცია|გამოცდა|გრანტი)", para, re.I))
        if buffer and (words + para_words > 850 or (heading_like and words > 250)):
            chunks.append("\n\n".join(buffer).strip())
            buffer = []
            words = 0
        buffer.append(para)
        words += para_words
    if buffer:
        chunks.append("\n\n".join(buffer).strip())
    refined: list[str] = []
    for chunk in chunks:
        parts = chunk.split()
        if len(parts) <= 1300:
            refined.append(chunk)
            continue
        for i in range(0, len(parts), 900):
            refined.append(" ".join(parts[i : i + 900]))
    return refined


def build_chunks(doc: SourceDoc, pages: list[dict]) -> list[dict]:
    chunks: list[dict] = []
    chunk_index = 1
    for page in pages:
        for text in split_page_text(page["text"]):
            if len(text) < 40:
                continue
            source_id = f"official_alte_8_pdf_kb_{doc.index:02d}_{Path(doc.source_file).stem}_p{page['page']:03d}_c{chunk_index:03d}"
            subtopic = detect_subtopic(text, doc.topic)
            chunks.append(
                {
                    "source_id": source_id,
                    "source_file": doc.source_file,
                    "original_file": doc.original_file,
                    "document_title": doc.title,
                    "page_start": page["page"],
                    "page_end": page["page"],
                    "chunk_index": chunk_index,
                    "language": "ka",
                    "department": doc.department,
                    "secondary_department": doc.secondary_department,
                    "topic": infer_topic(doc, text),
                    "subtopic": subtopic,
                    "content_type": doc.content_type,
                    "sensitivity": infer_sensitivity(doc, text),
                    "review_required": infer_review_required(doc, text),
                    "public_answer_allowed": infer_public_allowed(doc, text),
                    "handover_recommended": infer_handover(doc, text),
                    "answer_policy": infer_answer_policy(doc, text),
                    "keywords": keywords_for(doc, text),
                    "questions_supported": questions_for(doc),
                    "content": text,
                }
            )
            chunk_index += 1
    return chunks


def infer_topic(doc: SourceDoc, text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["გამოცდ", "შუალედ", "დასკვნით"]):
        return "exams" if doc.topic in {"academic_calendar", "study_process"} else doc.topic
    if any(x in t for x in ["სწავლის საფას", "გადახდ", "ტარიფ", "გრანტ", "დაფინანს"]):
        return "tuition" if doc.topic in {"finance", "state_grants", "study_process"} else doc.topic
    if any(x in t for x in ["სტატუს", "შეჩერ", "აღდგენ", "შეწყვეტ"]):
        return "student_status"
    if any(x in t for x in ["ფორმალური კომუნიკ", "ელექტრონულ", "შეტყობინ"]):
        return "formal_communication"
    return doc.topic


def infer_sensitivity(doc: SourceDoc, text: str) -> str:
    topic = infer_topic(doc, text)
    if doc.sensitivity == "high" or topic in {"tuition", "finance", "state_grants"}:
        return "high"
    if topic in {"academic_calendar", "exams", "student_status", "mobility_and_credit_recognition", "study_process"}:
        return "medium"
    return doc.sensitivity


def infer_review_required(doc: SourceDoc, text: str) -> bool:
    topic = infer_topic(doc, text)
    if topic in {"finance", "tuition", "academic_calendar", "student_status", "exams", "mobility_and_credit_recognition"}:
        return True
    return (infer_sensitivity(doc, text) in {"medium", "high"} and doc.topic not in {"bachelor_regulation", "master_regulation"}) or doc.review_required


def infer_public_allowed(doc: SourceDoc, text: str) -> bool:
    return infer_sensitivity(doc, text) == "low" and doc.public_answer_allowed


def infer_handover(doc: SourceDoc, text: str) -> bool:
    return not infer_public_allowed(doc, text) or doc.handover_recommended


def infer_answer_policy(doc: SourceDoc, text: str) -> str:
    topic = infer_topic(doc, text)
    if topic in {"finance", "tuition", "academic_calendar", "student_status", "exams", "mobility_and_credit_recognition"}:
        return "conservative" if infer_sensitivity(doc, text) == "high" else "handover_if_uncertain"
    sensitivity = infer_sensitivity(doc, text)
    if sensitivity == "high":
        return "conservative"
    if doc.answer_policy == "direct" and sensitivity == "low":
        return "direct"
    return doc.answer_policy


def questions_for(doc: SourceDoc) -> list[str]:
    return [q for _lang, q in QUESTION_TEMPLATES.get(doc.topic, [])]


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def build_question_bank() -> list[dict]:
    rows = []
    by_topic = {doc.topic: doc for doc in DOCS}
    for topic, questions in QUESTION_TEMPLATES.items():
        doc = by_topic[topic]
        for language, question in questions:
            rows.append(
                {
                    "question": question,
                    "language": language,
                    "expected_topic": topic,
                    "expected_department": doc.department,
                    "source_file": doc.source_file,
                    "answer_policy": doc.answer_policy,
                    "handover_if_uncertain": doc.answer_policy != "direct" or doc.handover_recommended,
                }
            )
    return rows


def write_manifest(hashes: dict[str, str]) -> None:
    lines = [
        "# Official Alte 8 PDF Source Manifest",
        "",
        "These files are the authoritative local Knowledge Base source set for this phase.",
        "",
        "| Normalized filename | Original filename | Document title | Department/topic | Expected routing | Sensitivity | Answer policy | Public direct answer | Handover recommended | SHA256 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for doc in DOCS:
        lines.append(
            "| {source_file} | {original_file} | {title} | {topic} | {department} / {secondary} | {sensitivity} | {policy} | {public} | {handover} | `{hash}` |".format(
                source_file=doc.source_file,
                original_file=doc.original_file,
                title=doc.title,
                topic=doc.topic,
                department=doc.department,
                secondary=doc.secondary_department,
                sensitivity=doc.sensitivity,
                policy=doc.answer_policy,
                public=str(doc.public_answer_allowed).lower(),
                handover=str(doc.handover_recommended).lower(),
                hash=hashes[doc.source_file],
            )
        )
    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reviewer_csv(chunks: list[dict]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "source_id",
        "source_file",
        "document_title",
        "page_start",
        "page_end",
        "department",
        "topic",
        "sensitivity",
        "review_required",
        "public_answer_allowed",
        "answer_policy",
        "suggested_decision",
        "reviewer_decision",
        "reviewer_comment",
    ]
    decision_by_file = {doc.source_file: doc.suggested_decision for doc in DOCS}
    with REVIEWER_CSV_PATH.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in chunks:
            writer.writerow(
                {
                    **{key: row.get(key) for key in fields if key in row},
                    "suggested_decision": decision_by_file[row["source_file"]],
                    "reviewer_decision": "",
                    "reviewer_comment": "",
                }
            )


def main() -> None:
    missing = [doc.source_file for doc in DOCS if not (EVIDENCE_DIR / doc.source_file).exists()]
    if missing:
        raise SystemExit(f"Missing official PDF evidence files: {missing}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hashes = {doc.source_file: sha256_file(EVIDENCE_DIR / doc.source_file) for doc in DOCS}
    all_chunks: list[dict] = []
    by_doc: dict[str, int] = {}
    for doc in DOCS:
        pages = extract_pages(EVIDENCE_DIR / doc.source_file)
        chunks = build_chunks(doc, pages)
        all_chunks.extend(chunks)
        by_doc[doc.source_file] = len(chunks)
    write_jsonl(JSONL_PATH, all_chunks)
    write_jsonl(QUESTION_BANK_PATH, build_question_bank())
    TAXONOMY_PATH.write_text(json.dumps(TAXONOMY, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ANSWER_POLICY_PATH.write_text(json.dumps(ANSWER_POLICY, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_manifest(hashes)
    write_reviewer_csv(all_chunks)
    summary = {
        "status": "BUILT",
        "jsonl_path": str(JSONL_PATH.relative_to(PROJECT_ROOT)),
        "question_bank_path": str(QUESTION_BANK_PATH.relative_to(PROJECT_ROOT)),
        "taxonomy_path": str(TAXONOMY_PATH.relative_to(PROJECT_ROOT)),
        "answer_policy_path": str(ANSWER_POLICY_PATH.relative_to(PROJECT_ROOT)),
        "reviewer_csv_path": str(REVIEWER_CSV_PATH.relative_to(PROJECT_ROOT)),
        "total_chunks": len(all_chunks),
        "chunks_by_document": by_doc,
        "review_required_count": sum(1 for row in all_chunks if row["review_required"]),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
