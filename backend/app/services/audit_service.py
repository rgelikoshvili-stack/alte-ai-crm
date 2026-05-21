from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def audit_event(
    db: AsyncSession,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None,
    actor_type: str = "system",
    actor_id: str | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> AuditLog:
    event = AuditLog(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata_json,
    )
    db.add(event)
    return event
