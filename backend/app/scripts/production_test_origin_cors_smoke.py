from __future__ import annotations

import json
from dataclasses import dataclass

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
TEST_ORIGIN = "https://alte-ai-chat-test.netlify.app"
EXPECTED_ALLOWED_ORIGINS = [
    "https://alte.edu.ge",
    "https://join.alte.edu.ge",
    TEST_ORIGIN,
]
BLOCKED_ORIGIN = "https://evil.example.com"
ENDPOINTS = ["/chat/session/start", "/chat/message"]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def preflight(client: httpx.Client, endpoint: str, origin: str) -> httpx.Response:
    return client.options(
        endpoint,
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def allowed_origin_check(client: httpx.Client, endpoint: str, origin: str) -> Check:
    response = preflight(client, endpoint, origin)
    allow_origin = response.headers.get("access-control-allow-origin")
    allow_methods = response.headers.get("access-control-allow-methods", "")
    allow_headers = response.headers.get("access-control-allow-headers", "")
    passed = (
        response.status_code < 400
        and allow_origin == origin
        and "POST" in allow_methods.upper()
        and "content-type" in allow_headers.lower()
    )
    return Check(
        name=f"{origin} preflight {endpoint}",
        passed=passed,
        detail=f"status={response.status_code}; allow_origin={allow_origin}; allow_methods={allow_methods}; allow_headers={allow_headers}",
    )


def blocked_origin_check(client: httpx.Client, endpoint: str) -> Check:
    response = preflight(client, endpoint, BLOCKED_ORIGIN)
    allow_origin = response.headers.get("access-control-allow-origin")
    passed = response.status_code >= 400 or allow_origin != BLOCKED_ORIGIN
    return Check(
        name=f"{BLOCKED_ORIGIN} blocked {endpoint}",
        passed=passed,
        detail=f"status={response.status_code}; allow_origin={allow_origin}",
    )


def run_smoke() -> dict[str, object]:
    checks: list[Check] = []
    with httpx.Client(base_url=PRODUCTION_BACKEND_URL, timeout=20.0) as client:
        for endpoint in ENDPOINTS:
            for origin in EXPECTED_ALLOWED_ORIGINS:
                checks.append(allowed_origin_check(client, endpoint, origin))
            checks.append(blocked_origin_check(client, endpoint))

    failures = [check.__dict__ for check in checks if not check.passed]
    return {
        "total_tests": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "failures": failures,
        "test_origin": TEST_ORIGIN,
        "old_origins_still_allowed": all(
            check.passed
            for check in checks
            if check.name.startswith("https://alte.edu.ge") or check.name.startswith("https://join.alte.edu.ge")
        ),
        "test_origin_allowed": all(check.passed for check in checks if check.name.startswith(TEST_ORIGIN)),
        "random_origin_blocked": all(check.passed for check in checks if check.name.startswith(BLOCKED_ORIGIN)),
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
