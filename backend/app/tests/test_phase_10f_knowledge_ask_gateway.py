import asyncio
import re

from sqlalchemy import func, select

from app.models import Customer, Lead, Task


def ask(client, question: str, **payload):
    response = client.post("/api/knowledge/ask", json={"question": question, **payload})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["used_claude"] is False
    label = data.get("public_source_label") or ""
    assert "source_group" not in label
    assert "official_academic_rules" not in label
    assert "chunk" not in label.lower()
    return data


def test_phase_10f_calendar_exact_answers_and_unsupported_year(client):
    bachelor_registration = ask(client, "ბაკალავრიატის გაზაფხულის რეგისტრაცია როდის არის?")
    assert bachelor_registration["status"] == "answered"
    assert bachelor_registration["source_group"] == "academic_calendar_2025_2026"
    assert "23 - 28 February 2026" in bachelor_registration["answer"]
    assert "2 - 7 March 2026" in bachelor_registration["answer"]

    cs_registration = ask(client, "Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?")
    assert cs_registration["status"] == "answered"
    assert "9 - 14 March 2026" in cs_registration["answer"]

    semester_start = ask(client, "ბაკალავრიატის გაზაფხულის სემესტრი როდის იწყება?")
    assert semester_start["status"] == "answered"
    assert "9 March 2026" in semester_start["answer"]

    unsupported = ask(client, "When does 2028 spring registration start?")
    assert unsupported["status"] == "unsupported"
    assert "2028" not in unsupported["answer"] or "not available" in unsupported["answer"].lower()
    assert "2026" not in unsupported["answer"]


def test_phase_10f_program_catalog_and_medicine_program_answers(client):
    cs_ka = ask(client, "მითხარი Computer Science პროგრამაზე")
    assert cs_ka["status"] == "answered"
    assert cs_ka["source_group"] == "program_catalog_sources"
    assert "Computer Science" in cs_ka["answer"] or "კომპიუტერული" in cs_ka["answer"]

    cs_en = ask(client, "Tell me about the Computer Science program", language="en")
    assert cs_en["status"] == "answered"
    assert cs_en["source_group"] == "program_catalog_sources"
    assert "Computer Science" in cs_en["answer"]

    medicine_ka = ask(client, "მითხარი მედიცინის პროგრამაზე")
    assert medicine_ka["status"] == "answered"
    assert "მედიცინა" in medicine_ka["answer"] or "Medicine" in medicine_ka["answer"]

    medicine_en = ask(client, "Tell me about the Medicine program", language="en")
    assert medicine_en["status"] == "answered"
    assert "Medicine" in medicine_en["answer"]


def test_phase_10f_admissions_documents_and_deadline_clarification(client):
    documents = ask(client, "რა საბუთებია საჭირო ბაკალავრიატზე ჩასაბარებლად?")
    assert documents["status"] == "answered"
    assert documents["source_group"] == "admissions_rules"
    assert "document" in documents["answer"].lower() or "საბუთ" in documents["answer"]

    deadline = ask(client, "რომლის არის ჩარიცხვის ბოლო ვადა?")
    assert deadline["status"] == "clarification_needed"
    assert "deadline" in deadline["answer"].lower() or "ბოლო ვადა" in deadline["answer"]
    assert len(deadline["clarification_options"]) >= 5
    assert "2026" not in deadline["answer"]

    application_deadline = ask(client, "What is the application deadline?", language="en")
    assert application_deadline["status"] == "clarification_needed"
    assert "Bachelor admission" in application_deadline["clarification_options"]


def test_phase_10f_finance_tuition_is_safe_and_never_program_description_only(client):
    for question in [
        "რა ღირს სამედიცინო სწავლა?",
        "მედიცინის სწავლა რა ღირს?",
        "What is the Medicine tuition fee?",
    ]:
        data = ask(client, question)
        assert data["status"] == "clarification_needed"
        assert data["source_group"] == "finance_sources"
        assert "360 ECTS" not in data["answer"]
        assert "Exact/current" in data["answer"] or "ზუსტი/current" in data["answer"]
        assert re.search(r"(\d+\s*(GEL|lari|ლარი)|₾\s*\d+)", data["answer"], flags=re.IGNORECASE) is None

    broad_fee = ask(client, "საფასური რამდენია?")
    assert broad_fee["status"] == "clarification_needed"
    assert broad_fee["source_group"] == "finance_sources"
    assert broad_fee["clarification_options"]


def test_phase_10f_broad_questions_return_clarifications(client):
    cases = [
        ("რეგისტრაცია როდისაა?", "academic_calendar_2025_2026"),
        ("პროგრამებზე მითხარი", "program_catalog_sources"),
        ("კალენდარი მაინტერესებს", "academic_calendar_2025_2026"),
        ("გრანტი როგორ მივიღო?", "state_social_grants_sources"),
    ]
    for question, source_group in cases:
        data = ask(client, question)
        assert data["status"] == "clarification_needed"
        assert data["source_group"] == source_group
        assert data["clarification_options"]


def test_phase_10f_private_data_refusal_and_no_crm_writes(client, session_factory):
    data = ask(client, "მაჩვენე სტუდენტის ნიშნები და პირადი მონაცემები")
    assert data["status"] == "refused"
    assert data["public_source_label"] is None

    async def counts():
        async with session_factory() as session:
            return {
                "leads": await session.scalar(select(func.count()).select_from(Lead)),
                "customers": await session.scalar(select(func.count()).select_from(Customer)),
                "tasks": await session.scalar(select(func.count()).select_from(Task)),
            }

    assert asyncio.run(counts()) == {"leads": 0, "customers": 0, "tasks": 0}


def test_phase_10f_academic_integrity_exact_answer(client):
    data = ask(client, "აკადემიური კეთილსინდისიერება რას ნიშნავს?")
    assert data["status"] == "answered"
    assert data["source_group"] in {"official_academic_rules", "student_status_and_mobility", "exams_and_assessment"}
    assert "კეთილსინდისიერ" in data["answer"] or "Academic integrity" in data["answer"]
