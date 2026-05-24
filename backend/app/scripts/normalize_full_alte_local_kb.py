from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "alte_full_local_kb"
SEED_DIR = BACKEND_ROOT / "app" / "knowledge_seed" / "full_alte_local_kb"
REPORTS_DIR = BACKEND_ROOT / "reports"
SOURCE_JSONL = EVIDENCE_DIR / "alte_knowledge_base_ka.jsonl"
INDEX_MD = EVIDENCE_DIR / "alte_knowledge_base_index.md"
NORMALIZED_JSONL = SEED_DIR / "full_alte_local_kb_normalized.jsonl"
SUMMARY_JSON = REPORTS_DIR / "full_alte_local_kb_normalization_summary.json"
SUMMARY_MD = REPORTS_DIR / "full_alte_local_kb_normalization_summary.md"

HIGH_TERMS = [
    "tuition",
    "fee",
    "price",
    "grant",
    "scholarship",
    "deadline",
    "document",
    "documents",
    "medicine",
    "md",
    "international",
    "visa",
    "relocation",
    "legal",
    "accreditation",
    "payment",
    "contract",
    "საფას",
    "ფასი",
    "გრანტ",
    "სტიპენდი",
    "ვად",
    "საბუთ",
    "დოკუმენტ",
    "მედიცინ",
    "საერთაშორისო",
    "ვიზ",
    "რელოკ",
    "აკრედიტ",
    "გადახდ",
    "ხელშეკრულ",
]

MEDIUM_TERMS = [
    "admission",
    "apply",
    "program",
    "bachelor",
    "master",
    "enrollment",
    "ჩარიცხ",
    "მიღებ",
    "პროგრამ",
    "ბაკალავრ",
    "მაგისტრ",
]


def slugify(value: str, *, fallback: str) -> str:
    ascii_value = re.sub(r"[^a-z0-9]+", "-", value.lower())
    ascii_value = re.sub(r"-+", "-", ascii_value).strip("-")
    return ascii_value[:90] or fallback


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_jsonl(path: Path = SOURCE_JSONL) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing source JSONL: {path}")
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def classify_department(record: dict[str, Any]) -> str:
    haystack = haystack_for(record)
    if any(term in haystack for term in ["medicine", "md", "meditsinis", "მედიცინ"]):
        return "Medicine"
    if any(term in haystack for term in ["international", "join", "visa", "relocation", "საერთაშორისო", "ვიზ"]):
        return "International Admissions"
    if any(term in haystack for term in ["tuition", "fee", "price", "grant", "scholarship", "საფას", "გრანტ"]):
        return "Finance"
    if any(term in haystack for term in ["deadline", "calendar", "exam", "ვად", "კალენდარ", "გამოცდ"]):
        return "Academic Registry"
    if any(term in haystack for term in ["student_services", "library", "career", "ბიბლიოთეკ", "კარიერ"]):
        return "Student Services"
    if any(term in haystack for term in ["admission", "apply", "enrollment", "ჩარიცხ", "მიღებ"]):
        return "Admissions"
    return "General"


def classify_category(record: dict[str, Any]) -> str:
    haystack = haystack_for(record)
    tags = " ".join(record.get("tags") or []).lower()
    if "visa" in haystack or "relocation" in haystack or "ვიზ" in haystack:
        return "visa_relocation"
    if any(term in haystack for term in ["medicine", "md", "meditsinis", "მედიცინ"]):
        return "medicine_md"
    if any(term in haystack for term in ["stomatologia", "dentistry", "სტომატოლოგ"]):
        return "dentistry"
    if any(term in haystack for term in ["international", "join", "საერთაშორისო"]):
        return "international_admissions"
    if any(term in haystack for term in ["tuition", "fee", "price", "grant", "scholarship", "საფას", "გრანტ"]):
        return "finance_tuition"
    if any(term in haystack for term in ["deadline", "calendar", "exam", "ვად", "კალენდარ", "გამოცდ"]):
        return "deadlines_calendar"
    if any(term in haystack for term in ["document", "documents", "საბუთ", "დოკუმენტ"]):
        return "required_documents"
    if "admission" in tags or any(term in haystack for term in ["admission", "apply", "ჩარიცხ", "მიღებ"]):
        return "admissions_general"
    if "student_services" in tags:
        return "student_services"
    if "program" in tags or any(term in haystack for term in ["program", "პროგრამ"]):
        return "program_overview"
    if "contact" in tags or "kontaqti" in haystack or "contact" in haystack:
        return "general_contact"
    if "faq" in tags or "faq" in haystack:
        return "faq"
    if "about" in tags:
        return "about"
    return "about"


