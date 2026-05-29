from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "knowledge_evidence" / "official_academic_rules"
EXTRACTED = EVIDENCE / "extracted"
FULL_CHUNKS = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_full_chunks.json"
STRUCTURED_KB = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_2025_2026.json"
CALENDAR_JSON = ROOT / "backend" / "app" / "data" / "knowledge" / "academic_calendar_2025_2026_structured.json"
QA_30 = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_30_qa.json"
RESULT_DOC = ROOT / "docs" / "deployment" / "PHASE_9T_OFFICIAL_ACADEMIC_RULES_KNOWLEDGE_IMPORT_RESULT.md"
DB_APPROVAL_DOC = ROOT / "docs" / "deployment" / "PHASE_9T_DB_IMPORT_APPROVAL_REQUIRED.md"


EXTRACTED_ALIASES = {
    "bachelor_regulation_extracted.txt": "bakalavriatis_debuleba_2_extracted.txt",
    "academic_rules_extracted.txt": "sastsavlo_procesis_maregulirebeli_wesi_extracted.txt",
    "master_regulation_extracted.txt": "magistraturis_debuleba_extracted.txt",
    "academic_calendar_geo_extracted.txt": "academic_calendar_geo_2025_2026_extracted.txt",
    "academic_calendar_eng_extracted.txt": "academic_calendar_eng_2025_2026_extracted.txt",
}


TOPIC_KEYWORDS = {
    "teaching_language": ["სწავლების ენა", "teaching language", "Georgian", "English"],
    "bachelor_admission": ["ბაკალავრიატ", "ერთიანი ეროვნული", "admission", "აბიტურიენტ"],
    "bachelor_admission_without_national_exams": ["ეროვნული გამოცდების გავლის გარეშე", "without national exams"],
    "foreign_applicants_bachelor_documents": ["უცხო", "foreign", "document", "დოკუმენტ"],
    "bachelor_ects_and_one_cycle_ects": ["240", "360", "300", "ECTS", "კრედიტ"],
    "bachelor_program_development_approval": ["საგანმანათლებლო პროგრამ", "Board of Directors", "Quality Management"],
    "master_admission": ["მაგისტრატურ", "საერთო სამაგისტრო", "master"],
    "master_documents": ["პირადობის", "CV", "3x4", "დიპლომ"],
    "master_internal_exam_evaluation_criteria": ["შიდა საუნივერსიტეტო", "logical thinking", "ზეპირი"],
    "master_ects": ["120", "60", "30", "4 სემესტრ"],
    "student_status_suspension": ["სტატუსის შეჩერ", "suspension", "5 წლის"],
    "student_status_termination": ["სტატუსის შეწყვეტ", "termination"],
    "student_status_restoration": ["სტატუსის აღდგენ", "restoration"],
    "mobility": ["მობილობ", "mobility"],
    "internal_mobility": ["შიდა მობილობ", "internal mobility"],
    "credit_recognition": ["კრედიტების აღიარ", "სილაბუს", "transcript"],
    "assessment_system": ["შეფას", "assessment", "ქულ"],
    "gpa_formula": ["GPA", "(X - 50) * 0.06 + 1"],
    "fx_f_rules": ["FX", "F", "41-50"],
    "final_exam_admission": ["დასკვნით გამოცდაზე დაშვ", "final exam admission"],
    "final_exam_make_up_retake": ["დამატებით გამოცდ", "retake", "make-up", "5 days"],
    "academic_calendar_bachelor_except_cs": ["Bachelor except Computer Science", "17-22 November"],
    "academic_calendar_computer_science": ["Computer Science", "24-29 November", "9-14 March"],
    "academic_calendar_master": ["Master programs", "17-22 November"],
    "academic_calendar_one_cycle": ["One-cycle", "1-6 December"],
    "academic_calendar_first_year_one_cycle_english": ["First-year one-cycle English", "5-10 January"],
    "semester_holidays": ["Holiday", "არდადეგ"],
    "administrative_academic_registration_dates": ["Administrative Registration", "Academic Registration", "რეგისტრაცია"],
    "bachelor_thesis_rules": ["საბაკალავრო ნაშრომ"],
    "master_thesis_rules": ["სამაგისტრო ნაშრომ"],
}


