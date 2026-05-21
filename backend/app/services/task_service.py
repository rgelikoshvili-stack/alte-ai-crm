from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.schemas.crm import TaskCreate, TaskUpdate
from app.services.audit_service import audit_event


async def create_task(db: AsyncSession, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    await db.flush()
    await audit_event(db, action="task_created", entity_type="task", entity_id=task.id)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, task: Task, payload: TaskUpdate) -> Task:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def complete_task(db: AsyncSession, task: Task) -> Task:
    task.status = "completed"
    task.completed_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(task)
    return task
