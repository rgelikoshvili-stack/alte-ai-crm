from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import Department
from app.schemas.crm import DepartmentCreate, DepartmentRead
from app.services.audit_service import audit_event

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("", response_model=DepartmentRead)
async def create_department(payload: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    department = Department(**payload.model_dump())
    db.add(department)
    await db.flush()
    await audit_event(db, action="department_created", entity_type="department", entity_id=department.id)
    await db.commit()
    await db.refresh(department)
    return department


@router.get("", response_model=list[DepartmentRead])
async def list_departments(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Department).order_by(Department.created_at.desc()))).all()


@router.get("/{department_id}", response_model=DepartmentRead)
async def get_department(department_id: str, db: AsyncSession = Depends(get_db)):
    return await get_or_404(db, Department, department_id, "Department")
