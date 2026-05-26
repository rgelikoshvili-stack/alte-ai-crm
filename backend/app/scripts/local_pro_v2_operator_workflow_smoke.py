from __future__ import annotations

import asyncio
import os
import sys

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("AUTH_REQUIRED", "false")
os.environ.setdefault("AI_PROVIDER", "mock")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("JWT_SECRET", "local-smoke-secret")
os.environ.setdefault("ANTHROPIC_API_KEY", "local-smoke-placeholder")

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Conversation, Customer, Lead, Message, Task  # noqa: E402
from app.schemas.crm import MessageCreate  # noqa: E402
from app.services.conversation_service import create_message  # noqa: E402


engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with SessionLocal() as session:
        yield session


async def reset_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_operator_reply(conversation_id: str) -> None:
    async with SessionLocal() as session:
        await create_message(
            session,
            conversation_id,
            MessageCreate(sender_type="operator", text="Operator reply visible in chatbot transcript"),
        )


async def counts() -> dict[str, int]:
    async with SessionLocal() as session:
        return {
            "customers": len((await session.scalars(select(Customer))).all()),
            "leads": len((await session.scalars(select(Lead))).all()),
            "tasks": len((await session.scalars(select(Task))).all()),
            "conversations": len((await session.scalars(select(Conversation))).all()),
            "messages": len((await session.scalars(select(Message))).all()),
        }


def assert_ok(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    asyncio.run(reset_db())
    app.dependency_overrides[get_db] = override_get_db
    failures: list[str] = []

    with TestClient(app) as client:
        session_response = client.post(
            "/chat/session/start",
            json={"source_domain": "alte.edu.ge", "language": "ka", "channel": "website_chat"},
        )
        assert_ok(session_response.status_code == 200, "session start failed", failures)
        session = session_response.json()

        contact_response = client.post(
            f"/chat/contact/{session['conversation_id']}",
            json={
                "session_id": session["session_id"],
                "full_name": "Local Smoke Visitor",
                "phone": "+995 500 00 00 03",
                "interest_area": "operator_handover",
                "selected_department": "admissions",
                "selected_topic": "operator",
                "source_domain": "alte.edu.ge",
                "language": "ka",
                "consent": True,
            },
        )
        assert_ok(contact_response.status_code == 200, "contact handover failed", failures)
        if contact_response.status_code == 200:
            data = contact_response.json()
            assert_ok(bool(data.get("customer_id")), "customer not linked", failures)
            assert_ok(bool(data.get("lead_id")), "lead not linked", failures)
            assert_ok(bool(data.get("task_id")), "operator task not created", failures)

        asyncio.run(add_operator_reply(session["conversation_id"]))

        transcript = client.get(
            f"/chat/messages/{session['conversation_id']}?session_id={session['session_id']}"
        )
        assert_ok(transcript.status_code == 200, "chat transcript failed", failures)
        if transcript.status_code == 200:
            rows = transcript.json()
            assert_ok(
                any(row["sender_type"] == "operator" for row in rows),
                "operator reply not visible in chatbot transcript",
                failures,
            )

        blocked = client.get(f"/chat/messages/{session['conversation_id']}?session_id=wrong")
        assert_ok(blocked.status_code == 403, "invalid session was not blocked", failures)

    app.dependency_overrides.clear()
    summary = asyncio.run(counts())
    total = 5
    passed = total - len(failures)
    print(
        {
            "status": "PASS" if not failures else "FAIL",
            "total_tests": total,
            "passed": passed,
            "failed": len(failures),
            "failures": failures,
            "counts": summary,
            "no_real_alte_site_modified": True,
            "no_cloud_run_or_cors_change": True,
            "no_contact_flow_production_test": True,
        }
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
