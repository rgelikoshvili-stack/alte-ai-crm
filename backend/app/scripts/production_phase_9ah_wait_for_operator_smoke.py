from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
REPORT_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AH_WAIT_FOR_OPERATOR_SMOKE_RESULT.json"

UNSUPPORTED_QUESTION = "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?"
DIRECT_CONTACT_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share|write).{0,60}(phone|email|name|whatsapp)", re.I),
    re.compile(r"(phone|email|name|whatsapp).{0,60}(type|enter|send|provide|share|write)", re.I),
    re.compile(r"(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი|whatsapp).{0,60}(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ)", re.I),
    re.compile(r"(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ).{0,60}(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი|whatsapp)", re.I),
]


@dataclass
class SmokeCheck:
    name: str
    passed: bool
    detail: str = ""


def _request(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], Any]:
    headers = {"Origin": NETLIFY_ORIGIN}
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
            return response.status, dict(response.headers), json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw[:200]}
        return exc.code, dict(exc.headers), data


def _start_session() -> dict[str, Any]:
    status, _, data = _request(
        "POST",
        f"{BASE_URL}/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": NETLIFY_URL, "phase": "9ah_wait_for_operator_no_contact_smoke"},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}")
    return data


def run_smoke(trigger_wait: bool = True) -> dict[str, Any]:
    session = _start_session()
    checks: list[SmokeCheck] = []
    status, _, message_data = _request(
        "POST",
        f"{BASE_URL}/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": UNSUPPORTED_QUESTION,
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "page_url": NETLIFY_URL,
            "widget_variant": "pro_v2_safe",
        },
    )
    reply = str((message_data or {}).get("reply") or "")
    checks.append(SmokeCheck("chat_message_200", status == 200, str(status)))
    checks.append(
        SmokeCheck(
            "unsupported_status",
            (message_data or {}).get("answer_source_status") == "no_approved_source_found",
            str((message_data or {}).get("answer_source_status")),
        )
    )
    checks.append(
        SmokeCheck(
            "operator_offer_present",
            "ოპერატორთან" in reply or "operator" in reply.lower(),
            reply[:160],
        )
    )
    checks.append(
        SmokeCheck(
            "no_direct_contact_request",
            not any(pattern.search(reply) for pattern in DIRECT_CONTACT_PATTERNS),
            reply[:160],
        )
    )
    checks.append(SmokeCheck("no_invented_scholarship", not any(token in reply.lower() for token in ["eligible", "deadline", "70%", "50%"])))

    handover_data: Any = None
    if trigger_wait:
        handover_status, _, handover_data = _request(
            "POST",
            f"{BASE_URL}/chat/handover/{session['conversation_id']}",
            {
                "session_id": session["session_id"],
                "selected_department": (message_data or {}).get("department_key") or "admissions",
                "selected_topic": "unsupported_question",
                "source_domain": "join.alte.edu.ge",
                "language": "ka",
                "reason": "wait_for_operator",
                "mode": "waiting_for_operator",
                "message": UNSUPPORTED_QUESTION,
            },
        )
        checks.append(SmokeCheck("wait_handover_200", handover_status == 200, str(handover_status)))
        checks.append(
            SmokeCheck(
                "wait_status_no_task",
                (handover_data or {}).get("status") == "waiting_for_operator" and (handover_data or {}).get("task_id") is None,
                json.dumps(handover_data, ensure_ascii=False)[:200],
            )
        )

    checks.append(
        SmokeCheck(
            "no_lead_task_customer_created_by_response",
            not (message_data or {}).get("created_lead_id") and not (message_data or {}).get("created_task_id"),
            f"lead={(message_data or {}).get('created_lead_id')} task={(message_data or {}).get('created_task_id')}",
        )
    )
    result = {
        "status": "PASSED" if all(check.passed for check in checks) else "FAILED",
        "backend_url": BASE_URL,
        "origin": NETLIFY_ORIGIN,
        "triggered_wait_for_operator": trigger_wait,
        "wait_handover_write_scope": "conversation.status and human_handover metadata only; no lead/customer/task expected",
        "checks": [check.__dict__ for check in checks],
        "conversation_id": session["conversation_id"],
        "sanitized": True,
    }
    REPORT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
