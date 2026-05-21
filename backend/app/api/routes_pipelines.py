from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Pipeline, PipelineStage
from app.schemas.crm import PipelineCreate, PipelineRead, PipelineStageCreate, PipelineStageRead

router = APIRouter(tags=["pipelines"])


@router.post("/pipelines", response_model=PipelineRead)
async def create_pipeline(payload: PipelineCreate, db: AsyncSession = Depends(get_db)):
    pipeline = Pipeline(**payload.model_dump())
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
    return pipeline


@router.get("/pipelines", response_model=list[PipelineRead])
async def list_pipelines(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Pipeline).order_by(Pipeline.created_at.desc()))).all()


@router.post("/pipeline-stages", response_model=PipelineStageRead)
async def create_pipeline_stage(payload: PipelineStageCreate, db: AsyncSession = Depends(get_db)):
    stage = PipelineStage(**payload.model_dump())
    db.add(stage)
    await db.commit()
    await db.refresh(stage)
    return stage


@router.get("/pipeline-stages", response_model=list[PipelineStageRead])
async def list_pipeline_stages(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(PipelineStage).order_by(PipelineStage.order.asc()))).all()
