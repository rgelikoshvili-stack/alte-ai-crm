from __future__ import annotations

import json
from dataclasses import dataclass

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

CASES = [
    {
        "name": "alte ka test site session",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "mode": "test_site",
    },
    {
        "name": "join en test site session",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "mode": "test_site",
    },
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def build_session_payload(case: dict[str, str]) -> dict[str, object]:
    return {
        "source_domain": case["source_domain"],
        "language": case["language"],
        "channel": "website_chat",
        "widget_variant": "safe_pro_sidebar",
        "metadata": {
            "mode": case["mode"],
            "page_url": f"https://{case['source_domain']}/test-site",
        },
    }


def check_session_start(client: httpx.Client, case: dict[str, str]) -> Check:
    payload = build_session_payload(case)
    response = client.post("/chat/session/start", json=payload)
    if response.status_code != 200:
        return Check(case["name"], False, f"status={response.status_code}; body={response.text[:300]}")
    data = response.json()
    required = ["conversation_id", "session_id", "source_domain"]
    missing = [field for field in required if not data.get(field)]
    source_ok = data.get("source_domain") == case["source_domain"]
    passed = not missing and source_ok
    detail = f"missing={missing}; source_domain={data.get('source_domain')}"
    return Check(case["name"], passed, detail)


def run_smoke() -> dict[str, object]:
    checks: list[Check] = []
    with httpx.Client(base_url=PRODUCTION_BACKEND_URL, timeout=30.0) as client:
        for case in CASES:
            checks.append(check_session_start(client, case))
    failures = [check.__dict__ for check in checks if not check.passed]
    return {
        "total_tests": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "failures": failures,
        "no_contact_details_sent": True,
        "contact_flow_test_run": False,
        "intentional_lead_task_customer_creation": False,
        "payload_channel": "website_chat",
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
