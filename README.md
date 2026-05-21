# Alte AI CRM Chatbot

AI-powered website chatbot and CRM backend foundation for Alte University / alte.edu.ge.

Current phase: Phase 4 knowledge base governance with mock retrieval.

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

Phase 2 adds website chat backend flow with deterministic mock AI analysis. The mock analyzer returns structured intent, confidence, contact extraction, missing fields, handover flags, and source-domain signals. Chat services apply business rules and decide whether to create customers, leads, tasks, messages, handover, and audit events.

Phase 3 extends the same mock chat flow with lead qualification: contact extraction, preferred program detection, qualification intent, urgency, lead score, qualification status, handover reason, and recommended next action. Qualification is stored on linked leads when a lead exists.

Phase 4 adds a controlled local knowledge base: approved sources, snippets, source status governance, language/category/program filtering, stale-source flags, and mock keyword retrieval. Chat answers can now mark whether they used an approved source, found no approved source, or hit a stale source.

Real Claude API calls, frontend, widget UI, WhatsApp, Messenger, Instagram, Email, and advanced routing remain intentionally out of scope until later phases.

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
- Chat: `/chat/session/start`, `/chat/message`, `/chat/handover/{conversation_id}`, `/chat/session/{conversation_id}/qualification`
- Knowledge: `/knowledge/sources`, `/knowledge/snippets`, `/knowledge/snippets/search`

## Phase 2 Chat Examples

Start a website chat session:

```powershell
curl -X POST http://127.0.0.1:8000/chat/session/start `
  -H "Content-Type: application/json" `
  -d "{\"source_domain\":\"alte.edu.ge\",\"language\":\"ka\"}"
```

Send a general contact question:

```powershell
curl -X POST http://127.0.0.1:8000/chat/message `
  -H "Content-Type: application/json" `
  -d "{\"conversation_id\":\"<conversation_id>\",\"message\":\"სად მდებარეობს უნივერსიტეტი?\",\"source_domain\":\"alte.edu.ge\"}"
```

Send an admissions message with contact data:

```powershell
curl -X POST http://127.0.0.1:8000/chat/message `
  -H "Content-Type: application/json" `
  -d "{\"conversation_id\":\"<conversation_id>\",\"message\":\"ნინო ბერიძე, +995599000000, nino@example.com მაინტერესებს ბიზნესის პროგრამა\",\"source_domain\":\"alte.edu.ge\"}"
```

Send a join.alte.edu.ge international medicine inquiry:

```powershell
curl -X POST http://127.0.0.1:8000/chat/message `
  -H "Content-Type: application/json" `
  -d "{\"conversation_id\":\"<conversation_id>\",\"message\":\"I want to apply for medicine from India, my email is test@example.com\",\"source_domain\":\"join.alte.edu.ge\"}"
```

Request handover:

```powershell
curl -X POST http://127.0.0.1:8000/chat/handover/<conversation_id>
```

Phase 2 AI is mocked and deterministic. Real Anthropic Claude integration is planned for Phase 3.

Phase 3 still uses mocked deterministic analysis. Real Anthropic Claude integration remains out of scope until explicitly approved.

Read current lead qualification:

```powershell
curl http://127.0.0.1:8000/chat/session/<conversation_id>/qualification
```

## Phase 4 Knowledge Examples

Create an approved source:

```powershell
curl -X POST http://127.0.0.1:8000/knowledge/sources `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Admissions FAQ\",\"source_type\":\"faq\",\"status\":\"approved\",\"language\":\"en\",\"owner\":\"Admissions\"}"
```

Create an approved snippet:

```powershell
curl -X POST http://127.0.0.1:8000/knowledge/snippets `
  -H "Content-Type: application/json" `
  -d "{\"source_id\":\"<source_id>\",\"title\":\"Business admission requirements\",\"content\":\"Business admission requires an application and documents.\",\"category\":\"admissions\",\"program_name\":\"Business\",\"keywords\":\"business admission requirements application\",\"status\":\"approved\",\"language\":\"en\"}"
```

Search snippets:

```powershell
curl "http://127.0.0.1:8000/knowledge/snippets/search?query=business%20admission&language=en"
```

Chat retrieval uses approved local snippets only. If no approved source exists for tuition, scholarship, or requirements questions, the chat response asks for verified admissions/consultant confirmation instead of inventing details.
