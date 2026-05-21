# Alte AI CRM Chatbot

AI-powered website chatbot and CRM backend foundation for Alte University / alte.edu.ge.

Current phase: Phase 1 CRM core backend.

## Stack

- Python
- FastAPI
- SQLAlchemy async engine
- Alembic
- PostgreSQL with asyncpg
- Pydantic / pydantic-settings
- Anthropic Claude API placeholder
- Pytest

## Create Virtual Environment

```powershell
cd C:\tmp\alte-ai-crm\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Install Requirements

```powershell
pip install -r requirements.txt
```

## Configure Environment

```powershell
Copy-Item .env.example .env
```

Update `.env` with local values. Do not commit real secrets.

## Run Backend

```powershell
cd C:\tmp\alte-ai-crm\backend
uvicorn app.main:app --reload
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

## Run Tests

```powershell
cd C:\tmp\alte-ai-crm\backend
pytest
```

## Current Scope

Phase 0 includes the backend foundation: FastAPI app, settings, database base/session setup, Alembic wiring, system routes, Anthropic client placeholder, and system tests.

Phase 1 adds CRM core backend tables, schemas, services, routes, audit logging, customer duplicate detection, lead stage history, tasks, conversations/messages, pipelines, and deadline tracking.

AI calls, frontend, widget UI, WhatsApp, Messenger, Instagram, Email, and advanced routing remain intentionally out of scope until later phases.

## Run Migrations

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

## Phase 1 Endpoint Areas

- System: `/health`, `/version`
- Departments: `/departments`
- Customers: `/customers`, `/customers/search`
- Leads: `/leads`, `/leads/{lead_id}/stage`
- Conversations: `/conversations`, `/conversations/{conversation_id}/messages`
- Inbox: `/inbox`
- Tasks: `/tasks`, `/tasks/{task_id}/complete`
- Pipelines: `/pipelines`, `/pipeline-stages`
- Deadlines: `/deadlines`
