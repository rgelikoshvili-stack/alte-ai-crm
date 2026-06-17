import importlib

from app.services.chat_service import (
    is_clearly_unsupported_official_question,
    is_official_academic_rules_text,
    is_selected_official_document_text,
)


def test_selected_alte_45_import_script_importable():
    module = importlib.import_module("app.scripts.apply_selected_alte_45_missing_docs")
    assert len(module.SELECTED_DOCUMENTS) == 32
    assert hasattr(module, "main")


def test_selected_official_document_questions_trigger_knowledge():
    questions = [
        "რა არის გენერაციული ხელოვნური ინტელექტის გამოყენების პოლიტიკა?",
        "ბიბლიოთეკით სარგებლობის წესები მაინტერესებს",
        "What does the IRO Policy say?",
        "Tell me about Examination Regulations",
        "რა წერია სტუდენტური ომბუდსმენის დებულებაში?",
    ]
    assert all(is_selected_official_document_text(question) for question in questions)


def test_program_catalog_and_admission_questions_trigger_knowledge():
    questions = [
        "რა პროგრამები აქვს ალტე უნივერსიტეტს და როგორ ხდება მიღება?",
        "Tell me about the educational program catalog and admission rules",
    ]
    assert all(is_official_academic_rules_text(question) for question in questions)


def test_clearly_unsupported_future_campus_question_is_guarded():
    assert is_clearly_unsupported_official_question(
        "რა არის ალტე უნივერსიტეტის 2031 წლის კოსმოსური კამპუსის სტიპენდიის ზუსტი პირობები?"
    )
