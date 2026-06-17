from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"


def curl_request(method: str, path: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    system_curl = Path("C:/Windows/System32/curl.exe")
    curl = shutil.which("curl.exe") or shutil.which("curl") or (str(system_curl) if system_curl.exists() else None)
    if not curl:
        return {"status": None, "headers": {}, "body": "", "error": "curl_not_found"}
    command = [
        curl,
        "-4",
        "-s",
        "-i",
        "-X",
        method,
        f"{BASE_URL}{path}",
        "-H",
        f"Origin: {ORIGIN}",
    ]
    if payload is not None:
        command.extend(["-H", "Content-Type: application/json", "--data-raw", json.dumps(payload, separators=(",", ":"))])
    completed = None
    for attempt in range(3):
        completed = subprocess.run(command, capture_output=True, text=True, timeout=45)
        if completed.returncode == 0 and completed.stdout:
            break
        time.sleep(0.5 * (attempt + 1))
    assert completed is not None
    raw = completed.stdout or completed.stderr
    header_text, _, body = raw.partition("\r\n\r\n")
    if not body:
        header_text, _, body = raw.partition("\n\n")
    status = None
    headers: dict[str, str] = {}
    for line in header_text.splitlines():
        if line.lower().startswith("http/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status = int(parts[1])
        elif ":" in line:
            key, value = line.split(":", 1)
            headers[key.lower().strip()] = value.strip()
    return {"status": status, "headers": headers, "body": body[:2000], "error": None if completed.returncode == 0 else "curl_failed"}


def parse_json(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def check(passed: bool, name: str, detail: str, checks: list[dict[str, Any]]) -> None:
    checks.append({"name": name, "passed": passed, "detail": detail})


def main() -> int:
    checks: list[dict[str, Any]] = []
    health = curl_request("GET", "/health")
    check(health["status"] == 200, "GET /health", f"status={health['status']}", checks)

    diagnostics = curl_request("GET", "/diagnostics/ai")
    diagnostics_json = parse_json(diagnostics["body"])
    check(diagnostics["status"] == 200, "GET /diagnostics/ai", f"status={diagnostics['status']}", checks)
    check(diagnostics_json.get("claude_enabled") is True, "Claude enabled", "claude_enabled=true", checks)

    session_payload = {
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "channel": "website_chat",
        "widget_variant": "pro_v2_safe",
        "metadata": {
            "mode": "production_db_credential_smoke",
            "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html",
        },
    }
    session = curl_request("POST", "/chat/session/start", payload=session_payload)
    session_json = parse_json(session["body"])
    allow_origin = session["headers"].get("access-control-allow-origin")
    check(allow_origin == ORIGIN, "session CORS exact origin", f"allow_origin={allow_origin}", checks)
    check(session["status"] == 200, "POST /chat/session/start", f"status={session['status']}", checks)
    conversation_id = session_json.get("conversation_id")
    session_id = session_json.get("session_id")
    check(bool(conversation_id and session_id), "session identifiers returned", "present" if conversation_id and session_id else "missing", checks)

    message_json: dict[str, Any] = {}
    if conversation_id:
        message_payload = {
            "conversation_id": conversation_id,
            "session_id": session_id,
            "message": "What documents do international students need?",
            "source_domain": "join.alte.edu.ge",
            "language": "en",
            "selected_department": "international",
            "selected_topic": "documents",
            "widget_variant": "pro_v2_safe",
            "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html",
        }
        message = curl_request("POST", "/chat/message", payload=message_payload)
        message_json = parse_json(message["body"])
        check(message["headers"].get("access-control-allow-origin") == ORIGIN, "message CORS exact origin", f"allow_origin={message['headers'].get('access-control-allow-origin')}", checks)
        check(message["status"] == 200, "POST /chat/message", f"status={message['status']}", checks)
        created = [
            key
            for key in ["created_customer_id", "created_lead_id", "created_task_id"]
            if message_json.get(key)
        ]
        check(not created, "no CRM records created by harmless smoke", ",".join(created) if created else "none", checks)
    else:
        check(False, "POST /chat/message skipped", "session_start_failed", checks)

    result = {
        "origin": ORIGIN,
        "contact_details_sent": False,
        "contact_flow_test_run": False,
        "intentional_lead_task_customer_creation": False,
        "checks": checks,
        "message_response_keys": sorted(message_json.keys()) if message_json else [],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    failed = [item for item in checks if not item["passed"]]
    print("production_db_credential_smoke=" + ("PASS" if not failed else "FAIL"))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
