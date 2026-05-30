from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.services.permission_service import is_public_path, permission_for_request, role_has_permission
from app.services.security_service import decode_access_token


async def correlation_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID") or str(uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


async def safe_error_response_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )


async def auth_rbac_middleware(request: Request, call_next):
    settings = get_settings()
    if request.method.upper() == "OPTIONS":
        return await call_next(request)

    if not settings.AUTH_REQUIRED or is_public_path(request.url.path):
        return await call_next(request)

    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return JSONResponse(status_code=401, content={"detail": "Missing bearer token"})

    payload = decode_access_token(token)
    if payload is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid bearer token"})

    role = str(payload.get("role") or "")
    permission = permission_for_request(request)
    if not role_has_permission(role, permission):
        return JSONResponse(status_code=403, content={"detail": "Permission denied"})

    request.state.user_id = payload.get("sub")
    request.state.role = role
    request.state.authenticated = True
    return await call_next(request)
