from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "alte_desktop_study_kb_v3"
SOURCE_FILE = EVIDENCE_DIR / "alte_kb_complete_v3.py"
SEED_DIR = BACKEND_ROOT / "app" / "knowledge_seed" / "alte_desktop_study_kb_v3"
REPORTS_DIR = BACKEND_ROOT / "reports"
NORMALIZED_JSONL = SEED_DIR / "alte_kb_complete_v3_normalized.jsonl"
SUMMARY_JSON = REPORTS_DIR / "alte_kb_complete_v3_normalization_summary.json"
SUMMARY_MD = REPORTS_DIR / "alte_kb_complete_v3_normalization_summary.md"

HIGH_TERMS = [
    "tuition",
    "fee",
    "fees",
    "price",
    "cost",
    "grant",
    "scholarship",
    "deadline",
    "document",
    "documents",
    "requirement",
    "requirements",
    "medicine",
    "medical",
    "md",
    "dentistry",
    "international",
    "visa",
    "relocation",
    "legal",
    "accreditation",
    "recognition",
    "payment",
    "contract",
    "$",
    "ielts",
    "toefl",
    "nmc",
    "who",
    "wdoms",
    "fmge",
    "საფას",
    "ფასი",
    "ღირებულ",
    "გრანტ",
    "სტიპენდ",
    "ვადა",
    "საბუთ",
    "დოკუმენტ",
    "მოთხოვნ",
    "მედიც",
    "სამედიცინო",
    "სტომატოლოგ",
    "საერთაშორისო",
    "ვიზა",
    "რელოკ",
    "აკრედიტ",
    "გადახდ",
    "ხელშეკრულ",
]

MEDIUM_TERMS = [
    "program",
    "school",
    "bachelor",
    "master",
    "admission",
    "apply",
    "student services",
    "library",
    "career",
    "პროგრამ",
    "სკოლა",
    "ბაკალავრ",
    "მაგისტ",
    "მიღება",
    "ბიბლიოთეკ",
    "კარიერ",
]


def slugify(value: str, *, fallback: str) -> str:
    ascii_value = re.sub(r"[^a-z0-9]+", "-", value.lower())
    ascii_value = re.sub(r"-+", "-", ascii_value).strip("-")
    return ascii_value[:90] or fallback


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_alte_kb_string(path: Path = SOURCE_FILE) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ALTE_KB" and isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, str):
                        return node.value.value
    raise ValueError("ALTE_KB string assignment not found")


def split_markdown_sections(text: str) -> list[dict[str, str]]:
    matches = list(re.finditer(r"(?m)^(#{2,3})\s+(.+?)\s*$", text))
    if not matches:
        return [{"title": "Alte Knowledge Base v3", "section": "full", "content": text.strip()}]

    chunks: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group(2).strip()
        content = text[start:end].strip()
        if not content:
            continue
        chunks.append(
            {
                "title": title[:240],
                "section": title[:240],
                "content": f"{title}\n\n{content}".strip(),
            }
        )
    return chunks


def extract_source_url(content: str) -> str:
    match = re.search(r"https?://[^\s)]+", content)
    return match.group(0).rstrip(".,;") if match else "https://alte.edu.ge"


def classify_department(content: str) -> str:
    haystack = content.lower()
    if any(term in haystack for term in ["medicine", "medical", "md", "dentistry", "მედიც", "სამედიცინო", "სტომატოლოგ"]):
        return "Medicine"
    if any(term in haystack for term in ["international", "foreign", "visa", "relocation", "join.alte", "საერთაშორისო", "უცხოელ", "ვიზა"]):
        return "International Admissions"
    if any(term in haystack for term in ["tuition", "fee", "cost", "payment", "scholarship", "grant", "საფას", "ფასი", "გრანტ", "სტიპენდ"]):
        return "Finance"
    if any(term in haystack for term in ["deadline", "calendar", "registration", "exam", "ვადა", "კალენდ", "რეგისტრ", "გამოცდ"]):
        return "Academic Registry"
    if any(term in haystack for term in ["library", "career", "student life", "ombudsman", "ბიბლიოთეკ", "კარიერ", "ომბუდსმენ"]):
        return "Student Services"
    if any(term in haystack for term in ["admission", "apply", "bachelor", "master", "program", "მიღება", "ჩარიცხვ", "ბაკალავრ", "მაგისტ", "პროგრამ"]):
        return "Admissions"
    return "General"


def classify_category(content: str) -> str:
    haystack = content.lower()
    if any(term in haystack for term in ["visa", "relocation", "ვიზა", "რელოკ"]):
        return "visa_relocation"
    if any(term in haystack for term in ["dentistry", "სტომატოლოგ"]):
        return "dentistry"
    if any(term in haystack for term in ["medicine", "medical", "md", "მედიც", "სამედიცინო"]):
        return "medicine_md"
    if any(term in haystack for term in ["international", "foreign", "join.alte", "საერთაშორისო", "უცხოელ"]):
        return "international_admissions"
    if any(term in haystack for term in ["tuition", "fee", "cost", "payment", "scholarship", "grant", "$", "საფას", "ფასი", "გრანტ", "სტიპენდ"]):
        return "finance_tuition"
    if any(term in haystack for term in ["deadline", "calendar", "registration", "exam", "ვადა", "კალენდ", "რეგისტრ", "გამოცდ"]):
        return "deadlines_calendar"
    if any(term in haystack for term in ["document", "requirement", "საბუთ", "დოკუმენტ", "მოთხოვნ"]):
        return "required_documents"
    if any(term in haystack for term in ["library", "career", "student life", "ombudsman", "ბიბლიოთეკ", "კარიერ", "ომბუდსმენ"]):
        return "student_services"
    if any(term in haystack for term in ["admission", "apply", "მიღება", "ჩარიცხვ"]):
        return "admissions_general"
    if any(term in haystack for term in ["program", "bachelor", "master", "პროგრამ", "ბაკალავრ", "მაგისტ"]):
        return "program_overview"
    if any(term in haystack for term in ["contact", "phone", "email", "კონტაქტ", "ტელ", "ელფოსტ"]):
        return "general_contact"
    return "about"


