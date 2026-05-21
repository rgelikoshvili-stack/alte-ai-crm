from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import DeadlineTracking
from app.schemas.crm import DeadlineCreate, DeadlineRead, DeadlineUpdate

router = APIRouter(prefix="/deadlines", tags=["deadlines"])


@router.post("", response_model=DeadlineRead)
async def create_deadline(payload: DeadlineCreate, db: AsyncSession = Depends(get_db)):
    deadline = DeadlineTracking(**payload.model_dump())
    db.add(deadline)
    await db.commit()
    await db.refresh(deadline)
    return deadline


@router.get("", response_model=list[DeadlineRead])
async def list_deadlines(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(DeadlineTracking).order_by(DeadlineTracking.deadline_date.asc()))).all()


@router.patch("/{deadline_id}", response_model=DeadlineRead)
async def update_deadline(deadline_id: str, payload: DeadlineUpdate, db: AsyncSession = Depends(get_db)):
    deadline = await get_or_404(db, DeadlineTracking, deadline_id, "Deadline")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(deadline, field, value)
    await db.commit()
    await db.refresh(deadline)
    return deadline
