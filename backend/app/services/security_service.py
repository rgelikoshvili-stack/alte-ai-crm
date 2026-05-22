from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings

PBKDF2_ITERATIONS = 120_000


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    try:
        algorithm, iterations_raw, salt_raw, digest_raw = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_raw)
        salt = _b64url_decode(salt_raw)
        expected = _b64url_decode(digest_raw)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expires = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "role": role, "exp": int(expires.timestamp())}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(settings.JWT_SECRET.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    settings = get_settings()
    try:
        header_raw, payload_raw, signature_raw = token.split(".", 2)
        signing_input = f"{header_raw}.{payload_raw}"
        expected_signature = hmac.new(
            settings.JWT_SECRET.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64url_decode(signature_raw), expected_signature):
            return None
        payload = json.loads(_b64url_decode(payload_raw))
        if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
            return None
        return payload
    except (ValueError, TypeError, json.JSONDecodeError):
        return None