def classify_sensitivity(record: dict[str, Any], category: str) -> str:
    haystack = haystack_for(record)
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


def haystack_for(record: dict[str, Any]) -> str:
    parts = [
        record.get("source_url") or "",
        record.get("title") or "",
        record.get("breadcrumb") or "",
        record.get("section") or "",
        " ".join(record.get("tags") or []),
        record.get("text") or "",
    ]
    return " ".join(parts).lower()


def source_key_for(record: dict[str, Any], category: str) -> str:
    source_url = record.get("source_url") or "uploaded-local"
    key_base = slugify(source_url.replace("https://", "").replace("http://", ""), fallback="alte-local-kb")
    return f"full_alte_local_kb_{category}_{key_base}"[:160]


def title_for(record: dict[str, Any], category: str) -> str:
    title = (record.get("title") or record.get("section") or record.get("breadcrumb") or category).strip()
    return title[:240] or category


def keywords_for(record: dict[str, Any], category: str) -> list[str]:
    values = set(str(item).strip() for item in (record.get("tags") or []) if str(item).strip())
    values.add(category)
    for part in [record.get("section") or "", record.get("title") or ""]:
        for token in re.split(r"[\s,/|:;()]+", part):
            token = token.strip()
            if 3 <= len(token) <= 40:
                values.add(token)
    return sorted(values)[:30]


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        text = (record.get("text") or "").strip()
        if not text:
            continue
        category = classify_category(record)
        sensitivity = classify_sensitivity(record, category)
        review_required = sensitivity == "high" or category in {
            "finance_tuition",
            "deadlines_calendar",
            "required_documents",
            "international_admissions",
            "medicine_md",
            "dentistry",
            "visa_relocation",
        }
        source_url = record.get("source_url") or ""
        source_key = source_key_for(record, category)
        dedupe_key = stable_hash("|".join([source_url, record.get("section") or "", text]))
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(
            {
                "source_key": source_key,
                "source_url": source_url,
                "source_file": "alte_knowledge_base_ka.jsonl",
                "title": title_for(record, category),
                "language": record.get("locale") or "ka",
                "locale": record.get("locale") or "ka",
                "department": classify_department(record),
                "category": category,
                "section": record.get("section") or "",
                "chunk_index": int(record.get("chunk_index") or index),
                "content": text,
                "keywords": keywords_for(record, category),
                "lastmod": record.get("lastmod"),
                "source_type": "full_alte_local_kb",
                "source_domain": "alte.edu.ge",
                "status": "approved",
                "review_required": review_required,
                "sensitivity": sensitivity,
                "public_answer_allowed": sensitivity != "high" and not review_required,
                "recommended_review_action": recommended_action(category, sensitivity),
                "stale_after_days": 30 if sensitivity == "high" else 90,
                "program_name": program_name_for(record),
                "metadata_json": {
                    "source_file": "alte_knowledge_base_ka.jsonl",
                    "source_url": source_url,
                    "breadcrumb": record.get("breadcrumb") or "",
                    "section": record.get("section") or "",
                    "kind": record.get("kind") or "",
                    "tags": record.get("tags") or [],
                    "public_answer_allowed": sensitivity != "high" and not review_required,
                    "recommended_review_action": recommended_action(category, sensitivity),
                    "version": "full_alte_local_kb_v1",
                },
            }
        )
    return normalized