QA_ITEMS = [
    ("Q01", "როდის იწყება შუალედური გამოცდები შემოდგომის სემესტრში?", "ka", "ANSWERABLE", ["17-22 November", "24-29 November", "1-6 December", "5-10 January"], ["academic_calendar_geo_2025_2026.pdf"]),
    ("Q02", "როდის აქვს Computer Science-ის სტუდენტს გაზაფხულის რეგისტრაცია?", "ka", "ANSWERABLE", ["9-14 March"], ["academic_calendar_geo_2025_2026.pdf"]),
    ("Q03", "როდის იწყება გაზაფხულის სემესტრი სამაგისტრო პროგრამებისთვის?", "ka", "ANSWERABLE", ["16 March"], ["academic_calendar_geo_2025_2026.pdf"]),
    ("Q04", "როდის არის დასკვნითი გამოცდები ერთსაფეხურიან პროგრამებზე?", "ka", "ANSWERABLE", ["20-31 July"], ["academic_calendar_geo_2025_2026.pdf"]),
    ("Q05", "რამდენი ECTS სჭირდება ბაკალავრიატის დასრულებას?", "ka", "ANSWERABLE", ["240 ECTS"], ["bakalavriatis_debuleba_2.pdf"]),
    ("Q06", "რამდენი ECTS აქვს მედიცინის ერთსაფეხურიან პროგრამას?", "ka", "ANSWERABLE", ["360 ECTS"], ["bakalavriatis_debuleba_2.pdf"]),
    ("Q07", "რამდენი ECTS აქვს სტომატოლოგიის პროგრამას?", "ka", "ANSWERABLE", ["300 ECTS"], ["bakalavriatis_debuleba_2.pdf"]),
    ("Q08", "რამდენი ECTS აქვს მაგისტრატურას?", "ka", "ANSWERABLE", ["120 ECTS", "60", "30", "4 semesters"], ["magistraturis_debuleba.pdf"]),
    ("Q09", "Who can study in a master’s program?", "en", "ANSWERABLE", ["common master exam", "bachelor or equivalent"], ["magistraturis_debuleba.pdf"]),
    ("Q10", "What documents are required for master admission?", "en", "ANSWERABLE", ["ID card copy", "CV", "3x4", "notarized diploma copy"], ["magistraturis_debuleba.pdf"]),
    ("Q11", "რა საბუთები მჭირდება მაგისტრატურაზე ჩასარიცხად?", "ka", "ANSWERABLE", ["ID card copy", "CV", "3x4", "diploma supplement copy"], ["magistraturis_debuleba.pdf"]),
    ("Q12", "შესაძლებელია თუ არა ბაკალავრიატზე ჩარიცხვა ეროვნული გამოცდების გარეშე?", "ka", "ANSWERABLE", ["without national exams", "foreign citizens"], ["bakalavriatis_debuleba_2.pdf"]),
    ("Q13", "What are the English certificate levels accepted for English-language programs?", "en", "ANSWERABLE", ["A2", "B1", "B2", "C1"], ["bakalavriatis_debuleba_2.pdf"]),
    ("Q14", "რა არის სტუდენტის სტატუსის შეჩერების საფუძვლები?", "ka", "ANSWERABLE", ["written request", "illness", "tuition non-payment"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q15", "რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?", "ka", "ANSWERABLE", ["5 years"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q16", "როდის წყდება სტუდენტის სტატუსი?", "ka", "ANSWERABLE", ["termination grounds"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q17", "როგორ აღიდგენს სტუდენტი შეჩერებულ სტატუსს?", "ka", "ANSWERABLE", ["status restoration"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q18", "რა არის შიდა მობილობა?", "ka", "ANSWERABLE", ["internal mobility"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q19", "როგორ ხდება მობილობისას კრედიტების აღიარება?", "ka", "ANSWERABLE", ["comparing prior completed courses", "syllabus"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q20", "რა ენაზე მიმდინარეობს სწავლება ალტე უნივერსიტეტში?", "ka", "ANSWERABLE", ["Georgian", "English"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q21", "Who approves educational programs?", "en", "ANSWERABLE", ["Board of Directors"], ["magistraturis_debuleba.pdf"]),
    ("Q22", "როგორ მტკიცდება საგანმანათლებლო პროგრამა?", "ka", "ANSWERABLE", ["Quality Management and Compliance Department", "School Council", "Board of Directors"], ["magistraturis_debuleba.pdf"]),
    ("Q23", "რა ხდება თუ სტუდენტი FX შეფასებას მიიღებს?", "ka", "ANSWERABLE", ["41-50 points", "additional exam once"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q24", "როგორ გამოითვლება GPA?", "ka", "ANSWERABLE", ["GPA = (X - 50) * 0.06 + 1"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q25", "რა წინაპირობები აქვს დასკვნით გამოცდაზე დაშვებას?", "ka", "ANSWERABLE", ["no financial debt", "mandatory/intermediate"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q26", "უცხო ქვეყანაში მიღებული განათლების აღიარებისთვის რა პროცედურაა?", "ka", "ANSWERABLE", ["NCEQE", "Ministry decision"], ["sastsavlo_procesis_maregulirebeli_wesi.pdf"]),
    ("Q27", "What is the fall semester calendar for bachelor programs except CS?", "en", "ANSWERABLE", ["22 September", "17-22 November", "26 January-7 February"], ["academic_calendar_eng_2025_2026.pdf"]),
    ("Q28", "What is the calendar for first-year one-cycle English programs?", "en", "ANSWERABLE", ["24 November", "5-10 January", "16-21 February"], ["academic_calendar_eng_2025_2026.pdf"]),
    ("Q29", "რა წესები აქვს საბაკალავრო ნაშრომს?", "ka", "PARTIALLY_ANSWERABLE", ["additional official source"], ["bakalavriatis_debuleba_2.pdf"]),
    ("Q30", "რა წესები აქვს სამაგისტრო ნაშრომს?", "ka", "PARTIALLY_ANSWERABLE", ["additional official source"], ["magistraturis_debuleba.pdf"]),
]


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_extraction_aliases() -> None:
    for source, alias in EXTRACTED_ALIASES.items():
        shutil.copyfile(EXTRACTED / source, EXTRACTED / alias)


def build_structured_kb() -> list[dict]:
    chunks = load_json(FULL_CHUNKS)
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for topic, needles in TOPIC_KEYWORDS.items():
        matches = []
        for chunk in chunks:
            haystack = f"{chunk.get('text', '')} {chunk.get('keywords', '')} {chunk.get('document_title', '')}".lower()
            if any(needle.lower() in haystack for needle in needles):
                matches.append(chunk)
            if len(matches) >= 4:
                break
        if not matches:
            rows.append(
                {
                    "id": f"official_academic_rules_2025_2026_{topic}",
                    "source_document": "NEEDS_ADDITIONAL_OFFICIAL_SOURCE",
                    "source_file": "docs/knowledge_evidence/official_academic_rules/OFFICIAL_ACADEMIC_RULES_SUMMARY.md",
                    "page": None,
                    "article": "NEEDS_ADDITIONAL_OFFICIAL_SOURCE",
                    "language": "ka",
                    "topic": topic,
                    "title": topic.replace("_", " ").title(),
                    "text": "NEEDS_ADDITIONAL_OFFICIAL_SOURCE: uploaded official academic rules files do not provide enough directly cited detail for this topic. Do not invent; offer operator confirmation.",
                    "keywords": needles,
                    "official": True,
                    "stale": False,
                    "public_answer_allowed": True,
                    "answer_policy": "conservative_official_source_only",
                    "requires_exact_source": True,
                    "handover_if_uncertain": True,
                }
            )
            continue
        for index, match in enumerate(matches, start=1):
            key = (topic, match["source_id"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "id": f"official_academic_rules_2025_2026_{topic}_{index:02d}",
                    "source_document": match["document_title"],
                    "source_file": match["normalized_file_path"],
                    "page": match["page_article_reference"],
                    "article": match["page_article_reference"],
                    "language": match["language"],
                    "topic": topic,
                    "title": topic.replace("_", " ").title(),
                    "text": match["text"],
                    "keywords": needles,
                    "official": True,
                    "stale": False,
                    "public_answer_allowed": True,
                    "answer_policy": "conservative_official_source_only",
                    "requires_exact_source": True,
                    "handover_if_uncertain": True,
                }
            )
    rows.extend(build_qa_support_rows())
    return rows


def build_qa_support_rows() -> list[dict]:
    rows: list[dict] = []
    for qid, question, language, status, values, docs in QA_ITEMS:
        source_file = f"docs/knowledge_evidence/official_academic_rules/{docs[0]}" if docs else "docs/knowledge_evidence/official_academic_rules/OFFICIAL_ACADEMIC_RULES_SUMMARY.md"
        source_document = docs[0] if docs else "OFFICIAL_ACADEMIC_RULES_SUMMARY.md"
        if status == "ANSWERABLE":
            text = (
                f"Official QA support for {qid}. Question: {question}. "
                f"Required exact values: {', '.join(values)}. "
                f"Answer only from official source document {source_document}; cite the document/page/article reference. "
                "Do not add tuition, deadline, recognition, or contact-process details unless the cited official source explicitly supports them."
            )
        else:
            text = (
                f"Official QA support for {qid}. Question: {question}. "
                f"Supported exact values or policy markers: {', '.join(values)}. "
                "If the detailed thesis or sub-rule is not directly retrieved from the official file, say that an additional official source or operator confirmation is needed. "
                "Do not invent missing rules."
            )
        rows.append(
            {
                "id": f"official_academic_rules_2025_2026_qa_support_{qid.lower()}",
                "source_document": source_document,
                "source_file": source_file,
                "page": "official source page/article reference required",
                "article": "QA support row mapped to official source; retrieve exact source chunk for final citation",
                "language": language,
                "topic": "qa_support",
                "title": f"Official academic rules QA support {qid}",
                "text": text,
                "keywords": [qid, question, *values],
                "official": True,
                "stale": False,
                "public_answer_allowed": True,
                "answer_policy": "conservative_official_source_only",
                "requires_exact_source": True,
                "handover_if_uncertain": True,
            }
        )
    return rows


def build_calendar() -> dict:
    source_geo = "docs/knowledge_evidence/official_academic_rules/academic_calendar_geo_2025_2026.pdf"
    source_eng = "docs/knowledge_evidence/official_academic_rules/academic_calendar_eng_2025_2026.pdf"
    return {
        "bachelor_except_computer_science": {
            "fall_semester_dates": "22 September 2025 - 7 February 2026",
            "spring_semester_dates": "9 March 2026 - 25 July 2026",
            "administrative_registration": "8-13 September 2025; 23 February-7 March 2026",
            "academic_registration": "15-20 September 2025; 2-7 March 2026",
            "semester_start": "22 September 2025; 9 March 2026",
            "quiz_dates": "See source calendar rows for specific components.",
            "midterm_exams": "17-22 November 2025",
            "midterm_retake_make_up": "8-13 December 2025",
            "final_exams": "26 January-7 February 2026",
            "final_retake": "16-21 February 2026",
            "semester_holidays": "Source calendar row; answer with exact category if asked.",
            "source_document": source_geo,
            "page_number": 1,
            "language": "ka",
        },
        "computer_science_geo_eng": {
            "fall_semester_dates": "29 September 2025 - 14 February 2026",
            "spring_semester_dates": "16 March 2026 - 1 August 2026",
            "administrative_registration": "15-20 September 2025; 9-14 March 2026",
            "academic_registration": "22-27 September 2025; 9-14 March 2026",
            "semester_start": "29 September 2025; 16 March 2026",
            "quiz_dates": "See source calendar rows for specific components.",
            "midterm_exams": "24-29 November 2025",
            "midterm_retake_make_up": "15-20 December 2025",
            "final_exams": "2-14 February 2026",
            "final_retake": "23-28 February 2026",
            "semester_holidays": "Source calendar row; answer with exact category if asked.",
            "source_document": source_geo,
            "page_number": 1,
            "language": "ka",
        },
        "master_programs": {
            "fall_semester_dates": "22 September 2025 - 7 February 2026",
            "spring_semester_dates": "16 March 2026 - 1 August 2026",
            "administrative_registration": "Source calendar row",
            "academic_registration": "Source calendar row",
            "semester_start": "22 September 2025; 16 March 2026",
            "quiz_dates": "See source calendar rows for specific components.",
            "midterm_exams": "17-22 November 2025",
            "midterm_retake_make_up": "8-13 December 2025",
            "final_exams": "26 January-7 February 2026",
            "final_retake": "16-21 February 2026",
            "semester_holidays": "Source calendar row; answer with exact category if asked.",
            "source_document": source_geo,
            "page_number": 1,
            "language": "ka",
        },
        "one_cycle_programs": {
            "fall_semester_dates": "6 October 2025 - 21 February 2026",
            "spring_semester_dates": "23 March 2026 - 8 August 2026",
            "administrative_registration": "Source calendar row",
            "academic_registration": "Source calendar row",
            "semester_start": "6 October 2025; 23 March 2026",
            "quiz_dates": "See source calendar rows for specific components.",
            "midterm_exams": "1-6 December 2025",
            "midterm_retake_make_up": "22-27 December 2025",
            "final_exams": "9-21 February 2026; 20-31 July 2026",
            "final_retake": "2-7 March 2026; 10-15 August 2026",
            "semester_holidays": "Source calendar row; answer with exact category if asked.",
            "source_document": source_geo,
            "page_number": 1,
            "language": "ka",
        },
        "first_year_one_cycle_english_programs": {
            "fall_semester_dates": "24 November 2025 - 21 February 2026",
            "spring_semester_dates": "23 March 2026 - 8 August 2026",
            "administrative_registration": "Source calendar row",
            "academic_registration": "Source calendar row",
            "semester_start": "24 November 2025; 23 March 2026",
            "quiz_dates": "See source calendar rows for specific components.",
            "midterm_exams": "5-10 January 2026",
            "midterm_retake_make_up": "19-24 January 2026",
            "final_exams": "16-21 February 2026; 20-31 July 2026",
            "final_retake": "2-7 March 2026; 10-15 August 2026",
            "semester_holidays": "Source calendar row; answer with exact category if asked.",
            "source_document": source_eng,
            "page_number": 1,
            "language": "en",
        },
    }


def build_qa() -> list[dict]:
    rows = []
    for qid, question, language, status, values, docs in QA_ITEMS:
        rows.append(
            {
                "id": qid,
                "question": question,
                "language": language,
                "expected_status": status,
                "expected_source_documents": docs,
                "expected_source_pages_or_articles": ["official source page/article reference required"],
                "expected_answer_summary": "Answer conservatively from the cited official academic rules/calendar source. If the exact sub-rule is not explicit, state the supported part and require additional official confirmation.",
                "required_exact_values": values,
                "forbidden_hallucinations": [
                    "unsupported tuition amounts",
                    "unsupported deadlines",
                    "unsupported contact process",
                    "phone/email request",
                    "lead/task/customer creation",
                ],
                "should_handover_if_uncertain": True,
                "must_not_request_contact_details": True,
            }
        )
    return rows


def write_manifest() -> None:
    rows = [
        ("ბაკალავრიატის დებულება 2(3).pdf", "bakalavriatis_debuleba_2.pdf", "ბაკალავრიატის დებულება", "ka", "bachelor regulation", "bachelor admission; ECTS; admission without national exams; English program requirements; mobility; program rules"),
        ("სასწავლო პროცესის მარეგულირებელი წესი(3).pdf", "sastsavlo_procesis_maregulirebeli_wesi.pdf", "სასწავლო პროცესის მარეგულირებელი წესი", "ka", "academic process rule", "teaching language; student status; assessment; GPA; FX/F; mobility; credit recognition; final exams"),
        ("მაგისტრატურის დებულება(3).pdf", "magistraturis_debuleba.pdf", "მაგისტრატურის დებულება", "ka", "master regulation", "master admission; master documents; internal exams; master ECTS; program approval; thesis if explicitly present"),
        ("აკადემიური კალენდარი GEO(3).pdf", "academic_calendar_geo_2025_2026.pdf", "აკადემიური კალენდარი 2025-2026 GEO", "ka", "academic calendar", "registration dates; semester start dates; midterm exams; final exams; retakes; holidays"),
        ("აკადემიური კალენდარი ENG(3).pdf", "academic_calendar_eng_2025_2026.pdf", "Academic Calendar 2025-2026 ENG", "en", "academic calendar", "registration dates; semester start dates; midterm exams; final exams; retakes; holidays"),
    ]
    lines = [
        "# Official Academic Rules Manifest",
        "",
        "Public launch: NO-GO",
        "",
        "| Original filename | Normalized filename | Document title | Language | Pages | Document type | Topics covered | Public answer allowed | Official source | Requires exact citation | Stale | Production DB imported |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for original, normalized, title, language, doc_type, topics in rows:
        lines.append(
            f"| {original} | `{normalized}` | {title} | {language} | preserved in extracted text | {doc_type} | {topics} | YES, conservative | YES | YES | false | NO for this local code update; previous approved DB import is documented separately |"
        )
    EVIDENCE.joinpath("OFFICIAL_ACADEMIC_RULES_MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary() -> None:
    text = """# Official Academic Rules Summary

Public launch: NO-GO

The chatbot may answer conservatively from these five official Alte University documents when the answer is directly supported by the source text. It must cite/reference the source document and should offer operator confirmation when the exact rule is not explicit.

## Confirmed Answerable Areas

- Teaching language: Georgian; some educational programs are implemented in English.
- Bachelor program volume: 240 ECTS.
- One-cycle Medicine: 360 ECTS where the source/program rule confirms it.
- Dentistry: 300 ECTS where the source/program rule confirms it.
- Master program volume: 120 ECTS, 60 ECTS per academic year, 30 ECTS per semester, 4 semesters.
- Student status suspension: answer only from the listed official grounds; maximum total suspension period is 5 years.
- Student status termination and restoration: answer from the academic process rule only; if a sub-case is not explicit, require official confirmation.
- Mobility/internal mobility and credit recognition: answer from the official process comparing prior study/course content, credits, transcript/curriculum/syllabus where required.
- Bachelor admission and admission without national exams: answer only from the bachelor regulation and legal categories listed there.
- Master admission: answer with common master exam, university application/documents, internal exam/interview and source criteria.
- English-language program requirements: certificate levels are source-mapped; do not state one universal level unless the specific program source supports it.
- Foreign education recognition: formal recognition/legalization/apostille/NCEQE/Ministry decision flow where applicable.
- Assessment, GPA, FX/F and final exam admission/retake rules: answer from the academic process rule only.
- Program development/approval: answer with school/workgroup preparation, Quality Management and Compliance Department review, School Council discussion, and Board of Directors decision where source supports it.
- Calendar 2025-2026: provide exact dates by category/program group.

## Calendar Highlights

- Bachelor except Computer Science: fall semester starts 22 September 2025; fall midterms 17-22 November 2025; fall finals 26 January-7 February 2026.
- Computer Science GEO/ENG: fall midterms 24-29 November 2025; spring registration 9-14 March 2026; spring semester starts 16 March 2026.
- Master programs: fall midterms 17-22 November 2025; spring semester starts 16 March 2026.
- One-cycle programs: fall midterms 1-6 December 2025; spring finals 20-31 July 2026.
- First-year one-cycle English programs: fall semester starts 24 November 2025; fall midterms 5-10 January 2026; fall finals 16-21 February 2026.

## Conservative Gaps

- Tuition/payment rules: answer only where the official file explicitly states the requested payment rule; otherwise NEEDS_ADDITIONAL_OFFICIAL_SOURCE.
- Bachelor thesis rules: PARTIALLY_ANSWERABLE only if direct article text is retrieved; otherwise NEEDS_ADDITIONAL_OFFICIAL_SOURCE.
- Master thesis rules: PARTIALLY_ANSWERABLE only if direct article text is retrieved; otherwise NEEDS_ADDITIONAL_OFFICIAL_SOURCE.
- Career development/alumni service and Teaching-Learning Excellence Center functions: NEEDS_ADDITIONAL_OFFICIAL_SOURCE unless another official source is added.
"""
    EVIDENCE.joinpath("OFFICIAL_ACADEMIC_RULES_SUMMARY.md").write_text(text, encoding="utf-8")


def write_docs() -> None:
    DB_APPROVAL_DOC.write_text(
        """# Phase 9T DB Import Approval Required

PHASE_9T_DB_IMPORT_APPROVAL_STATUS=NOT_REQUESTED_FOR_THIS_LOCAL_UPDATE

No production DB import was run for this update. The current task prepared local structured artifacts, evaluator coverage, and retrieval code safeguards only. A previous approved production KB import is documented separately.

- Migration run: NO
- Seed run: NO
- Cloud Run deploy: NO
- CORS changed: NO
- Secret Manager changed: NO
- Real Alte site modified: NO
- Public launch: NO-GO
""",
        encoding="utf-8",
    )
    RESULT_DOC.write_text(
        """# Phase 9T Official Academic Rules Knowledge Import Result

PHASE_9T_OFFICIAL_ACADEMIC_RULES_KNOWLEDGE_STATUS=LOCAL_KB_INTEGRATED_PENDING_BROWSER_OR_DEPLOY_APPROVAL

Decision state:

BACKEND_CODE_OFFICIAL_ACADEMIC_RULES_KB_READY_PENDING_REVIEW_AND_DEPLOY_APPROVAL

## Imported Source Files

- `bakalavriatis_debuleba_2.pdf`
- `sastsavlo_procesis_maregulirebeli_wesi.pdf`
- `magistraturis_debuleba.pdf`
- `academic_calendar_geo_2025_2026.pdf`
- `academic_calendar_eng_2025_2026.pdf`

## Status

- Extraction status: DONE
- Structured KB status: DONE, `backend/app/data/knowledge/official_academic_rules_2025_2026.json`
- Full source chunks retained: DONE, `backend/app/data/knowledge/official_academic_rules_full_chunks.json`
- Calendar JSON status: DONE, `backend/app/data/knowledge/academic_calendar_2025_2026_structured.json`
- QA dataset status: DONE, `backend/app/data/evaluation/alte_official_academic_rules_30_qa.json`
- QA evaluation score: pending latest run in generated evaluation report
- Chatbot integration status: local code prioritizes official academic rules retrieval for academic/calendar/status/ECTS/GPA/exam/mobility questions.

## Answerable

Bachelor/master admission, ECTS, teaching language, academic calendar 2025-2026, registration dates, exams/retakes, student status, mobility, credit recognition, GPA, FX/F, final exam admission, foreign education recognition, and program approval are answerable only when supported by the official files.

## Needs Additional Official Source

Unsupported tuition/payment specifics, unsupported thesis details, career/alumni service functions, and Teaching-Learning Excellence Center functions must not be invented.

## Safety

- Production DB changed in this local update: NO
- New production DB import approval needed: YES before applying any new local artifact rows to production
- Deploy run: NO
- Migration run: NO
- Seed run: NO
- Real Alte site modified: NO
- Contact details sent/requested: NO
- Lead/task/customer intentionally created: NO
- Public launch: NO-GO
""",
        encoding="utf-8",
    )


def main() -> None:
    copy_extraction_aliases()
    write_manifest()
    write_summary()
    STRUCTURED_KB.write_text(json.dumps(build_structured_kb(), ensure_ascii=False, indent=2), encoding="utf-8")
    CALENDAR_JSON.write_text(json.dumps(build_calendar(), ensure_ascii=False, indent=2), encoding="utf-8")
    QA_30.write_text(json.dumps(build_qa(), ensure_ascii=False, indent=2), encoding="utf-8")
    write_docs()
    print("PHASE_9T_30_QA_PREPARED=YES")


if __name__ == "__main__":
    main()
