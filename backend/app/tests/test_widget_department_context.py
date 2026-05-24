from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAFE_PRO_WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"


def test_safe_pro_widget_sends_department_context():
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8")

    assert "selected_department" in text
    assert "selected_topic" in text
    assert "widget_variant" in text
    assert "safe_pro" in text


def test_safe_pro_widget_has_expected_department_chips():
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8")

    for department in ["admissions", "finance", "international", "medicine", "student_services", "it_support"]:
        assert department in text


def test_safe_pro_widget_has_no_direct_anthropic_or_secret():
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8")

    assert "api.anthropic.com" not in text
    assert "ANTHROPIC_API_KEY" not in text
    assert "sk-ant-" not in text
