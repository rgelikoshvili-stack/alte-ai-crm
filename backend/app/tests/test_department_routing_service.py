from app.services.department_routing_service import resolve_department


def test_ka_tuition_routes_to_finance():
    result = resolve_department(
        message_text="რა ღირს სწავლა?",
        ai_intent="finance_question",
        ai_confidence=0.9,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="ka",
    )

    assert result.department_key == "finance"
    assert result.department == "Finance"
    assert result.handover_required is True
    assert result.sensitive_topic is True


def test_medicine_from_india_routes_to_medicine_with_international_priority_reason():
    result = resolve_department(
        message_text="I want to apply for medicine from India",
        ai_intent="international_admission",
        ai_confidence=0.88,
        source_domain="join.alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key == "medicine"
    assert result.department == "Medicine / MD"
    assert result.reason == "medicine_with_international_priority"


def test_selected_finance_routes_ambiguous_message_to_finance():
    result = resolve_department(
        message_text="მაინტერესებს დეტალები",
        ai_intent="unknown",
        ai_confidence=0.55,
        source_domain="alte.edu.ge",
        selected_department="finance",
        selected_topic="tuition",
        risk_flags=[],
        used_sources=[],
        language="ka",
    )

    assert result.department_key == "finance"
    assert result.handover_required is True


def test_selected_medicine_routes_unknown_to_medicine():
    result = resolve_department(
        message_text="Can you explain this?",
        ai_intent="unknown",
        ai_confidence=0.4,
        source_domain="alte.edu.ge",
        selected_department="medicine",
        selected_topic="medicine_md",
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key == "medicine"
    assert result.handover_required is True


def test_human_request_uses_selected_finance():
    result = resolve_department(
        message_text="I want to talk to an operator about tuition",
        ai_intent="human_request",
        ai_confidence=0.9,
        source_domain="alte.edu.ge",
        selected_department="finance",
        selected_topic="tuition",
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key == "finance"
    assert result.reason == "human_request_selected_or_inferred_department"


def test_unknown_without_selected_defaults_to_admissions():
    result = resolve_department(
        message_text="What about this topic?",
        ai_intent="unknown",
        ai_confidence=0.3,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key == "admissions"
    assert result.handover_required is True


def test_technical_issue_routes_to_it_support():
    result = resolve_department(
        message_text="I have a portal login problem",
        ai_intent="general_info",
        ai_confidence=0.8,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key == "it_support"


def test_student_services_question_routes_to_student_services():
    result = resolve_department(
        message_text="Tell me about library, career and student clubs",
        ai_intent="general_info",
        ai_confidence=0.8,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key == "student_services"


def test_spec_program_question_routes_to_programs():
    result = resolve_department(
        message_text="რომელი პროგრამები აქვს ალტე უნივერსიტეტს?",
        ai_intent="general_info",
        ai_confidence=0.9,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=["official_alte_pdf_kb"],
        language="ka",
    )

    assert result.department_key == "programs"
    assert result.department == "Programs"


def test_spec_admission_documents_route_to_admissions():
    result = resolve_department(
        message_text="რა საბუთებია ჩარიცხვისთვის საჭირო?",
        ai_intent="admission_interest",
        ai_confidence=0.9,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=["official_academic_rules"],
        language="ka",
    )

    assert result.department_key == "admissions"


def test_spec_international_student_route():
    result = resolve_department(
        message_text="I am a foreign student and need visa admission information",
        ai_intent="international_admission",
        ai_confidence=0.9,
        source_domain="join.alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=["official_alte_pdf_kb"],
        language="en",
    )

    assert result.department_key == "international"


def test_spec_medicine_md_route():
    result = resolve_department(
        message_text="Medicine MD program admission",
        ai_intent="admission_interest",
        ai_confidence=0.9,
        source_domain="alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=["official_alte_pdf_kb"],
        language="en",
    )

    assert result.department_key == "medicine"


def test_spec_library_and_career_route_to_student_services():
    for message in ["ბიბლიოთეკის წესები მაინტერესებს", "კარიერული მხარდაჭერა არსებობს?"]:
        result = resolve_department(
            message_text=message,
            ai_intent="student_service",
            ai_confidence=0.9,
            source_domain="alte.edu.ge",
            selected_department=None,
            selected_topic=None,
            risk_flags=[],
            used_sources=["official_alte_pdf_kb"],
            language="ka",
        )

        assert result.department_key == "student_services"


def test_spec_study_process_exam_ects_status_routes():
    for message in [
        "FX შეფასების შემდეგ დამატებით გამოცდაზე გასვლა შეიძლება?",
        "ECTS კრედიტების აღიარება როგორ ხდება?",
        "სტუდენტის სტატუსის შეჩერება რამდენი წლით შეიძლება?",
    ]:
        result = resolve_department(
            message_text=message,
            ai_intent="general_info",
            ai_confidence=0.9,
            source_domain="alte.edu.ge",
            selected_department=None,
            selected_topic=None,
            risk_flags=[],
            used_sources=["official_academic_rules"],
            language="ka",
        )

        assert result.department_key == "study_process"
        assert result.department == "Study Process"


def test_spec_ombudsman_rights_and_special_needs_route_to_student_services():
    for message in ["ომბუდსმენის მექანიზმი როგორ მუშაობს?", "სპეციალური საჭიროებების მხარდაჭერა მაინტერესებს"]:
        result = resolve_department(
            message_text=message,
            ai_intent="student_service",
            ai_confidence=0.9,
            source_domain="alte.edu.ge",
            selected_department=None,
            selected_topic=None,
            risk_flags=[],
            used_sources=["official_alte_pdf_kb"],
            language="ka",
        )

        assert result.department_key == "student_services"


def test_spec_ai_policy_plagiarism_ethics_route_to_study_process():
    for message in ["AI-ის გამოყენება შეიძლება?", "პლაგიატის წესი მაინტერესებს", "ეთიკის კოდექსი რას ამბობს?"]:
        result = resolve_department(
            message_text=message,
            ai_intent="general_info",
            ai_confidence=0.9,
            source_domain="alte.edu.ge",
            selected_department=None,
            selected_topic=None,
            risk_flags=[],
            used_sources=["official_alte_pdf_kb"],
            language="ka",
        )

        assert result.department_key == "study_process"