def classify_sensitivity(content: str, category: str) -> str:
    haystack = content.lower()
    if category in {
        "finance_tuition",
        "deadlines_calendar",
        "required_documents",
        "international_admissions",
        "medicine_md",
        "dentistry",
        "visa_relocation",
    }:
        return "high"
    if any(term in haystack for term in HIGH_TERMS):
        return "high"
    if category in {"program_overview", "admissions_general", "student_services"}:
        return "medium"
    if any(term in haystack for term in MEDIUM_TERMS):
        return "medium"
    return "low"


def recommended_action(category: str, sensitivity: str) -> str:
    if category in {"visa_relocation"}:
        return "HANDOVER_ONLY"
    if sensitivity == "high":
        return "NEEDS_OFFICIAL_SOURCE"
    if sensitivity == "medium":
        return "REVIEW_REQUIRED"
    return "APPROVE_CANDIDATE"


def keywords_for(title: str, content: str, category: str) -> list[str]:
    values = {category}
    for token in re.split(r"[\s,/|:;()#\-]+", f"{title} {content[:600]}"):
        token = token.strip()
        if 3 <= len(token) <= 40:
            values.add(token)
    return sorted(values)[:30]


def normalize() -> list[dict[str, Any]]:
    raw_text = read_alte_kb_string()
    sections = split_markdown_sections(raw_text)
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, section in enumerate(sections):
        content = section["content"].strip()
        if len(content) < 40:
            continue
        dedupe = stable_hash(content)
        if dedupe in seen:
            continue
        seen.add(dedupe)
        category = classify_category(content)
        sensitivity = classify_sensitivity(content, category)
        review_required = sensitivity == "high"
        source_url = extract_source_url(content)
        title = section["title"]
        source_key = f"alte_desktop_kb_v3_{category}_{slugify(title, fallback='section')}"[:160]
        normalized.append(
            {
                "source_key": source_key,
                "source_url": source_url,
                "source_file": "alte_kb_complete_v3.py",
                "title": title,
                "language": "ka",
                "locale": "ka",
                "department": classify_department(content),
                "category": category,
                "section": section["section"],
                "chunk_index": index,
                "content": content,
                "keywords": keywords_for(title, content, category),
                "lastmod": "2026-05-24",
                "source_type": "alte_desktop_study_kb_v3",
                "source_domain": "alte.edu.ge",
                "status": "approved",
                "review_required": review_required,
                "sensitivity": sensitivity,
                "public_answer_allowed": sensitivity != "high" and not review_required,
                "recommended_review_action": recommended_action(category, sensitivity),
                "stale_after_days": 30 if sensitivity == "high" else 90,
                "program_name": None,
                "metadata_json": {
                    "source_file": "alte_kb_complete_v3.py",
                    "source_url": source_url,
                    "version": "alte_desktop_study_kb_v3",
                    "public_answer_allowed": sensitivity != "high" and not review_required,
                    "recommended_review_action": recommended_action(category, sensitivity),
                },
            }
        )
    return normalized


def write_outputs(records: list[dict[str, Any]]) -> dict[str, Any]:
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    NORMALIZED_JSONL.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )
    category_counts = Counter(record["category"] for record in records)
    department_counts = Counter(record["department"] for record in records)
    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_file": str(SOURCE_FILE.relative_to(PROJECT_ROOT)),
        "normalized_records": len(records),
        "high_sensitivity_count": sum(1 for item in records if item["sensitivity"] == "high"),
        "review_required_count": sum(1 for item in records if item["review_required"]),
        "category_counts": dict(sorted(category_counts.items())),
        "department_counts": dict(sorted(department_counts.items())),
        "output_path": str(NORMALIZED_JSONL.relative_to(PROJECT_ROOT)),
        "warnings": [
            "Sensitive exact facts remain review_required and are not public-launch approval.",
            "No live website crawling was run.",
        ],
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    SUMMARY_MD.write_text(
        "\n".join(
            [
                "# Alte Desktop Study KB v3 Normalization Summary",
                "",
                f"- Source file: `{summary['source_file']}`",
                f"- Normalized records: `{summary['normalized_records']}`",
                f"- High sensitivity: `{summary['high_sensitivity_count']}`",
                f"- Review required: `{summary['review_required_count']}`",
                f"- Output: `{summary['output_path']}`",
                "",
                "Sensitive exact facts are review-required until a human reviewer approves official wording.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    records = normalize()
    summary = write_outputs(records)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
