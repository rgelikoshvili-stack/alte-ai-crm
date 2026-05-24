from __future__ import annotations

import asyncio
import json

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import Department, Pipeline, PipelineStage
from app.services.bootstrap_service import DEFAULT_DEPARTMENTS, DEFAULT_STAGES


async def bootstrap_production_core() -> dict[str, int]:
    created = {"departments": 0, "pipelines": 0, "pipeline_stages": 0}
    async with AsyncSessionLocal() as db:
        departments: dict[str, Department] = {}
        for name, description, queue in DEFAULT_DEPARTMENTS:
            department = await db.scalar(select(Department).where(Department.name == name))
            if department is None:
                department = Department(name=name, description=description, default_queue=queue, is_active=True)
                db.add(department)
                await db.flush()
                created["departments"] += 1
            departments[name] = department

        pipeline = await db.scalar(select(Pipeline).where(Pipeline.name == "Admissions Pipeline"))
        if pipeline is None:
            pipeline = Pipeline(name="Admissions Pipeline", department_id=departments["Admissions"].id, is_active=True)
            db.add(pipeline)
            await db.flush()
            created["pipelines"] += 1

        existing_stage_names = set(
            (
                await db.scalars(select(PipelineStage.name).where(PipelineStage.pipeline_id == pipeline.id))
            ).all()
        )
        for name, order, is_final, is_lost in DEFAULT_STAGES:
            if name not in existing_stage_names:
                db.add(
                    PipelineStage(
                        pipeline_id=pipeline.id,
                        name=name,
                        order=order,
                        is_final=is_final,
                        is_lost=is_lost,
                    )
                )
                created["pipeline_stages"] += 1

        await db.commit()
    return created


async def main_async() -> None:
    result = await bootstrap_production_core()
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
