from fastapi import Request
from app.api.tenant_context import resolve_tenant_id


async def tenant_middleware(request: Request, call_next):
    tenant_id = (
        request.headers.get("X-Tenant-ID")
        or request.query_params.get("tenant_id")
        or "default"
    )

    request.state.tenant_id = resolve_tenant_id(tenant_id)

    response = await call_next(request)
    return response