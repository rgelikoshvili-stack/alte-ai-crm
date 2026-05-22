from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import Task
from app.schemas.crm import TaskCreate, TaskRead, TaskUpdate
from app.schemas.operator import TaskListItem
from app.services.operator_service import build_task_items
from app.services.task_service import complete_task, create_task, update_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead)
async def create_task_route(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await create_task(db, payload)


@router.get("", response_model=list[TaskListItem])
async def list_tasks(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    department_id: str | None = None,
    assigned_user_id: str | None = None,
    overdue: bool | None = None,
    lead_id: str | None = None,
    customer_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await build_task_items(
        db,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        department_id=department_id,
        assigned_user_id=assigned_user_id,
        overdue=overdue,
        lead_id=lead_id,
        customer_id=customer_id,
    )


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task_route(task_id: str, payload: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await get_or_404(db, Task, task_id, "Task")
    return await update_task(db, task, payload)


@router.patch("/{task_id}/complete", response_model=TaskRead)
async def complete_task_route(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await get_or_404(db, Task, task_id, "Task")
    return await complete_task(db, task)
