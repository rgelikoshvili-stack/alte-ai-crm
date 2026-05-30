from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"
QUESTION = "როგორ ჩავაბარო ბაკალავრიატზე?"
MOJIBAKE_MARKER = "áƒ"

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
REPORT_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AF_GEORGIAN_ENCODING_SMOKE_RESULT.json"


def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], bytes]:
    headers = {"Origin": NETLIFY_ORIGIN}
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def _decode_json(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"_decode_error": text[:300]}
    return data


def _contains_georgian(text: str) -> bool:
    return bool(re.search(r"[\u10A0-\u10FF]", text))


def _header(headers: dict[str, str], name: str) -> str:
    wanted = name.lower()
    for key, value in headers.items():
        if key.lower() == wanted:
            return value
    return ""


def run_smoke() -> dict[str, Any]:
    session_status, session_headers, session_raw = _request(
        "POST",
        "/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": NETLIFY_URL, "phase": "9af_georgian_encoding_smoke"},
        },
    )
    session = _decode_json(session_raw)
    message_status = 0
    message_headers: dict[str, str] = {}
    message_raw = b""
    message: dict[str, Any] = {}
    if session_status == 200 and session.get("conversation_id") and session.get("session_id"):
        message_status, message_headers, message_raw = _request(
            "POST",
            "/chat/message",
            {
                "conversation_id": session["conversation_id"],
                "session_id": session["session_id"],
                "message": QUESTION,
                "source_domain": "join.alte.edu.ge",
                "language": "ka",
                "page_url": NETLIFY_URL,
                "widget_variant": "pro_v2_safe",
            },
        )
        message = _decode_json(message_raw)

    raw_text = message_raw.decode("utf-8", errors="replace")
    reply = str(message.get("reply") or "")
    session_content_type = _header(session_headers, "content-type")
    message_content_type = _header(message_headers, "content-type")
    checks = {
        "session_start_ok": session_status == 200,
        "message_ok": message_status == 200,
        "session_content_type_json": "application/json" in session_content_type.lower(),
        "message_content_type_json": "application/json" in message_content_type.lower(),
        "raw_response_no_mojibake": MOJIBAKE_MARKER not in raw_text,
        "reply_no_mojibake": MOJIBAKE_MARKER not in reply,
        "raw_response_contains_georgian": _contains_georgian(raw_text),
        "reply_contains_georgian": _contains_georgian(reply),
        "question_preserved_locally": QUESTION == "როგორ ჩავაბარო ბაკალავრიატზე?",
        "no_created_lead": message.get("created_lead_id") is None,
        "no_created_task": message.get("created_task_id") is None,
        "no_created_customer": message.get("created_customer_id") is None,
        "no_create_lead_flag": message.get("should_create_lead") is not True,
    }
    report = {
        "status": "PASSED" if all(checks.values()) else "FAILED",
        "backend_url": BASE_URL,
        "origin": NETLIFY_ORIGIN,
        "question": QUESTION,
        "checks": checks,
        "session_status": session_status,
        "message_status": message_status,
        "session_content_type": session_content_type,
        "message_content_type": message_content_type,
        "answer_source_status": message.get("answer_source_status"),
        "route_department": message.get("route_department"),
        "department_key": message.get("department_key"),
        "reply_excerpt": reply[:320],
        "contact_details_sent": False,
        "lead_task_customer_created": False,
        "public_launch": "NO-GO",
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    report = run_smoke()
    print(
        json.dumps(
            {
                "status": report["status"],
                "checks": report["checks"],
                "answer_source_status": report.get("answer_source_status"),
                "route_department": report.get("route_department"),
                "department_key": report.get("department_key"),
                "report_json": str(REPORT_JSON.relative_to(PROJECT_ROOT)),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    if report["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
