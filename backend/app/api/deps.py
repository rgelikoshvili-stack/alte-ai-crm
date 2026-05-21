from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_404(db: AsyncSession, model, entity_id: str, label: str):
    entity = await db.get(model, entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return entity
