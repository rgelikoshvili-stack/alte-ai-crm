def start_session(client, language="ka"):
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def create_source(client, *, title, source_domain, language="ka", status="approved"):
    response = client.post(
        "/knowledge/sources",
        json={
            "source_key": title.lower().replace(" ", "_"),
            "title": title,
            "source_type": "pdf",
            "status": status,
            "language": language,
            "source_domain": source_domain,
            "category": "academic_rules",
            "sensitivity": "official",
        },
    )
    assert response.status_code == 200
    return response.json()


def create_snippet(client, source, *, title, content, keywords):
    response = client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": source["source_key"],
            "title": title,
            "content": content,
            "category": "academic_rules",
            "source_domain": source["source_domain"],
            "sensitivity": "official",
            "keywords": keywords,
            "status": "approved",
            "language": source["language"],
        },
    )
    assert response.status_code == 200
    return response.json()


def seed_official_academic_rules(client):
    official = create_source(client, title="ბაკალავრიატის დებულება", source_domain="official_academic_rules")
    create_snippet(
        client,
        official,
        title="ბაკალავრიატის დებულება - კრედიტები",
        content=(
            "საბაკალავრო პროგრამაზე საჭიროა არანაკლებ 240 კრედიტი. "
            "მედიცინის ერთსაფეხურიან პროგრამაზე საჭიროა არანაკლებ 360 კრედიტი. "
            "სტომატოლოგიის ერთსაფეხურიან პროგრამაზე საჭიროა არანაკლებ 300 კრედიტი."
        ),
        keywords="ბაკალავრიატი bachelor ECTS კრედიტი 240 მედიცინა 360 სტომატოლოგია 300",
    )
    process = create_source(client, title="სასწავლო პროცესის მარეგულირებელი წესი", source_domain="official_academic_rules")
    create_snippet(
        client,
        process,
        title="სწავლების ენა და სტატუსის შეჩერება",
        content=(
            "უნივერსიტეტში სწავლების ენა არის ქართული. ცალკეულ პროგრამებზე სწავლება ხორციელდება ინგლისურ ენაზე. "
            "სტუდენტის სტატუსის შეჩერების საერთო ვადა არ უნდა აღემატებოდეს 5 წელს."
        ),
        keywords="სწავლების ენა ქართული ინგლისური სტატუსის შეჩერება 5 წელი",
    )
    master = create_source(client, title="მაგისტრატურის დებულება", source_domain="official_academic_rules")
    create_snippet(
        client,
        master,
        title="მაგისტრატურის დებულება - კრედიტები",
        content="სამაგისტრო პროგრამაზე საჭიროა არანაკლებ 120 კრედიტი.",
        keywords="მაგისტრატურა master ECTS კრედიტი 120",
    )
    create_snippet(
        client,
        master,
        title="მაგისტრატურის დებულება - ჩარიცხვის საბუთები",
        content=(
            "მაგისტრატურაზე ჩასარიცხად საჭიროა პირადობის დამადასტურებელი დოკუმენტის ასლი, CV, "
            "3x4 ფოტოსურათი ბეჭდური და ელექტრონული ფორმით, სამხედრო აღრიცხვაზე ყოფნის "
            "დამადასტურებელი დოკუმენტის ასლი მამაკაცი აპლიკანტებისთვის, ნოტარიულად დამოწმებული "
            "დიპლომის ასლი და დიპლომის დანართის ასლი."
        ),
        keywords="მაგისტრატურა საბუთები დოკუმენტები ჩარიცხვა ID CV 3x4 სამხედრო ნოტარიული დიპლომის დანართი",
    )
    stale_marketing = create_source(client, title="Old marketing bachelor program", source_domain="alte.edu.ge")
    create_snippet(
        client,
        stale_marketing,
        title="ბიზნესის ადმინისტრირების 3-წლიანი პროგრამა",
        content="კრედიტი/ხანგრძლივობა: 180 კრედიტი/3 წელი.",
        keywords="ბაკალავრიატი bachelor ECTS კრედიტი 180 3 წელი",
    )


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


def assert_no_contact_request(payload):
    reply = payload["reply"].lower()
    assert "phone" not in reply
    assert "email" not in reply
    assert "ტელეფონ" not in reply
    assert "ელ.ფოსტ" not in reply
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def test_bachelor_ects_uses_official_240_not_old_180(client):
    seed_official_academic_rules(client)

    payload = ask(client, "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "240" in payload["reply"]
    assert "180" not in payload["reply"]
    assert "3-წლიანი" not in payload["reply"]
    assert "3 წელი" not in payload["reply"]
    assert_no_contact_request(payload)


def test_master_ects_returns_120(client):
    seed_official_academic_rules(client)

    payload = ask(client, "რამდენი კრედიტია სამაგისტრო პროგრამა ალტე უნივერსიტეტში?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "120" in payload["reply"]
    assert_no_contact_request(payload)


def test_master_admission_documents_returns_official_checklist(client):
    seed_official_academic_rules(client)

    payload = ask(client, "რა საბუთები მჭირდება მაგისტრატურაზე ჩასარიცხად?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    reply = payload["reply"]
    for expected in ["პირადობის", "CV", "3x4", "სამხედრო", "ნოტარ", "დიპლომის დანართ"]:
        assert expected in reply
    assert_no_contact_request(payload)


def test_teaching_language_is_conservative(client):
    seed_official_academic_rules(client)

    payload = ask(client, "რა ენაზე მიმდინარეობს სწავლება ალტე უნივერსიტეტში?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "ქართული" in payload["reply"]
    assert "ინგლისურ" in payload["reply"]
    assert "დაგეგმ" not in payload["reply"]
    assert "program list" not in payload["reply"].lower()
    assert_no_contact_request(payload)


def test_status_suspension_max_returns_5_years(client):
    seed_official_academic_rules(client)

    payload = ask(client, "რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?")

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "5" in payload["reply"]
    assert_no_contact_request(payload)
