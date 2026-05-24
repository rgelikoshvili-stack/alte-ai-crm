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
