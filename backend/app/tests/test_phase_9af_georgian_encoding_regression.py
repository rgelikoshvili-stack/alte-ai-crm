from __future__ import annotations

import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AF_GEORGIAN_ENCODING_FIX_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
NETLIFY_TOML = PROJECT_ROOT / "netlify.toml"

FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "dist" / "netlify_test_site_package" / "variants" / "pro-v2-chat.jsx",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9af_georgian_encoding_fix")
    assert hasattr(module, "run_checks")


def test_smoke_script_importability() -> None:
    module = importlib.import_module("app.scripts.production_georgian_encoding_smoke")
    assert hasattr(module, "run_smoke")


def test_georgian_frontend_strings_are_utf8_not_mojibake() -> None:
    text = read(PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx")
    assert "ოპერატორი" in text
    assert "დაკოპირდა" in text
    assert "დამაკავშირე ცოცხალ ოპერატორთან" in text
    assert "áƒ" not in text


def test_known_mojibake_fragments_absent_from_active_frontend_sources() -> None:
    combined = "\n".join(read(path) for path in FRONTEND_FILES if path.exists())
    for forbidden in ["áƒ", "Ã", "Â·", "â€”"]:
        assert forbidden not in combined


def test_utf8_charset_exists_in_html_and_netlify_jsx_headers() -> None:
    assert '<meta charset="utf-8"' in read(PROJECT_ROOT / "test_site" / "join.html").lower()
    assert '<meta charset="utf-8"' in read(PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html").lower()
    netlify = read(NETLIFY_TOML)
    assert 'for = "/variants/*.jsx"' in netlify
    assert "Content-Type" in netlify
    assert "charset=UTF-8" in netlify


def test_api_serialization_preserves_georgian_question(client) -> None:
    question = "როგორ ჩავაბარო ბაკალავრიატზე?"
    response = client.post("/chat/session/start", json={"source_domain": "join.alte.edu.ge", "language": "ka"})
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    session = response.json()
    message_response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": question,
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
        },
    )
    assert message_response.status_code == 200
    assert "application/json" in message_response.headers["content-type"]
    raw = message_response.content.decode("utf-8")
    assert "áƒ" not in raw
    assert any("\u10a0" <= ch <= "\u10ff" for ch in raw)


def test_result_doc_status_valid_if_present() -> None:
    if not RESULT_DOC.exists():
        return
    text = read(RESULT_DOC)
    valid = [
        "PHASE_9AF_GEORGIAN_ENCODING_STATUS=PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL",
        "PHASE_9AF_GEORGIAN_ENCODING_STATUS=FIXED_PENDING_NETLIFY_REDEPLOY",
        "PHASE_9AF_GEORGIAN_ENCODING_STATUS=FAILED_PENDING_ENCODING_FIX",
    ]
    assert sum(status in text for status in valid) == 1


def test_public_launch_remains_no_go() -> None:
    text = read(PUBLIC_LAUNCH).lower()
    assert "public_launch_decision=go" not in text
    assert "public launch: go" not in text
    assert "no-go" in text
