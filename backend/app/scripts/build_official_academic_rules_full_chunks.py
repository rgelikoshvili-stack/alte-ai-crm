from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "official_academic_rules"
EXTRACTED_DIR = EVIDENCE_DIR / "extracted"
OUTPUT_PATH = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_full_chunks.json"


DOCS = [
    {
        "extracted": "academic_rules_extracted.txt",
        "pdf": "sastsavlo_procesis_maregulirebeli_wesi.pdf",
        "title": "სასწავლო პროცესის მარეგულირებელი წესი",
        "language": "ka",
        "topic": "academic_rules",
    },
    {
        "extracted": "bachelor_regulation_extracted.txt",
        "pdf": "bakalavriatis_debuleba_2.pdf",
        "title": "ბაკალავრიატის დებულება",
        "language": "ka",
        "topic": "bachelor_regulation",
    },
    {
        "extracted": "master_regulation_extracted.txt",
        "pdf": "magistraturis_debuleba.pdf",
        "title": "მაგისტრატურის დებულება",
        "language": "ka",
        "topic": "master_regulation",
    },
    {
        "extracted": "academic_calendar_geo_extracted.txt",
        "pdf": "academic_calendar_geo_2025_2026.pdf",
        "title": "აკადემიური კალენდარი 2025-2026 GEO",
        "language": "ka",
        "topic": "academic_calendar",
    },
    {
        "extracted": "academic_calendar_eng_extracted.txt",
        "pdf": "academic_calendar_eng_2025_2026.pdf",
        "title": "Academic Calendar 2025-2026 ENG",
        "language": "en",
        "topic": "academic_calendar",
    },
]


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pages_from_extracted(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^===== PAGE (\d+) =====$", text, flags=re.MULTILINE))
    pages: list[tuple[int, str]] = []
    for index, match in enumerate(matches):
        page_no = int(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        page_text = normalize_text(text[start:end])
        if page_text:
            pages.append((page_no, page_text))
    return pages


def split_chunks(text: str, max_chars: int = 1800) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        paragraphs = [text]
    chunks: list[str] = []
    buffer: list[str] = []
    size = 0
    for paragraph in paragraphs:
        paragraph_size = len(paragraph)
        heading_like = len(paragraph) <= 140 and bool(
            re.search(r"(მუხლი|თავი|Article|Final Exams|Midterm|Registration|Semester|დანართი)", paragraph, re.I)
        )
        if buffer and (size + paragraph_size > max_chars or (heading_like and size > 900)):
            chunks.append("\n\n".join(buffer).strip())
            buffer = []
            size = 0
        if paragraph_size > max_chars:
            words = paragraph.split()
            piece: list[str] = []
            piece_size = 0
            for word in words:
                if piece and piece_size + len(word) + 1 > max_chars:
                    chunks.append(" ".join(piece).strip())
                    piece = []
                    piece_size = 0
                piece.append(word)
                piece_size += len(word) + 1
            if piece:
                chunks.append(" ".join(piece).strip())
        else:
            buffer.append(paragraph)
            size += paragraph_size + 2
    if buffer:
        chunks.append("\n\n".join(buffer).strip())
    return [chunk for chunk in chunks if len(chunk) >= 40]


def detect_reference(text: str, page: int, chunk_index: int) -> str:
    for line in text.splitlines()[:8]:
        clean = line.strip()
        if re.search(r"მუხლი\s+\d+|თავი\s+[IVX\d]+|Article\s+\d+|Final Exams|Midterm|Registration|Semester", clean, re.I):
            return f"page {page}; {clean[:120]}"
    return f"page {page}; chunk {chunk_index}"


def keywords(text: str, topic: str) -> str:
    words = [topic]
    for word in re.findall(r"[A-Za-zა-ჰ0-9][A-Za-zა-ჰ0-9\-]{2,}", text):
        lowered = word.lower()
        if lowered not in words:
            words.append(lowered)
        if len(words) >= 28:
            break
    return ", ".join(words)


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for doc_index, doc in enumerate(DOCS, start=1):
        pages = pages_from_extracted(EXTRACTED_DIR / doc["extracted"])
        doc_chunk_index = 0
        for page, text in pages:
            for chunk in split_chunks(text):
                doc_chunk_index += 1
                source_id = f"official_academic_rules_full_{doc_index:02d}_p{page:03d}_c{doc_chunk_index:03d}"
                rows.append(
                    {
                        "source_id": source_id,
                        "document_title": doc["title"],
                        "normalized_file_path": f"docs/knowledge_evidence/official_academic_rules/{doc['pdf']}",
                        "page_article_reference": detect_reference(chunk, page, doc_chunk_index),
                        "language": doc["language"],
                        "topic": doc["topic"],
                        "text": chunk,
                        "answer_policy": "answer only from this official source; handover if the answer is not supported",
                        "sensitivity": "official academic rule / academic calendar",
                        "public_answer_allowed": True,
                        "requires_exact_source": True,
                        "stale": False,
                        "official": True,
                        "keywords": keywords(chunk, doc["topic"]),
                    }
                )
    return rows


def main() -> None:
    rows = build_rows()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    by_doc: dict[str, int] = {}
    for row in rows:
        by_doc[row["document_title"]] = by_doc.get(row["document_title"], 0) + 1
    print(json.dumps({"full_chunk_count": len(rows), "chunks_by_document": by_doc}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
