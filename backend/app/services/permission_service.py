from __future__ import annotations

from fastapi import Request

PUBLIC_PREFIXES = (
    "/health",
    "/version",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/chat/session/start",
    "/chat/message",
    "/chat/handover",
)

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"*"},
    "manager": {
        "dashboard:read",
        "inbox:read",
        "conversation:read",
        "lead:read",
        "lead:write",
        "task:read",
        "task:write",
        "pipeline:read",
        "knowledge:read",
        "knowledge:write",
        "deadline:read",
        "department:read",
        "customer:read",
    },
    "admissions_user": {
        "dashboard:read",
        "inbox:read",
        "conversation:read",
        "lead:read",
        "lead:write",
        "task:read",
        "task:write",
        "pipeline:read",
        "knowledge:read",
        "customer:read",
    },
    "international_admissions_user": {
        "dashboard:read",
        "inbox:read",
        "conversation:read",
        "lead:read",
        "lead:write",
        "task:read",
        "task:write",
        "pipeline:read",
        "knowledge:read",
        "customer:read",
    },
    "finance_user": {
        "dashboard:read",
        "inbox:read",
        "conversation:read",
        "lead:read",
        "task:read",
        "task:write",
        "knowledge:read",
        "customer:read",
    },
    "student_services_user": {
        "inbox:read",
        "conversation:read",
        "task:read",
        "task:write",
        "knowledge:read",
        "customer:read",
    },
    "operator": {
        "inbox:read",
        "conversation:read",
        "lead:read",
        "task:read",
        "knowledge:read",
        "customer:read",
    },
}


def is_public_path(path: str) -> bool:
    return any(path == prefix or path.startswith(f"{prefix}/") for prefix in PUBLIC_PREFIXES)


def permission_for_request(request: Request) -> str | None:
    path = request.url.path
    method = request.method.upper()

    if path.startswith("/dashboard"):
        return "dashboard:read"
    if path.startswith("/inbox"):
        return "inbox:read"
    if path.startswith("/conversations"):
        return "conversation:read"
    if path.startswith("/leads"):
        return "lead:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "lead:read"
    if path.startswith("/tasks"):
        return "task:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "task:read"
    if path.startswith("/pipelines") or path.startswith("/pipeline-stages"):
        return "pipeline:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "pipeline:read"
    if path.startswith("/knowledge"):
        return "knowledge:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "knowledge:read"
    if path.startswith("/deadlines"):
        return "deadline:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "deadline:read"
    if path.startswith("/departments"):
        return "department:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "department:read"
    if path.startswith("/customers"):
        return "customer:write" if method in {"POST", "PATCH", "PUT", "DELETE"} else "customer:read"
    return None


def role_has_permission(role: str, permission: str | None) -> bool:
    if permission is None:
        return True
    permissions = ROLE_PERMISSIONS.get(role, set())
    return "*" in permissions or permission in permissions

