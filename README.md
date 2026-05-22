# Alte AI CRM Chatbot

AI-powered website chatbot and CRM backend foundation for Alte University / alte.edu.ge.

Current phase: Phase 5B CRM operator frontend shell.

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

Phase 5A prepares backend-only operator dashboard API responses: dashboard overview cards, filtered inbox, conversation details, lead list/detail, task list, pipeline board data, and knowledge admin filters. No frontend is included.

Phase 5B adds a static CRM operator frontend shell in `frontend/`. It uses the Phase 5A backend APIs for dashboard overview, inbox, conversation detail, leads, lead detail, pipeline board, tasks, knowledge sources, and knowledge snippet search. It does not add authentication, real Claude calls, external channels, or website widget behavior.

Phase 5C adds backend authentication and security hardening: password hashing, token login, `/auth/me`, optional `AUTH_REQUIRED` route protection, role permission checks, correlation IDs, response secret sanitizing helpers, and security tests. Authentication is disabled by default for local compatibility and can be enabled with `AUTH_REQUIRED=true`.

Real Claude API calls, website widget UI, WhatsApp, Messenger, Instagram, Email, and advanced routing remain intentionally out of scope until later phases.

Bridge Hub reference material has been copied under `docs/reference/bridge-hub/` for architecture and safety guidance only. The Alte-specific mapping is documented in `docs/alte-bridge-reference-adaptation-plan.md`.

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
- Dashboard: `/dashboard/overview`
- Operator readiness: filtered `/inbox`, `/leads`, `/tasks`, `/conversations/{id}/detail`, `/leads/{id}/detail`, `/pipelines/{id}/board`
- Auth: `/auth/login`, `/auth/me`

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

## Phase 5A Operator API Examples

Dashboard overview:

```powershell
curl http://127.0.0.1:8000/dashboard/overview
```

Filtered inbox:

```powershell
curl "http://127.0.0.1:8000/inbox?limit=20&offset=0&channel=website_chat&q=business"
```

Lead list:

```powershell
curl "http://127.0.0.1:8000/leads?source_domain=join.alte.edu.ge&medical_track=true"
```

Task list:

```powershell
curl "http://127.0.0.1:8000/tasks?status=open&overdue=false"
```

Pipeline board:

```powershell
curl "http://127.0.0.1:8000/pipelines/<pipeline_id>/board?leads_per_stage=20"
```

## Phase 5B Operator Frontend

Start the backend:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Serve the frontend:

```powershell
cd C:\tmp\alte-ai-crm\frontend
python -m http.server 5173
```

Open:

```text
http://127.0.0.1:5173
```

The frontend is intentionally dependency-free in this phase. It can later be replaced by a Next.js/React app after CRM workflows and security are stable.

## Phase 5C Auth / Security

Authentication is optional in local development:

```env
AUTH_REQUIRED=false
```

To enforce token authentication and role checks for operator/CRM endpoints:

```env
AUTH_REQUIRED=true
```

Login:

```powershell
curl -X POST http://127.0.0.1:8000/auth/login `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"admin@alte.edu.ge\",\"password\":\"password123\"}"
```

Use the returned bearer token:

```powershell
curl http://127.0.0.1:8000/auth/me `
  -H "Authorization: Bearer <token>"
```

The static operator frontend has a Settings login form and sends the stored token on API requests.
