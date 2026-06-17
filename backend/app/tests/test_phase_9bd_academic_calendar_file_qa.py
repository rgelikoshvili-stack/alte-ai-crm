from __future__ import annotations

import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
QA_SET_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9bd_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9bd_academic_calendar_file_qa")
    assert hasattr(verifier, "run_checks")


def test_phase_9bd_docs_exist():
    assert QA_SET_DOC.exists()
    assert RESULT_DOC.exists()


def test_phase_9bd_expected_key_dates_appear_in_qa_docs():
    text = read(QA_SET_DOC) + "\n" + read(RESULT_DOC)
    for expected in [
        "29 September 2025",
        "9 - 14 March 2026",
        "30 March 2026",
        "13 - 25 July 2026",
        "29 June - 11 July 2026",
        "20 July - 1 August 2026",
        "3 - 8 August 2026",
        "30 December 2025 - 4 January 2026",
        "10 - 13 April 2026",
    ]:
        assert expected in text


def test_phase_9bd_required_questions_appear():
    text = read(QA_SET_DOC) + "\n" + read(RESULT_DOC)
    for question in [
        "საბაკალავრო პროგრამებისთვის შემოდგომის სემესტრი როდის იწყება?",
        "Computer Science-ის გაზაფხულის სემესტრის რეგისტრაცია როდის არის?",
        "Computer Science-ის გაზაფხულის დასკვნითი გამოცდები როდის არის?",
        "სამაგისტრო პროგრამებისთვის გაზაფხულის სემესტრი როდის იწყება?",
        "ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?",
        "When does the fall semester start for Bachelor programs except Computer Science?",
        "When is academic registration for Computer Science in spring?",
        "When do spring final exams take place for Computer Science?",
        "What are the New Year holidays?",
        "What are the Easter holidays?",
        "2031 წლის გაზაფხულის სემესტრი როდის იწყება?",
        "2027 წლის Computer Science-ის გამოცდები როდისაა?",
    ]:
        assert question in text


def test_phase_9bd_result_summary_exists():
    text = read(RESULT_DOC)
    assert "PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_STATUS=COMPLETED" in text
    assert "Total tests:" in text
    assert "PASS count:" in text
    assert "PARTIAL count:" in text
    assert "FAIL count:" in text
    assert text.count("\nFile:") >= 20


def test_phase_9bd_safety_claims_exist():
    text = read(RESULT_DOC)
    assert "Public launch: `NO-GO`" in text
    assert "Public launch remains: NO-GO" in text
    assert "Real site modified: NO" in text
    assert "Assets uploaded or embedded: NO" in text
    assert "Frontend/Netlify changed: NO" in text
    assert "DB schema/migration/seed/import changed or run: NO" in text
    assert "Secret Manager changed: NO" in text
    assert "CORS changed: NO" in text
    assert "Bridge Hub touched: NO" in text
    assert "Contact flow submitted: NO" in text
    assert "Lead/customer/task created: NO" in text
    assert "Lead/customer/task created: YES" not in text
