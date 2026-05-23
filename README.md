# Alte AI CRM Chatbot

AI-powered website chatbot and CRM backend foundation for Alte University / alte.edu.ge.

Current status: `v0.7-local-mvp`

Checkpoint docs:

- `docs/PROJECT_STATUS.md`
- `docs/LOCAL_MVP_CHECKLIST.md`
- `docs/GITHUB_SETUP.md`
- `docs/releases/v0.7-local-mvp.md`
- `docs/EXTERNAL_SERVICES_SETUP.md`
- `docs/ENVIRONMENT_VARIABLES.md`
- `docs/NEXT_PHASES.md`

Release verification:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_release_checkpoint
```

Local package:

```powershell
cd C:\tmp\alte-ai-crm
.\scripts\create_local_mvp_package.ps1
```

External Services / Registration Checklist:

- GitHub repository
- Anthropic Console / Claude API
- Google Cloud project
- Cloud SQL PostgreSQL
- Alte website admin/developer access
- Meta Developers later, after website chat is stable

See:

- `docs/EXTERNAL_SERVICES_SETUP.md`
- `docs/ENVIRONMENT_VARIABLES.md`
- `docs/NEXT_PHASES.md`

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

Phase 6 adds backend analytics and SLA readiness endpoints for admissions performance, AI/mock response quality, source governance coverage, and operator task follow-up. It uses existing CRM, task, message, and knowledge tables only.

Phase 6B adds an Analytics view to the static operator frontend using the Phase 6 backend endpoints.

Phase 6C adds a local/demo bootstrap script for development data: departments, an admissions pipeline, pipeline stages, approved demo knowledge snippets, and an optional admin user from environment variables.

Phase 7A adds safe/staged Claude analysis support behind `AI_PROVIDER=claude` while keeping `AI_PROVIDER=mock` as the default for tests and local development. AI still returns structured analysis only; CRM changes remain controlled by services.

Website widget UI, WhatsApp, Messenger, Instagram, Email, and advanced routing remain intentionally out of scope until later phases.

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
- Analytics: `/analytics/overview`, `/analytics/leads`, `/analytics/sla`, `/analytics/knowledge`, `/analytics/ai`

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

The frontend is intentionally dependency-free in this phase. It includes dashboard, inbox, leads, pipeline, tasks, knowledge, analytics, and settings views. It can later be replaced by a Next.js/React app after CRM workflows and security are stable.

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

## Phase 6 Analytics / SLA

Overview:

```powershell
curl http://127.0.0.1:8000/analytics/overview
```

Lead analytics:

```powershell
curl http://127.0.0.1:8000/analytics/leads
```

SLA analytics:

```powershell
curl http://127.0.0.1:8000/analytics/sla
```

Knowledge governance analytics:

```powershell
curl http://127.0.0.1:8000/analytics/knowledge
```

AI/mock response analytics:

```powershell
curl http://127.0.0.1:8000/analytics/ai
```

## Phase 6C Local Bootstrap

Run migrations first:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Seed local demo data:

```powershell
python -m app.scripts.bootstrap_demo
```

Optional local admin user:

```powershell
$env:ALTE_BOOTSTRAP_ADMIN_EMAIL="admin@alte.edu.ge"
Read-Host "Local bootstrap admin password" | Set-Item Env:ALTE_BOOTSTRAP_ADMIN_PASSWORD
$env:ALTE_BOOTSTRAP_ADMIN_NAME="Alte Admin"
python -m app.scripts.bootstrap_demo
```

The bootstrap command is idempotent. Re-running it does not create duplicate departments, pipeline stages, knowledge sources, snippets, or admin users.

## Phase 7A Safe Claude Integration

Default local/test mode:

```env
AI_PROVIDER=mock
```

Claude mode:

```env
AI_PROVIDER=claude
AI_MODEL=claude-sonnet-4-5-20250929
AI_TIMEOUT_SECONDS=20
AI_CONFIDENCE_THRESHOLD=0.70
AI_MAX_TOKENS=1200
ANTHROPIC_API_KEY=your-anthropic-api-key
```

Claude calls are isolated in `app.services.ai_service`. The chat service receives an `AIAnalysisResult` and applies CRM business rules itself. Claude never writes customers, leads, tasks, messages, or handovers directly.

Safe fallback behavior:

- invalid JSON
- validation failure
- timeout/client failure
- low confidence below `AI_CONFIDENCE_THRESHOLD`
- missing approved knowledge for factual tuition/deadline/requirement questions

Tests mock Claude responses and do not require a real API key.

## Phase 7B Manual Alte Knowledge Seed

Phase 7B adds a local, manually maintained Alte knowledge seed. It is not scraping, crawling, or live website ingestion.

Seed file:

```text
backend/app/knowledge_seed/alte_seed_v1.json
```

Run migrations first, then seed the local database:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.scripts.seed_alte_knowledge
```

