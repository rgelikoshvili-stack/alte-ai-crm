from __future__ import annotations

import os
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department, KnowledgeSnippet, KnowledgeSource, Pipeline, PipelineStage, User
from app.services.security_service import hash_password

DEFAULT_DEPARTMENTS = [
    ("Admissions", "Local admissions queue", "admissions"),
    ("International Admissions", "International admissions and join.alte.edu.ge queue", "international_admissions"),
    ("Finance", "Tuition, scholarship and payment follow-up", "finance"),
    ("Student Services", "Student support and service desk", "student_services"),
]

DEFAULT_STAGES = [
    ("New", 1, False, False),
    ("Qualified", 2, False, False),
    ("Consultation Scheduled", 3, False, False),
    ("Documents Requested", 4, False, False),
    ("Application Submitted", 5, False, False),
    ("Won / Enrolled", 6, True, False),
    ("Lost", 7, True, True),
]

DEFAULT_KNOWLEDGE_SNIPPETS = [
    {
        "title": "Business program admissions",
        "content": "Business program admission details must be verified by the admissions team before final submission.",
        "category": "admissions",
        "program_name": "Business",
        "keywords": "business admission requirements application",
        "language": "en",
    },
    {
        "title": "Medicine / 6-year MD international flow",
        "content": "International Medicine / 6-year MD applicants should be reviewed by International Admissions.",
        "category": "admissions",
        "program_name": "Medicine / 6-year MD",
        "keywords": "medicine md international india visa relocation",
        "language": "en",
    },
    {
        "title": "Tuition requires confirmation",
        "content": "Exact tuition, payment schedule and scholarship information must be confirmed by an authorized consultant.",
        "category": "tuition",
        "program_name": None,
        "keywords": "tuition fee scholarship payment price",
        "language": "en",
    },
]


async def bootstrap_local_demo_data(db: AsyncSession) -> dict[str, int | bool]:
    created = {
        "departments": 0,
        "pipelines": 0,
        "pipeline_stages": 0,
        "knowledge_sources": 0,
        "knowledge_snippets": 0,
        "admin_user_created": False,
    }

    departments: dict[str, Department] = {}
    for name, description, queue in DEFAULT_DEPARTMENTS:
        department = await get_department(db, name)
        if department is None:
            department = Department(name=name, description=description, default_queue=queue, is_active=True)
            db.add(department)
            await db.flush()
            created["departments"] += 1
        departments[name] = department

    pipeline = await get_pipeline(db, "Admissions Pipeline")
    if pipeline is None:
        pipeline = Pipeline(name="Admissions Pipeline", department_id=departments["Admissions"].id, is_active=True)
        db.add(pipeline)
        await db.flush()
        created["pipelines"] += 1

    existing_stage_names = {
        stage.name
        for stage in (
            await db.scalars(select(PipelineStage).where(PipelineStage.pipeline_id == pipeline.id))
        ).all()
    }
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

    source = await get_knowledge_source(db, "Alte demo admissions knowledge")
    if source is None:
        source = KnowledgeSource(
            title="Alte demo admissions knowledge",
            source_type="manual",
            status="approved",
            language="en",
            owner="Admissions",
            approved_by="local-bootstrap",
            approved_at=datetime.now(UTC),
        )
        db.add(source)
        await db.flush()
        created["knowledge_sources"] += 1

    existing_snippet_titles = {
        snippet.title
        for snippet in (
            await db.scalars(select(KnowledgeSnippet).where(KnowledgeSnippet.source_id == source.id))
        ).all()
    }
    for item in DEFAULT_KNOWLEDGE_SNIPPETS:
        if item["title"] not in existing_snippet_titles:
            db.add(KnowledgeSnippet(source_id=source.id, status="approved", **item))
            created["knowledge_snippets"] += 1

    admin_created = await maybe_create_admin_user(db)
    created["admin_user_created"] = admin_created

    await db.commit()
    return created


async def maybe_create_admin_user(db: AsyncSession) -> bool:
    email = os.getenv("ALTE_BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ALTE_BOOTSTRAP_ADMIN_PASSWORD", "")
    name = os.getenv("ALTE_BOOTSTRAP_ADMIN_NAME", "Alte Admin").strip() or "Alte Admin"
    if not email or not password:
        return False

    existing = await db.scalar(select(User).where(User.email == email))
    if existing:
        return False

    db.add(
        User(
            name=name,
            email=email,
            role="admin",
            is_active=True,
            password_hash=hash_password(password),
        )
    )
    return True


async def get_department(db: AsyncSession, name: str) -> Department | None:
    return await db.scalar(select(Department).where(Department.name == name))


async def get_pipeline(db: AsyncSession, name: str) -> Pipeline | None:
    return await db.scalar(select(Pipeline).where(Pipeline.name == name))


async def get_knowledge_source(db: AsyncSession, title: str) -> KnowledgeSource | None:
    return await db.scalar(select(KnowledgeSource).where(KnowledgeSource.title == title))

