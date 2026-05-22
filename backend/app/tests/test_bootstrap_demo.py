import asyncio

from sqlalchemy import select

from app.models import Department, KnowledgeSnippet, KnowledgeSource, Pipeline, PipelineStage, User
from app.services.bootstrap_service import bootstrap_local_demo_data
from app.services.security_service import verify_password


def test_bootstrap_demo_creates_reference_data_idempotently(session_factory):
    async def run():
        async with session_factory() as session:
            first = await bootstrap_local_demo_data(session)
            second = await bootstrap_local_demo_data(session)
            departments = (await session.scalars(select(Department))).all()
            pipelines = (await session.scalars(select(Pipeline))).all()
            stages = (await session.scalars(select(PipelineStage))).all()
            sources = (await session.scalars(select(KnowledgeSource))).all()
            snippets = (await session.scalars(select(KnowledgeSnippet))).all()
            return first, second, departments, pipelines, stages, sources, snippets

    first, second, departments, pipelines, stages, sources, snippets = asyncio.run(run())

    assert first["departments"] == 4
    assert first["pipelines"] == 1
    assert first["pipeline_stages"] == 7
    assert first["knowledge_sources"] == 1
    assert first["knowledge_snippets"] == 3
    assert first["admin_user_created"] is False
    assert second == {
        "departments": 0,
        "pipelines": 0,
        "pipeline_stages": 0,
        "knowledge_sources": 0,
        "knowledge_snippets": 0,
        "admin_user_created": False,
    }
    assert len(departments) == 4
    assert len(pipelines) == 1
    assert len(stages) == 7
    assert len(sources) == 1
    assert len(snippets) == 3


def test_bootstrap_demo_creates_admin_only_from_env(session_factory, monkeypatch):
    monkeypatch.setenv("ALTE_BOOTSTRAP_ADMIN_EMAIL", "admin@alte.edu.ge")
    monkeypatch.setenv("ALTE_BOOTSTRAP_ADMIN_PASSWORD", "local-password")
    monkeypatch.setenv("ALTE_BOOTSTRAP_ADMIN_NAME", "Local Admin")

    async def run():
        async with session_factory() as session:
            first = await bootstrap_local_demo_data(session)
            second = await bootstrap_local_demo_data(session)
            user = await session.scalar(select(User).where(User.email == "admin@alte.edu.ge"))
            return first, second, user

    first, second, user = asyncio.run(run())

    assert first["admin_user_created"] is True
    assert second["admin_user_created"] is False
    assert user is not None
    assert user.role == "admin"
    assert user.password_hash != "local-password"
    assert verify_password("local-password", user.password_hash)