The seed command is idempotent. It creates missing `KnowledgeSource` and `KnowledgeSnippet` rows and skips existing snippets by deterministic content hash.

Knowledge governance rules:

- approved snippets are returned by default
- archived sources are excluded by default
- source metadata includes `source_key`, `source_domain`, `category`, `language`, `sensitivity`, and stale-review settings
- high-risk topics such as tuition, deadlines, admission requirements, medicine, visa, relocation, and policy facts must be verified from an approved current source or by a consultant
- the chatbot must not invent exact tuition, dates, documents, or official policy when no approved snippet exists

Useful local checks:

```powershell
curl "http://127.0.0.1:8000/knowledge/snippets/search?query=contact&language=en&category=contact"
curl "http://127.0.0.1:8000/knowledge/snippets/search?query=tuition%20fee&language=en&category=finance"
curl "http://127.0.0.1:8000/knowledge/snippets/search?query=medicine%20visa&language=en&source_domain=join.alte.edu.ge"
```

## Phase 7C Knowledge Review Admin Readiness

Phase 7C adds backend-only review and approval endpoints for manually governed knowledge content.

Review queue:

```powershell
curl "http://127.0.0.1:8000/knowledge/review-queue?sensitivity=high"
curl "http://127.0.0.1:8000/knowledge/review-queue?stale=true"
curl "http://127.0.0.1:8000/knowledge/review-queue?review_required=true"
```

Update source metadata:

```powershell
curl -X PATCH "http://127.0.0.1:8000/knowledge/sources/<source_id>" `
  -H "Content-Type: application/json" `
  -d "{\"review_required\":true,\"sensitivity\":\"high\"}"
```

Update, approve, or archive snippets:

```powershell
curl -X PATCH "http://127.0.0.1:8000/knowledge/snippets/<snippet_id>" `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Updated title\",\"review_required\":false}"

curl -X PATCH "http://127.0.0.1:8000/knowledge/snippets/<snippet_id>/approve?approved_by=knowledge-admin"
curl -X PATCH "http://127.0.0.1:8000/knowledge/snippets/<snippet_id>/archive"
```

Every review mutation writes an audit event:

- `knowledge_source_updated`
- `knowledge_snippet_updated`
- `knowledge_snippet_approved`
- `knowledge_snippet_archived`

## Phase 7D Public Website Chat Widget

Phase 7D adds a lightweight static widget for embedding Alte AI CRM chat into `alte.edu.ge` or `join.alte.edu.ge`.

Widget files:

```text
widget/alte-chat-widget.js
widget/demo.html
widget/README.md
```

Backend:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Widget demo:

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/demo.html
```

Embed example:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "http://127.0.0.1:8000",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka"
  };
