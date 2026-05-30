import importlib

from app.services.chat_service import is_selected_official_document_text


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
