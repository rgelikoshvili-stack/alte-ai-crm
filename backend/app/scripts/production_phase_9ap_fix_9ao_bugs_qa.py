from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AP_PRODUCTION_QA_RESULT.json"
CS_QUESTION = "როდის იწყება კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია?"
GENERIC_FALLBACK_MARKERS = [
    "AI სერვისთან კავშირი შეფერხებულია",
    "Could not get an answer",
    "AI service",
]
DIRECT_CONTACT_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share|write).{0,60}(phone|email|name|whatsapp)", re.I),
    re.compile(r"(phone|email|name|whatsapp).{0,60}(type|enter|send|provide|share|write)", re.I),
    re.compile(r"(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი|whatsapp).{0,60}(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ)", re.I),
    re.compile(r"(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ).{0,60}(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი|whatsapp)", re.I),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Origin": NETLIFY_ORIGIN, "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
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


def start_session(case_id: str) -> dict[str, Any]:
    status, _, data = request_json(
        "POST",
        "/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": NETLIFY_URL, "phase": "9ap_fix_9ao_bugs", "case": case_id},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}:{data}")
    return data


def send(case_id: str, message: str) -> dict[str, Any]:
    session = start_session(case_id)
    status, _, data = request_json(
        "POST",
        "/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "page_url": NETLIFY_URL,
            "widget_variant": "pro_v2_safe",
        },
    )
    if status != 200:
        return {"http_status": status, "error": data}
    data["http_status"] = status
    return data


def no_crm_records(payload: dict[str, Any]) -> bool:
    return not payload.get("created_lead_id") and not payload.get("created_task_id")


def no_direct_contact_request(reply: str) -> bool:
    return not any(pattern.search(reply) for pattern in DIRECT_CONTACT_PATTERNS)


def run_checks() -> dict[str, Any]:
    checks: list[Check] = []

    cs = send("computer_science_spring_registration", CS_QUESTION)
    cs_reply = str(cs.get("reply") or "")
    checks.extend(
        [
            Check("cs_http_200", cs.get("http_status") == 200, str(cs.get("http_status"))),
            Check("cs_source_backed", cs.get("answer_source_status") == "answered_from_approved_source", str(cs.get("answer_source_status"))),
            Check("cs_calendar_source_group", cs.get("source_group") == "academic_calendar_2025_2026", str(cs.get("source_group"))),
            Check("cs_includes_9_14_march", "9" in cs_reply and "14" in cs_reply and "მარტ" in cs_reply, cs_reply[:180]),
            Check("cs_includes_30_march", "30" in cs_reply and "მარტ" in cs_reply, cs_reply[:180]),
            Check("cs_no_generic_ai_fallback", not any(marker in cs_reply for marker in GENERIC_FALLBACK_MARKERS), cs_reply[:180]),
            Check("cs_no_crm_records", no_crm_records(cs)),
            Check("cs_no_direct_contact_request", no_direct_contact_request(cs_reply), cs_reply[:180]),
        ]
    )

    clarification = send("broad_clarification", "სწავლა მაინტერესებს")
    clarification_reply = str(clarification.get("reply") or "")
    checks.extend(
        [
            Check("clarification_needed", clarification.get("clarification_needed") is True),
            Check(
                "clarification_options",
                all(token in clarification_reply for token in ["მიღება", "პროგრამები", "სწავლის საფასური", "სტუდენტის სტატუსი"]),
                clarification_reply[:180],
            ),
            Check("clarification_no_crm_records", no_crm_records(clarification)),
        ]
    )

    unsupported = send("unsupported_no_hallucination", "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?")
    unsupported_reply = str(unsupported.get("reply") or "")
    checks.extend(
        [
            Check(
                "unsupported_no_source",
                unsupported.get("answer_source_status") == "no_approved_source_found",
                str(unsupported.get("answer_source_status")),
            ),
            Check("unsupported_no_hallucination", "კოსმოსური კამპუსის სტიპენდია არის" not in unsupported_reply and "70%" not in unsupported_reply),
            Check("unsupported_operator_offer", "ოპერატორ" in unsupported_reply, unsupported_reply[:180]),
            Check("unsupported_no_crm_records", no_crm_records(unsupported)),
            Check("unsupported_no_direct_contact_request", no_direct_contact_request(unsupported_reply), unsupported_reply[:180]),
        ]
    )

    result = {
        "status": "PASSED" if all(check.passed for check in checks) else "FAILED",
        "backend_url": BASE_URL,
        "origin": NETLIFY_ORIGIN,
        "checks": [check.__dict__ for check in checks],
        "sanitized": True,
        "real_contact_data_sent": False,
        "lead_task_customer_created_intentionally": False,
    }
    REPORT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    result = run_checks()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    time.sleep(0.1)
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