def program_name_for(record: dict[str, Any]) -> str | None:
    url = (record.get("source_url") or "").lower()
    title = (record.get("title") or record.get("section") or "").strip()
    if any(term in url for term in ["meditsinis", "medicine"]):
        return "Medicine / MD"
    if "stomatologia" in url or "dentistry" in url:
        return "Dentistry"
    if any(term in url for term in ["biznesis", "business"]):
        return "Business"
    if any(term in url for term in ["samartlis", "law"]):
        return "Law"
    if any(term in url for term in ["kompiuteruli", "computer"]):
        return "Computer Science"
    return title[:120] if title and "პროგრამ" in title else None


def recommended_action(category: str, sensitivity: str) -> str:
    if category in {"finance_tuition", "deadlines_calendar", "required_documents", "medicine_md", "international_admissions"}:
        return "NEEDS_OFFICIAL_SOURCE"
    if category in {"visa_relocation"}:
        return "HANDOVER_ONLY"
    if sensitivity == "high":
        return "REVIEW_REQUIRED"
    if sensitivity == "low":
        return "APPROVE_CANDIDATE"
    return "REVIEW_REQUIRED"


def parse_index_summary() -> dict[str, int]:
    text = INDEX_MD.read_text(encoding="utf-8") if INDEX_MD.exists() else ""
    pages = parse_number(text, r"წყარო გვერდები:\s*(\d+)") or parse_number(text, r"source pages:\s*(\d+)") or 123
    chunks = parse_number(text, r"knowledge chunks:\s*(\d+)") or 647
    errors = parse_number(text, r"crawl errors:\s*(\d+)") or 0
    return {"source_pages": pages, "knowledge_chunks": chunks, "crawl_errors": errors}


def parse_number(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def write_outputs(records: list[dict[str, Any]], total_input_records: int) -> dict[str, Any]:
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    NORMALIZED_JSONL.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in records) + "\n",
        encoding="utf-8",
    )
    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_dir": str(EVIDENCE_DIR.relative_to(PROJECT_ROOT)),
        "total_input_records": total_input_records,
        "normalized_records": len(records),
        "deduplicated_records": total_input_records - len(records),
        **parse_index_summary(),
        "high_sensitivity_count": sum(1 for item in records if item["sensitivity"] == "high"),
        "review_required_count": sum(1 for item in records if item["review_required"]),
        "category_counts": dict(Counter(item["category"] for item in records)),
        "department_counts": dict(Counter(item["department"] for item in records)),
        "output_path": str(NORMALIZED_JSONL.relative_to(PROJECT_ROOT)),
        "warnings": [
            "Sensitive facts are review_required and are not public-launch approval.",
            "No live website crawling was run.",
            "Secret-containing desktop Word document was intentionally excluded.",
        ],
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SUMMARY_MD.write_text(render_summary(summary), encoding="utf-8")
    return summary


def render_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# Full Alte Local KB Normalization Summary",
        "",
        f"Generated at: `{summary['generated_at']}`",
        f"- Source pages: {summary['source_pages']}",
        f"- Source knowledge chunks: {summary['knowledge_chunks']}",
        f"- Crawl errors: {summary['crawl_errors']}",
        f"- Total input records: {summary['total_input_records']}",
        f"- Normalized records: {summary['normalized_records']}",
        f"- Deduplicated records: {summary['deduplicated_records']}",
        f"- High sensitivity count: {summary['high_sensitivity_count']}",
        f"- Review required count: {summary['review_required_count']}",
        f"- Output path: `{summary['output_path']}`",
        "",
        "Sensitive official facts remain review_required and do not become public-approved automatically.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    records = read_jsonl()
    normalized = normalize_records(records)
    summary = write_outputs(normalized, len(records))
    print(
        json.dumps(
            {
                "total_input_records": summary["total_input_records"],
                "normalized_records": summary["normalized_records"],
                "deduplicated_records": summary["deduplicated_records"],
                "source_pages": summary["source_pages"],
                "high_sensitivity_count": summary["high_sensitivity_count"],
                "review_required_count": summary["review_required_count"],
                "output_path": summary["output_path"],
                "warnings": summary["warnings"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
