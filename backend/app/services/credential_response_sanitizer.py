from __future__ import annotations

from typing import Any

FORBIDDEN_RESPONSE_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "apiKey",
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "client_secret",
        "private_key",
    }
)
_FORBIDDEN_LOWER = frozenset(key.lower() for key in FORBIDDEN_RESPONSE_KEYS)


def sanitize_response(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            key: sanitize_response(value)
            for key, value in data.items()
            if key.lower() not in _FORBIDDEN_LOWER
        }
    if isinstance(data, list):
        return [sanitize_response(item) for item in data]
    return data


def assert_no_forbidden_response_fields(data: Any) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in _FORBIDDEN_LOWER:
                raise ValueError(f"Forbidden response field: {key}")
            assert_no_forbidden_response_fields(value)
    elif isinstance(data, list):
        for item in data:
            assert_no_forbidden_response_fields(item)


def mask_value(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) <= 4:
        return "****"
    return f"****{value[-4:]}"

