def start_session(client, language="ka"):
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def ask(client, message, language="ka"):
    session = start_session(client, language=language)
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": message,
            "source_domain": "alte.edu.ge",
            "language": language,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_source(client, *, title, source_domain, category="academic_rules"):
    response = client.post(
        "/knowledge/sources",
        json={
            "source_key": title.lower().replace(" ", "_"),
            "title": title,
            "source_type": "pdf",
            "status": "approved",
            "language": "ka",
            "source_domain": source_domain,
            "category": category,
            "sensitivity": "official",
        },
    )
    assert response.status_code == 200
    return response.json()


def create_snippet(client, source, *, title, content, category="academic_rules", keywords=""):
    response = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": source["source_key"],
            "title": title,
            "content": content,
            "category": category,
            "source_domain": source["source_domain"],
            "sensitivity": "official",
            "keywords": keywords,
            "status": "approved",
            "language": "ka",
        },
    )
    assert response.status_code == 200
    return response.json()


def seed_gpa_source(client):
    source = create_source(client, title="სასწავლო პროცესის მარეგულირებელი წესი", source_domain="official_academic_rules")
    create_snippet(
        client,
        source,
        title="GPA-ის გამოთვლის წესი",
        content="GPA გამოითვლება ფორმულით: კურსის GPA = (X - 50) * 0.06 + 1. ჯამური GPA არის კრედიტებით შეწონილი საშუალო.",
        category="exams_and_assessment",
        keywords="GPA გამოთვლა ფორმულა კრედიტებით შეწონილი საშუალო FX F",
    )


def assert_no_crm_side_effects(payload):
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def assert_not_admissions_documents(reply):
    forbidden = ["პირადობის დამადასტურებელი", "3x4", "დიპლომის ასლი", "ჩასარიცხად საჭირო"]
    assert not any(marker in reply for marker in forbidden)


def test_phase_9bf_gpa_formula_is_exact_and_credit_weighted(client):
    seed_gpa_source(client)

    payload = ask(client, "როგორ გამოითვლება GPA?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "(X - 50) * 0.06 + 1" in payload["reply"]
    assert "კრედიტ" in payload["reply"]
    assert "FX" in payload["reply"]
    assert_no_crm_side_effects(payload)


def test_phase_9bf_broad_calendar_controls_ask_clarification(client):
    questions = [
        "როდის არის რეგისტრაციის პერიოდი აკადემიურ კალენდარში?",
        "როდის იწყება სემესტრი?",
        "როდის არის შუალედური ან დასკვნითი გამოცდები?",
    ]

    for question in questions:
        payload = ask(client, question)
        assert payload["answer_source_status"] == "clarification_needed"
        assert "დააზუსტ" in payload["reply"]
        assert "პროგრამის ჯგუფი" in payload["reply"]
        assert_no_crm_side_effects(payload)


def test_phase_9bf_selected_student_support_topics_are_not_admissions_docs(client):
    cases = [
        ("რა სერვისებს იღებს სტუდენტი უნივერსიტეტში?", ["ბიბლიოთეკ", "კარიერულ", "ომბუდსმენ"]),
        ("რა ფუნქცია აქვს სტუდენტურ ომბუდსმენს?", ["ომბუდსმენ", "უფლებ"]),
        ("როგორ შეუძლია სტუდენტს საკუთარი უფლებების დაცვა?", ["უფლებ", "ომბუდსმენ"]),
        ("როგორ შეუძლია სტუდენტს ბიბლიოთეკით სარგებლობა?", ["ბიბლიოთეკ"]),
        ("რა მხარდაჭერა აქვს სპეციალური საჭიროების მქონე სტუდენტს?", ["სპეციალური საჭირო", "ადაპტ"]),
    ]

    for question, expected_terms in cases:
        payload = ask(client, question)
        assert payload["answer_source_status"] == "answered_from_approved_source"
        assert all(term in payload["reply"] for term in expected_terms)
        assert_not_admissions_documents(payload["reply"])
        assert_no_crm_side_effects(payload)


def test_phase_9bf_integrity_edi_sustainability_and_finance_controls(client):
    cases = [
        ("რა არის სახელმწიფო სასწავლო გრანტი ან სოციალური პროგრამა?", ["სახელმწიფო სასწავლო გრანტ", "სოციალური პროგრამ"]),
        ("რა არის პლაგიატი?", ["პლაგიატი", "აკადემიური"]),
        ("რა სანქციები შეიძლება მოჰყვეს აკადემიური კეთილსინდისიერების დარღვევას?", ["სანქცია", "კეთილსინდისიერ"]),
        ("რას მოიცავს EDI policy?", ["თანასწორ", "მრავალფერ", "ინკლუზ"]),
        ("რას ეხება მდგრადი განვითარების სტრატეგია?", ["მდგრად", "სტრატეგ"]),
        ("რა მოთხოვნები შეიძლება ჰქონდეს ინგლისურენოვან პროგრამაზე ჩარიცხვას?", ["ინგლისურენოვან", "ინგლისური ენის"]),
    ]

    for question, expected_terms in cases:
        payload = ask(client, question)
        assert payload["answer_source_status"] == "answered_from_approved_source"
        assert all(term in payload["reply"] for term in expected_terms)
        assert_not_admissions_documents(payload["reply"])
        assert_no_crm_side_effects(payload)


def test_phase_9bf_current_tuition_is_unsupported_not_catalog_answer(client):
    payload = ask(client, "რა ღირს წელს სამართლის პროგრამაზე სწავლა?")

    assert payload["answer_source_status"] == "no_approved_source_found"
    assert "ზუსტი ინფორმაცია ვერ ვიპოვე" in payload["reply"]
    assert "კატალოგ" not in payload["reply"]
    assert "240" not in payload["reply"]
    assert_no_crm_side_effects(payload)
