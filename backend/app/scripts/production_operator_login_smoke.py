from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[3]
CREDENTIAL_FILE = ROOT / ".local-secrets" / "temporary_crm_admin_credentials.txt"
DEFAULT_BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
PROTECTED_ENDPOINT = "/dashboard/overview"


class SmokeError(RuntimeError):
    pass


def read_credentials(path: Path = CREDENTIAL_FILE) -> tuple[str, str]:
    if not path.exists():
        raise SmokeError("Credential file missing")

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = raw_line.partition("=")
        if separator:
            values[key.strip().lower()] = value.strip()

    email = values.get("email", "")
    password = values.get("password", "")
    if not email or not password:
        raise SmokeError("Credential file is missing required keys")
    return email, password


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
) -> tuple[int, dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=30) as response:
            status = int(response.status)
            text = response.read().decode("utf-8")
    except HTTPError as exc:
        status = int(exc.code)
        text = exc.read().decode("utf-8", errors="replace")
    except URLError as exc:
        raise SmokeError(f"Network request failed: {exc.reason}") from exc

    if not text:
        return status, {}
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"Non-JSON response from {url}") from exc
    if not isinstance(decoded, dict):
        raise SmokeError(f"Unexpected JSON response from {url}")
    return status, decoded


def run_smoke(base_url: str | None = None) -> dict[str, str]:
    base = (base_url or os.getenv("ALTE_OPERATOR_SMOKE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    email, password = read_credentials()

    login_status, login_payload = request_json(
        "POST",
        f"{base}/auth/login",
        {"email": email.strip().lower(), "password": password},
    )
    if login_status != 200:
        detail = str(login_payload.get("detail") or "login failed")
        raise SmokeError(f"Login failed with HTTP {login_status}: {detail}")

    token = str(login_payload.get("access_token") or "")
    if not token:
        raise SmokeError("Login response did not include an access token")

    protected_status, protected_payload = request_json(
        "GET",
        f"{base}{PROTECTED_ENDPOINT}",
        token=token,
    )
    if protected_status != 200:
        detail = str(protected_payload.get("detail") or "protected endpoint failed")
        raise SmokeError(f"Protected endpoint failed with HTTP {protected_status}: {detail}")
    if not isinstance(protected_payload, dict):
        raise SmokeError("Protected endpoint did not return an object")

    return {
        "email": email.strip().lower(),
        "login_status": str(login_status),
        "token_returned": "YES",
        "protected_endpoint": PROTECTED_ENDPOINT,
        "protected_status": str(protected_status),
    }


def main() -> None:
    result = run_smoke()
    print("PRODUCTION_OPERATOR_LOGIN_SMOKE_STATUS=PASS")
    print(f"USER_EMAIL={result['email']}")
    print(f"LOGIN_HTTP_STATUS={result['login_status']}")
    print(f"TOKEN_RETURNED={result['token_returned']}")
    print(f"PROTECTED_ENDPOINT={result['protected_endpoint']}")
    print(f"PROTECTED_HTTP_STATUS={result['protected_status']}")


if __name__ == "__main__":
    main()
