from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.operator import InboxListItem
from app.services.operator_service import build_inbox_items

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("", response_model=list[InboxListItem])
async def list_inbox(
    limit: int = 20,
    offset: int = 0,
    channel: str | None = None,
    status: str | None = None,
    human_handover: bool | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await build_inbox_items(
        db,
        limit=limit,
        offset=offset,
        channel=channel,
        status=status,
        human_handover=human_handover,
        q=q,
    )
