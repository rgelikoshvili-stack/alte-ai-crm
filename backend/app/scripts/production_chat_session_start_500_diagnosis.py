from __future__ import annotations

import json
import shutil
import subprocess
import sys

import httpx


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"


def _safe_body(text: str) -> str:
    if not text:
        return ""
    lowered = text.lower()
    forbidden = ["database_url", "password", "secret", "token", "sk-ant", "anthropic_api_key"]
    if any(item in lowered for item in forbidden):
        return "[redacted: response contained sensitive-looking text]"
    return text[:800]


def main() -> int:
    payload = {
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "channel": "website_chat",
        "widget_variant": "pro_v2_safe",
        "metadata": {
            "mode": "diagnosis",
            "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html",
        },
    }
    result: dict[str, object] = {
        "endpoint": "/chat/session/start",
        "origin": ORIGIN,
        "contact_details_sent": False,
        "intentional_lead_task_customer_creation": False,
    }
    try:
        response = httpx.post(
            f"{BASE_URL}/chat/session/start",
            headers={"Origin": ORIGIN, "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
    except httpx.HTTPError as exc:
        curl_result = _curl_fallback(payload)
        if curl_result is not None:
            print(json.dumps(curl_result, ensure_ascii=False, indent=2))
            status_code = curl_result.get("status_code")
            return 0 if isinstance(status_code, int) and status_code < 500 else 1
        result.update(
            {
                "status_code": None,
                "cors_allow_origin_present": False,
                "error_type": exc.__class__.__name__,
                "sanitized_response_body": "",
            }
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    allow_origin = response.headers.get("access-control-allow-origin")
    result.update(
        {
            "status_code": response.status_code,
            "cors_allow_origin_present": bool(allow_origin),
            "cors_allow_origin": allow_origin,
            "sanitized_response_body": _safe_body(response.text),
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if response.status_code < 500 else 1


def _curl_fallback(payload: dict) -> dict[str, object] | None:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        return None
    command = [
        curl,
        "-s",
        "-i",
        "-X",
        "POST",
        f"{BASE_URL}/chat/session/start",
        "-H",
        f"Origin: {ORIGIN}",
        "-H",
        "Content-Type: application/json",
        "--data-raw",
        json.dumps(payload, separators=(",", ":")),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
    raw = completed.stdout or completed.stderr
    header_text, _, body = raw.partition("\r\n\r\n")
    if not body:
        header_text, _, body = raw.partition("\n\n")
    status_code = None
    allow_origin = None
    for line in header_text.splitlines():
        lower = line.lower()
        if lower.startswith("http/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status_code = int(parts[1])
        if lower.startswith("access-control-allow-origin:"):
            allow_origin = line.split(":", 1)[1].strip()
    return {
        "endpoint": "/chat/session/start",
        "origin": ORIGIN,
        "transport": "curl_fallback",
        "contact_details_sent": False,
        "intentional_lead_task_customer_creation": False,
        "status_code": status_code,
        "cors_allow_origin_present": bool(allow_origin),
        "cors_allow_origin": allow_origin,
        "sanitized_response_body": _safe_body(body),
    }


if __name__ == "__main__":
    raise SystemExit(main())
