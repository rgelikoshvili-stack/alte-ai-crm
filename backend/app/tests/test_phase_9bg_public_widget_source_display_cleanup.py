from pathlib import Path

from app.schemas.chat import ChatMessageResponse
from app.services.chat_service import PUBLIC_SOURCE_LABEL_WHITELIST, response_public_source_label


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHAT_VARIANTS = [
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9BG_PUBLIC_WIDGET_SOURCE_DISPLAY_CLEANUP_RESULT.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9bg_public_widget_uses_single_source_line_not_chips():
    for path in CHAT_VARIANTS:
        text = read(path)
        assert "function SourceLine" in text
        assert "function SourceChip" not in text
        assert "<SourceLine label={msg.sourceLabel} lang={lang}/>" in text
        assert "msg.sources.map" not in text
        assert "window.open(url" not in text
        assert "sourceLabel:" in text


def test_phase_9bg_public_source_label_requires_source_backed_answer():
    for path in CHAT_VARIANTS:
        text = read(path)
        assert "backend.answer_source_status !== 'answered_from_approved_source'" in text
        assert "backend.clarification_needed || backend.should_handover" in text
        assert "backend.public_source_label" in text
        assert "groupLabel(backend.source_group)" in text
        assert "sourceLabel: settingsState.sources ? publicSourceLabel(backend) : null" in text
        assert "sourceLabel: null" in text
        assert "inferSources(reply" not in text
        assert "defaultUrls" not in text


def test_phase_9bg_public_label_mapping_hides_internal_source_ids():
    for path in CHAT_VARIANTS:
        text = read(path)
        for public_label in [
            "ბაკალავრიატის დებულება",
            "მაგისტრატურის დებულება",
            "სასწავლო პროცესის მარეგულირებელი წესი",
            "აკადემიური კალენდარი 2025–2026",
            "საგანმანათლებლო პროგრამების კატალოგი",
            "მიღების წესი",
            "საერთაშორისო მიღების წესი",
            "ბიბლიოთეკის წესი",
            "კარიერის სერვისები",
            "ფინანსური მხარდაჭერა",
            "სახელმწიფო/სოციალური გრანტები",
        ]:
            assert public_label in text
        public_ui = text[text.index("// ============ Public source line ============"):text.index("// ============ Bubble actions ============")]
        forbidden = ["full_alte_local_kb", "selected_alte_45_doc", "official_alte_8_pdf_kb", "official_academic_rules", "chunk"]
        for marker in forbidden:
            assert marker not in public_ui


def test_phase_9bg_result_doc_exists_and_keeps_no_go():
    assert RESULT_DOC.exists()
    text = read(RESULT_DOC)
    assert "PHASE_9BG_STATUS=LOCAL_READY_PENDING_REVIEW" in text
    assert "Public launch: NO-GO" in text
    assert "Deploy status: NOT_DEPLOYED" in text
    assert "Commit status: NO" in text


def test_phase_9bg_backend_public_source_label_is_safe_and_source_backed_only():
    knowledge = {
        "answer_source_status": "answered_from_approved_source",
        "used_sources": ["Phase 9BF Georgian control deterministic source mapping"],
    }
    assert response_public_source_label(
        knowledge,
        should_handover=False,
        source_group="official_academic_rules",
    ) == "სასწავლო პროცესის მარეგულირებელი წესი"
    assert response_public_source_label(
        {"answer_source_status": "no_approved_source_found", "used_sources": []},
        should_handover=False,
        source_group="program_catalog_sources",
    ) is None
    assert response_public_source_label(
        knowledge,
        should_handover=True,
        source_group="program_catalog_sources",
    ) is None
    assert response_public_source_label(
        {"answer_source_status": "answered_from_approved_source", "used_sources": ["official_academic_rules_full chunk 7"]},
        should_handover=False,
        source_group=None,
    ) is None
    assert response_public_source_label(
        knowledge,
        should_handover=False,
        source_group="unknown",
    ) is None
    assert response_public_source_label(
        {"answer_source_status": "answered_from_approved_source", "used_sources": ["Some official looking source"]},
        should_handover=False,
        source_group=None,
    ) is None
    assert response_public_source_label(
        {"answer_source_status": "answered_from_approved_source", "used_sources": ["official_alte_8_pdf_kb something"]},
        should_handover=False,
        source_group=None,
    ) is None
    assert response_public_source_label(
        {"answer_source_status": "answered_from_approved_source", "used_sources": []},
        should_handover=False,
        source_group="academic_calendar_2025_2026",
    ) == "აკადემიური კალენდარი 2025–2026"
    assert response_public_source_label(
        {"answer_source_status": "clarification_needed", "used_sources": [], "public_source_label": "აკადემიური კალენდარი 2025–2026"},
        should_handover=False,
        source_group="academic_calendar_2025_2026",
    ) is None
    assert response_public_source_label(
        {"answer_source_status": "answered_from_approved_source", "used_sources": [], "public_source_label": "Some official looking source"},
        should_handover=False,
        source_group=None,
    ) is None
    for label in PUBLIC_SOURCE_LABEL_WHITELIST:
        assert response_public_source_label(
            {"answer_source_status": "answered_from_approved_source", "used_sources": [], "public_source_label": label},
            should_handover=False,
            source_group=None,
        ) == label


def test_phase_9bg_response_schema_exposes_public_source_label_without_required_value():
    response = ChatMessageResponse(
        conversation_id="1",
        reply="ok",
        intent="knowledge",
        confidence=1.0,
        should_create_lead=False,
        should_handover=False,
        answer_source_status="answered_from_approved_source",
        used_sources=["Phase 9BF Georgian control deterministic source mapping"],
        public_source_label="სასწავლო პროცესის მარეგულირებელი წესი",
    )
    assert response.public_source_label == "სასწავლო პროცესის მარეგულირებელი წესი"


def test_phase_9bg_frontend_prefers_clean_backend_label_and_source_group_fallback():
    for path in CHAT_VARIANTS:
        text = read(path)
        assert "const allowedLabels = [" in text
        assert "const directLabel = safeLabel(backend.public_source_label)" in text
        assert "if (directLabel) return directLabel" in text
        assert "const routedLabel = safeLabel(groupLabel(backend.source_group))" in text
        assert "if (routedLabel) return routedLabel" in text
        assert "backend.used_sources" not in text
        assert "backend.snippet_titles" not in text
        assert ".concat(Array.isArray" not in text
        for marker in [
            "full_alte_local_kb",
            "selected_alte_45_doc",
            "official_alte_8_pdf_kb",
            "official_academic_rules_full",
            "source_key",
            "source_id",
        ]:
            assert marker not in text[text.index("const publicSourceLabel = (backend) => {"):text.index("// Detect intent")]