</script>
<script src="./alte-chat-widget.js"></script>
```

For `join.alte.edu.ge`, set:

```js
window.AlteChatWidgetConfig = {
  apiBaseUrl: "http://127.0.0.1:8000",
  sourceDomain: "join.alte.edu.ge",
  defaultLanguage: "en"
};
```

The widget is local/static only in this phase. It does not add analytics tracking, deployment, scraping, or omnichannel integrations.

## Phase 7E Local Demo Runbook

Phase 7E hardens the local end-to-end demo flow. The default demo uses SQLite and `AI_PROVIDER=mock`, so it does not require a real Claude API key.

Step 1: local backend environment

```powershell
cd C:\tmp\alte-ai-crm\backend
copy .env.local.example .env
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Step 2: migrations and demo data

```powershell
alembic upgrade head
python -m app.scripts.setup_local_demo
```

Step 3: start backend

```powershell
uvicorn app.main:app --reload
```

Step 4: start widget demo in a second terminal

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Step 5: open demo

```text
http://127.0.0.1:5500/demo.html
```

Step 6: run HTTP smoke check

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.e2e_local_smoke
```

Useful local endpoints:

- `GET /health`
- `GET /diagnostics/local-demo`
- `GET /dashboard/overview`
- `GET /inbox`
- `GET /analytics/overview`

Common local errors:

- Missing `.env`: copy `backend/.env.local.example` to `backend/.env`.
- PostgreSQL placeholder `DATABASE_URL`: use `sqlite+aiosqlite:///./alte_ai_crm_local.db` for local demo.
- Missing tables: run `alembic upgrade head`.
- Empty knowledge results: run `python -m app.scripts.setup_local_demo`.

## Phase 8A Controlled Claude Live Test

Claude live testing is documented in:

```text
docs/CLAUDE_LIVE_TEST_GUIDE.md
```

Default local/demo mode remains:

```env
AI_PROVIDER=mock
```

Controlled Claude mode uses:

```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your-real-key
AUTH_REQUIRED=false
```

Direct AI service dry run:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.ai_direct_dry_run
```

Claude live HTTP smoke, with the backend already running:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.claude_live_smoke
```

AI diagnostics:

```text
GET /diagnostics/ai
```

The smoke script refuses placeholder keys and never prints the key. Claude still returns structured analysis only; CRM writes remain in service/business logic.

## Phase 8C Production Deployment Preparation

Deployment preparation files are available, but no Google Cloud deployment has been performed yet.

Deployment docs:

- `docs/deployment/CLOUD_RUN_DEPLOYMENT.md`
- `docs/deployment/CLOUD_SQL_POSTGRES.md`
- `docs/deployment/SECRET_MANAGER.md`
- `docs/deployment/CORS_AND_WIDGET_ORIGINS.md`
- `docs/deployment/DEPLOYMENT_CHECKLIST.md`
- `docs/deployment/DEPLOYMENT_VARIABLES.template.md`
- `docs/deployment/GOOGLE_CLOUD_PREFLIGHT.md`
- `docs/deployment/COMMAND_PLAN_GCLOUD.md`
- `docs/deployment/DEPLOYMENT_RISK_REGISTER.md`
- `docs/deployment/PRODUCTION_READINESS_DECISION.md`

Production startup readiness check:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.startup_check
```

Local Docker build check:

```powershell
cd C:\tmp\alte-ai-crm
.\scripts\docker_build_check.ps1
```

The Docker image expects production secrets from Secret Manager or equivalent runtime environment configuration. Do not include `.env`, local SQLite databases, or API keys in the image.

Deployment docs verification:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_deployment_docs
```

Phase 8D-Prep adds concrete Google Cloud command templates only. Do not run the commands until `PROJECT_ID`, region, Cloud SQL cost, secrets, CORS and rollback are reviewed.

## Phase 8D Final Preflight

Final preflight docs:

- `docs/deployment/GITHUB_BACKUP_AND_RELEASE.md`
- `docs/deployment/FINAL_PREFLIGHT_GATE.md`

Final preflight verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_final_preflight
```

Actual Cloud Run deployment remains blocked until GitHub backup/tag, Cloud SQL cost/tier, Secret Manager values, website access and privacy approval are confirmed.
