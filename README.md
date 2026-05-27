# Alte AI CRM Chatbot

AI-powered website chatbot and CRM backend foundation for Alte University / alte.edu.ge.

Current status: Phase 9T official Alte 8 PDF Knowledge Base package is prepared pending human review and DB apply approval.

Production backend is deployed with Phase 9K security/reliability fixes, and the exact Pro v2 safe widget package is prepared. Local Pro v2 chatbot/operator wiring is ready, including contact handover, operator reply polling, and draft knowledge candidate creation from operator replies. The Netlify deploy ZIP includes the Pro v2 HTML and `variants/` source needed for the hosted test page. The local operator CRM now has explicit `Local API` and `Production API` controls so the team can test Netlify chatbot messages and operator replies against the same production backend. Automated smoke checks passed for session payload, test site API, CORS, security/reliability, department routing, finance no-contact, knowledge, local operator workflow, and Phase 9T/9U/9V targeted tests. A production no-contact diagnostic confirmed handover conversations appear in Inbox and operator replies can return to the same chatbot session. The user browser workflow confirmed that chatbot messages reach the operator, the operator can reply, and the reply returns to chatbot. The official Alte 8 PDF Knowledge Base package has been extracted and normalized into 273 chunks with question bank, taxonomy, answer policy, reviewer CSV, and dry-run apply support; production DB apply has not been run. Operator replies and official PDF chunks are not automatically learned or approved; they remain review-gated where required. Public launch remains NO-GO until the official privacy URL, actual asset upload, actual site embed, real-domain smoke, and final public launch approval are recorded.

Decision state:

```text
BACKEND_DEPLOYED_OFFICIAL_ALTE_8_PDF_KB_PREPARED_PENDING_REVIEW_AND_APPLY
```

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
python -m app.scripts.verify_phase_9j_final_pre_embed_gate
python -m app.scripts.verify_phase_9l_m_n_final_launch_package
python -m app.scripts.verify_phase_9l_p_final_handoff_launch_gate
python -m app.scripts.verify_phase_9n_test_site_package
python -m app.scripts.verify_phase_9n_cors_test_origin_plan
python -m app.scripts.verify_phase_9n_cors_test_origin_execution
python -m app.scripts.verify_phase_9n_netlify_test_site_fix
python -m app.scripts.verify_phase_9n_actual_netlify_origin_cors
python -m app.scripts.verify_phase_9n_test_widget_session_payload_fix
python -m app.scripts.verify_phase_9s_frontend_event_binding_fix
python -m app.scripts.verify_phase_9t_chatbot_operator_wiring
python -m app.scripts.verify_phase_9u_operator_answer_knowledge_candidates
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

Phase 8 and Phase 9 prepared and deployed the production backend, imported approved knowledge, verified department routing/no-contact guards, prepared privacy/content approval packages, selected Alte-controlled widget asset hosting, and produced the final Safe Pro sidebar widget/embed package. The project is currently at a NO-GO final pre-site-embed gate until required approvals are complete.

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
curl -X POST http://127.0.0.1:8000/chat/handover/<conversation_id> `
  -H "Content-Type: application/json" `
  -d "{\"session_id\":\"<session_id_from_start>\"}"
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

## Phase 8E Infrastructure Decision Gate

Phase 8E prepares final infrastructure decision documents. It does not create cloud resources.

Readiness docs:

- `docs/deployment/CLOUD_SQL_TIER_DECISION.md`
- `docs/deployment/SECRET_VALUES_RUNBOOK.md`
- `docs/deployment/PRODUCTION_ENV_MAPPING.md`
- `docs/deployment/PRODUCTION_MIGRATION_AND_SEED.md`
- `docs/deployment/WEBSITE_AND_PRIVACY_APPROVAL.md`

Phase 8E verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8e_readiness
```

Actual cloud resource creation remains blocked until Cloud SQL cost/tier, Secret Manager values, website access and privacy approval are completed.

## Phase 8F-Prep Cloud SQL And Secret Execution Checklist

Phase 8F-Prep prepares the approval form and execution checklist for the next cloud-resource phase. It does not run `gcloud`.

Docs:

- `docs/deployment/CLOUD_SQL_COST_APPROVAL_FORM.md`
- `docs/deployment/SECRET_PREPARATION_CHECKLIST.md`
- `docs/deployment/PHASE_8F_EXECUTION_PLAN.md`

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8f_prep
```

Actual Cloud SQL and Secret Manager creation stays blocked until explicit approval.

## Phase 8F-Secrets-Prep Secret Values Gate

Phase 8F-Secrets-Prep prepares secret value handling without creating any Google Cloud resources.

Docs:

- `docs/deployment/SECRET_VALUES_PREPARATION_WORKSHEET.md`
- `docs/deployment/SECRET_MANAGER_APPROVAL_GATE.md`
- `docs/deployment/DATABASE_URL_CONSTRUCTION.md`
- `scripts/prepare_secret_values.ps1`

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8f_secrets_prep
```

Secret Manager creation remains blocked until explicit approval. Do not paste API keys, DB passwords, JWT secrets, or real `DATABASE_URL` values into docs or chat.

## Phase 8F Secret Values Local Prep

Phase 8F-Secret-Values-Local-Prep adds a local-only workflow for preparing DB password and JWT secret values without committing them.

Docs and scripts:

- `docs/deployment/LOCAL_SECRET_VALUES_PREP.md`
- `scripts/prepare_local_secret_values.ps1`
- `backend/app/scripts/verify_local_secret_values_prep.py`

Run the verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_local_secret_values_prep
```

The helper script may write to `.local-secrets/`, which is ignored by Git. Treat that folder as sensitive. Actual Secret Manager creation remains blocked until the explicit execution phase is approved.

## Phase 8G Cloud SQL Pilot Database

Phase 8G creates the approved low-cost Cloud SQL PostgreSQL pilot database without deploying Cloud Run.

Status:

- Cloud SQL instance: `alte-ai-crm-db`
- Edition/tier: Enterprise edition, `db-f1-micro`
- Region: `europe-west1`
- Database: `alte_ai_crm`
- App user: `alte_app`
- `alte-database-url` secret version: added without documenting the URL

Cloud Run is still not deployed, Docker images are not pushed, and production migrations/seed are still pending.

## Phase 8H Production Migration And Seed

Phase 8H ran the approved production migration and seed flow against the Cloud SQL PostgreSQL pilot database.

Status:

- Production DB connectivity: `PASS`
- Alembic version table width correction: `alembic_version.version_num VARCHAR(128)`
- Alembic migration: `MIGRATIONS_COMPLETED`
- Current revision: `006_phase_7b_knowledge_governance`
- Production schema verification: `PASS`
- Production-safe core bootstrap: `PRODUCTION_SAFE_BOOTSTRAP_COMPLETED`
- Knowledge seed: `KNOWLEDGE_SEED_COMPLETED`
- Production DB seed verification: `PRODUCTION_DB_SEED_VERIFIED`

Production-safe bootstrap created only departments, the admissions pipeline, and pipeline stages. It did not create fake customers, fake leads, fake conversations, or fake messages.

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8h_migration_seed_docs
```

Cloud Run is still not deployed, Docker images are not pushed, and the deployment decision remains `NO-GO_FOR_ACTUAL_DEPLOYMENT` until website access, privacy/data approval, and explicit Cloud Run deployment approval are complete.

## Phase 8I Cloud Run Backend Deployment

Phase 8I deployed the FastAPI backend to Google Cloud Run.

Status:

- Deployment state: `BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY`
- Cloud Run deployment: `CLOUD_RUN_DEPLOYED`
- Service: `alte-ai-crm-backend`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Docker image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.8-cloud-run`
- Cloud SQL: `CLOUD_SQL_ATTACHED`
- Secret Manager: `SECRET_MANAGER_MAPPED`
- Unauthenticated access: enabled for the public website widget API surface

Read-only production checks:

- `/health: 200`
- `/version: 200`
- `/diagnostics/ai: 200`
- `/diagnostics/local-demo: 200`
- `/dashboard/overview: 401` without bearer token, expected because `AUTH_REQUIRED=true`

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_cloud_run_deployment_docs
```

Full public launch is still pending website admin/developer access, privacy/data approval, actual website widget embed, and production widget smoke from `alte.edu.ge` / `join.alte.edu.ge`.

## Phase 8J Website Widget Production Embed Preparation

Phase 8J prepares production website embed snippets and smoke/rollback checklists for the deployed backend.

Docs and examples:

- `docs/deployment/WEBSITE_WIDGET_PRODUCTION_EMBED.md`
- `docs/deployment/PRODUCTION_WIDGET_SMOKE_CHECKLIST.md`
- `widget/production-config.alte.example.js`
- `widget/production-config.join.example.js`

Backend URL:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8j_widget_embed_docs
```

Actual website changes were not made. Website admin/developer access, privacy/data approval, actual widget embed, and production widget smoke remain pending.

## Phase 8L Widget Asset Hosting And Embed Gate

Phase 8L prepares the versioned widget asset, final embed snippets, developer handoff, and staging/test page for production backend testing.

Files:

- `widget/alte-chat-widget.v0.8.js`
- `widget/production-embed-test.html`
- `docs/deployment/WIDGET_ASSET_HOSTING_DECISION.md`
- `docs/deployment/WIDGET_EMBED_SNIPPETS_FINAL.md`
- `docs/deployment/WEBSITE_DEVELOPER_HANDOFF.md`

Recommended asset hosting:

```text
Option A - Website/CMS static asset hosting
```

Current embed status:

```text
ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL
```

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8l_widget_asset_embed
```

No real website changes are made in this phase.

## Phase 8L Sandbox Standalone Production Widget Demo

Phase 8L-Sandbox adds a standalone static demo page that uses the production Cloud Run backend without modifying the real Alte websites.

Files:

- `widget/standalone-production-demo.html`
- `widget/STANDALONE_PRODUCTION_DEMO.md`
- `docs/deployment/WIDGET_TRANSFER_TO_ALTE_SITE.md`
- `docs/deployment/STANDALONE_WIDGET_SMOKE_CHECKLIST.md`

Run locally:

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/standalone-production-demo.html
```

Decision state:

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED
```

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8l_standalone_widget
```

## Phase 8M Standalone Widget CORS Smoke Decision

Phase 8M records the standalone widget smoke result without changing production CORS or redeploying Cloud Run.

Results:

- Local static demo page: `200`
- Widget JS asset: `200`
- Production `/health`: `200`
- Production `/version`: `200`
- Production `/diagnostics/ai`: `200`, Claude enabled, no secrets exposed
- Backend API safe chat smoke:
  - `alte.edu.ge` / `ka`: PASS
  - `join.alte.edu.ge` / `en`: PASS
- Production CORS:
  - `https://alte.edu.ge`: PASS
  - `https://join.alte.edu.ge`: PASS
- Localhost browser CORS:
  - `http://127.0.0.1:5500`: blocked as expected

Decision:

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE
```

Localhost is not approved for production CORS by default:

```text
LOCALHOST_CORS_NOT_APPROVED_FOR_PRODUCTION
```

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8m_cors_decision
```

## Phase 8N Website Privacy Approval Gate

Phase 8N prepares the final gate for the actual Alte website widget embed. It does not modify `alte.edu.ge` or `join.alte.edu.ge`.

Files:

- `docs/deployment/WEBSITE_EMBED_APPROVAL_GATE.md`
- `docs/deployment/PRIVACY_CONSENT_APPROVAL.md`
- `docs/deployment/FINAL_WIDGET_EMBED_GO_NO_GO.md`
- `docs/deployment/WIDGET_FINAL_ASSET_URL_DECISION.md`

Decision:

```text
BACKEND_DEPLOYED_WIDGET_READY_PENDING_WEBSITE_PRIVACY_APPROVAL
```

Actual site embed remains blocked until website access, privacy approval, final asset URL, and real-domain smoke ownership are approved.

Verifier:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.verify_phase_8n_website_privacy_gate
```

## Phase 8O Full Standalone Chatbot Test Site

Phase 8O prepares a complete standalone chatbot test page and curated test knowledge package for independent testing before the real Alte site embed.

Files:

- `widget/full-standalone-chatbot-test.html`
- `backend/app/knowledge_seed/alte_required_test_knowledge_v1.json`
- `backend/app/scripts/seed_required_test_knowledge.py`
- `backend/app/scripts/standalone_chatbot_api_smoke.py`
- `docs/deployment/STANDALONE_TEST_SITE_RUNBOOK.md`
- `docs/deployment/STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md`
- `docs/deployment/FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md`

Run the static page:

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/full-standalone-chatbot-test.html
```

Run backend/API smoke without browser CORS:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.standalone_chatbot_api_smoke
```

Decision:

```text
BACKEND_DEPLOYED_FULL_STANDALONE_CHATBOT_READY_PENDING_REAL_SITE_EMBED
```

Production seed was not run in Phase 8O. Review the knowledge file before seeding any production database.

Verifier:

```powershell
python -m app.scripts.verify_phase_8o_standalone_chatbot
```

## Phase 8P Standalone API Smoke

Phase 8P ran the safe standalone API smoke against the production backend without the contact-flow flag.

Result:

- `/health`: PASS
- `/version`: PASS
- `/diagnostics/ai`: PASS
- KA greeting: PASS
- KA finance question: PASS, no exact invented price
- EN medicine/international question: PASS
- Contact-flow test: not run
- Contact details submitted: no
- Intentional lead/task creation: no
- Observed side effect: the medicine/international admission message triggered existing backend business rules to create a lead/task.

Production test knowledge seed remains pending approval:

```text
PENDING_APPROVAL
```

Decision:

```text
BACKEND_DEPLOYED_STANDALONE_API_SMOKE_PASSED_PENDING_TEST_KNOWLEDGE_APPROVAL
```

Verifier:

```powershell
python -m app.scripts.verify_phase_8p_api_smoke_docs
```

The page uses the production backend. Do not enter real student data unless production test records are approved.

## Phase 8P-Fix No-Contact Lead Guard

Phase 8P revealed an unintended production side effect: a medicine/international admissions message without phone, email, or contact-flow approval created a lead/task.

Fix applied locally:

- Admission, consultation, international, and medicine admission intent now requires phone or email before lead/task creation.
- No contact -> ask for name and phone/email, save conversation and AI analysis only.
- Contact present -> create/update customer, lead, and follow-up task.
- Human request chat behavior remains contact-gated for task creation; the explicit handover endpoint remains the exception path.

Decision:

```text
BACKEND_DEPLOYED_STANDALONE_API_SMOKE_NEEDS_REDEPLOY_FOR_NO_CONTACT_GUARD
```

Cloud Run redeploy was required before production received this fix.

## Phase 8P-Redeploy No-Contact Guard Verification

The no-contact lead guard was deployed to Cloud Run with image tag:

```text
v0.8-no-contact-guard
```

Production checks:

- `/health`: 200
- `/version`: 200
- `/diagnostics/ai`: 200, Claude enabled, no secrets exposed
- Safe standalone API smoke: PASS
- Contact-flow test: not run
- Contact details submitted: no
- Medicine/international no-contact result: no lead, no task, `should_create_lead=false`, `phone_or_email` requested

Decision:

```text
BACKEND_DEPLOYED_NO_CONTACT_GUARD_VERIFIED_PENDING_TEST_KNOWLEDGE_APPROVAL
```

## Phase 8Q Production Test Knowledge Seed

Phase 8Q seeded the curated required test knowledge into production Cloud SQL after explicit approval.

Result:

- First seed run: `sources_created=12`, `snippets_created=13`, `skipped_existing=0`, `review_required_count=11`
- Second seed run: `sources_created=0`, `snippets_created=0`, `skipped_existing=13`
- Idempotency: PASS
- Required test knowledge verification: PASS
- Safe standalone API smoke after seed: PASS
- Contact-flow test: not run
- Intentional lead/task creation: no
- Official content review: still required before public launch

Verifier:

```powershell
python -m app.scripts.verify_phase_8q_test_knowledge_seed_docs
```

Decision:

```text
BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_SAFE_SMOKE_PASSED_PENDING_OFFICIAL_REVIEW_AND_SITE_EMBED
```

## Phase 8R Official Content Review Gate

Phase 8R adds the content approval gate required before public chatbot launch.

Created:

- `docs/deployment/OFFICIAL_CONTENT_REVIEW_REPORT.md`
- `docs/deployment/OFFICIAL_CONTENT_REVIEW_CHECKLIST.md`
- `docs/deployment/CHATBOT_PUBLIC_ANSWER_POLICY.md`
- `docs/deployment/KNOWLEDGE_REVIEW_QUEUE_TEMPLATE.csv`
- `python -m app.scripts.export_knowledge_review_queue`

Current review status:

```text
OFFICIAL_CONTENT_REVIEW_STATUS=PENDING
```

Decision:

```text
BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_PENDING_OFFICIAL_CONTENT_REVIEW
```

Public launch remains blocked until official content review, privacy approval, website access, final widget asset hosting, real-site embed, and real-domain browser smoke are complete.

## Phase 8S Official Content Review Apply

Phase 8S inspected the exported review queue and ran the content review apply workflow in dry-run mode.

Result:

- Explicit reviewer decisions found: 0
- Reviewer `decision` column present: no
- `recommended_action` values treated as reviewer decisions: no
- Dry-run rows: 26
- Apply run: no
- Applied count: 0
- Sensitive fully approved count: 0
- Sensitive pending review count: 7
- Public launch: still blocked

Decision:

```text
BACKEND_DEPLOYED_CONTENT_REVIEW_DRY_RUN_PENDING_REVIEWER_DECISIONS
```

## Phase 8T Reviewer Decision CSV

Phase 8T prepared a human-reviewable CSV so official content decisions can be entered explicitly.

Result:

- Source CSV: `backend/reports/knowledge_review_queue.csv`
- Reviewer CSV: `backend/reports/knowledge_review_queue_for_review.csv`
- Rows prepared: 26
- Reviewer-owned columns added: `decision`, `reviewer`, `review_date`, `reviewer_notes`
- Decision column prefilled: no
- `recommended_action` copied into `decision`: no
- Apply run: no
- Official content review: still pending human review

Decision:

```text
BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW
```

## Alte Study Docs Knowledge Import

The local Alte study/planning files from `C:\tmp\alte-docs-extracted` were copied into `docs/knowledge_evidence/alte_study_docs/`, normalized, and imported into the production Knowledge Base for controlled chatbot testing.

Result:

- Seed file: `backend/app/knowledge_seed/alte_study_docs/alte_study_docs_seed_v1.json`
- Records imported: 11
- Sources created: 11
- Snippets created: 11
- High-sensitivity records: 5
- Review-required records: 8
- Sensitive topics remain review-required: finance, deadlines, required documents, international admissions, Medicine/MD
- Public launch remains blocked pending official review, privacy approval, website embed, and real-domain smoke

Decision:

```text
BACKEND_DEPLOYED_STUDY_DOCS_KNOWLEDGE_IMPORTED_PENDING_OFFICIAL_REVIEW
```

## Phase 8W Production Knowledge Smoke After Study Docs

Production endpoint checks passed after the study-docs Knowledge Base import:

- `/health`: `200`
- `/version`: `200`
- `/diagnostics/ai`: `200`, Claude enabled, no secrets exposed

Original Phase 8W safe no-contact knowledge smoke status:

- Original status: `FAILED_NEEDS_REVIEW`, resolved by Phase 8Y-Redeploy
- Assertions: `22 passed`, `1 failed`
- Contact-flow test run: no
- Contact details sent: no
- Intentional lead/task/customer creation: no
- Sensitive answers stayed conservative for exact tuition/deadline checks
- Failure: one tuition question returned `should_create_lead=true` without contact details, although `created_lead_id=null` and `created_task_id=null`

Original decision, now superseded by Phase 8Y-Redeploy:

```text
BACKEND_DEPLOYED_STUDY_DOCS_KB_SMOKE_FAILED_NEEDS_REVIEW
```

Current resolved decision:

```text
BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

Public launch remains blocked.

## Full Local Alte KB Import

All useful local Alte KB/study/prototype files were copied into `docs/knowledge_evidence/alte_full_local_kb/`, normalized, and imported into the application Knowledge Base. Duplicate KB copies were not imported twice, and the desktop Word file containing an API key/secret was excluded.

Result:

- Source pages: 123
- Source knowledge chunks: 647
- Normalized records: 647
- High-sensitivity records: 379
- Review-required records: 379
- Knowledge Base import: 240 sources, 645 snippets
- Duplicate snippets skipped: 2
- Reviewer CSV: `backend/reports/full_alte_local_kb_reviewer_decision_queue.csv`
- Sensitive official facts remain review-required and are not public-approved automatically.

Decision:

```text
BACKEND_DEPLOYED_FULL_LOCAL_KB_IMPORTED_PENDING_HUMAN_REVIEW
```

Public launch remains blocked pending reviewer decisions, privacy approval, final widget asset hosting, real site embed, and real-domain browser smoke.

## Phase 8Y Finance No-Contact Guard

The Phase 8W smoke found a tuition/finance no-contact lead bug: a tuition question without phone/email returned `should_create_lead=true` even though no lead/task IDs were created.

The service-layer guard is deployed and verified in production:

- finance/tuition/scholarship/deadline questions without phone/email force `should_create_lead=false`
- no customer, lead, or task is created for no-contact finance information requests
- phone/email is not forced for pure information finance questions
- sensitive finance content remains `review_required=true`
- deployed to Cloud Run as `v0.8-finance-no-contact-guard`
- finance no-contact smoke passed `24/24`; broader knowledge smoke passed `25/25`

Decision:

```text
BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

## Phase 8Z Safe Uploaded Widget UI

The uploaded `alte_university_ai_chatbot.html` UI was copied as evidence and converted into a safe backend-connected standalone page.

- Evidence: `docs/knowledge_evidence/uploaded_widget_ui/alte_university_ai_chatbot.html`
- Safe UI: `widget/alte-university-ai-chatbot-safe.html`
- Removed unsafe direct browser Anthropic call.
- Removed frontend prompt as production source of truth.
- Uses production FastAPI backend:
  - `POST /chat/session/start`
  - `POST /chat/message`
- No API keys or secrets in frontend.
- Public launch remains blocked.

Decision:

```text
BACKEND_DEPLOYED_FULL_LOCAL_KB_IMPORTED_SAFE_WIDGET_UI_READY_PENDING_REVIEW_AND_SITE_EMBED
```

## Phase 8Y-Redeploy Finance No-Contact Guard

The Phase 8Y finance/tuition no-contact guard has been deployed to Cloud Run.

- Cloud Run service: `alte-ai-crm-backend`
- Image tag: `v0.8-finance-no-contact-guard`
- Previous revision: `alte-ai-crm-backend-00003-x84`
- New revision: `alte-ai-crm-backend-00004-gsn`
- `/health`: 200
- `/version`: 200
- `/diagnostics/ai`: 200, Claude enabled, no secrets exposed
- Finance no-contact smoke: `24 passed`, `0 failed`
- Broader knowledge smoke: `25 passed`, `0 failed`
- Contact-flow test: not run
- Contact details sent: no
- Intentional production lead/task/customer creation: no

Verified production behavior:

- finance/tuition/scholarship/deadline no-contact questions return `should_create_lead=false`
- `created_customer_id=null`, `created_lead_id=null`, and `created_task_id=null`
- sensitive tuition/deadline answers remain conservative and review-governed

Decision state:

```text
BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

Public launch remains blocked until human reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, and real-domain browser smoke are completed.

## Phase 9A Human Reviewer Decisions Package

The final human reviewer package has been prepared from the full imported Alte KB.

- Full reviewer CSV: `docs/reviewer_package/alte_kb_human_review_decisions.csv`
- Compact management CSV: `docs/reviewer_package/alte_kb_human_review_compact.csv`
- Georgian instructions: `docs/reviewer_package/REVIEWER_INSTRUCTIONS_GEO.md`
- Georgian summary: `docs/reviewer_package/REVIEWER_SUMMARY_GEO.md`
- Source rows: 647
- High-sensitivity rows: 379
- Review-required rows: 379
- Human decisions filled: 0
- Validation status: `PENDING_HUMAN_DECISIONS`

The backend is deployed and smoke verified, and the safe widget is ready. Public launch remains blocked until reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, and real-domain browser smoke are completed.

Decision state:

```text
BACKEND_DEPLOYED_REVIEWER_PACKAGE_READY_PENDING_HUMAN_DECISIONS
```

## Phase 9B Widget Design Concepts

The uploaded Alte widget design concept package has been imported as UI evidence and converted into a safe backend-connected production candidate.

- Evidence folder: `docs/knowledge_evidence/uploaded_widget_design_concepts/`
- Concept review: `docs/deployment/WIDGET_DESIGN_CONCEPTS_REVIEW.md`
- Safe Pro candidate: `widget/alte-university-ai-chatbot-safe-pro.html`
- Standalone preview: `widget/standalone-safe-pro-demo.html`
- Embed snippet draft: `docs/deployment/WIDGET_SAFE_PRO_EMBED_SNIPPET.md`
- Recommended design direction: compact PIP-style widget with selected Pro-style polish.
- Unsafe direct browser Anthropic calls remain forbidden.
- The FastAPI backend remains the AI, Knowledge Base, and CRM business-rule source of truth.
- Public launch remains blocked.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_CANDIDATE_READY_PENDING_REVIEW_AND_SITE_EMBED
```

## Phase 9C Final Pre-Embed Gate

The final approval gate before actual website embedding has been prepared.

- Gate: `docs/deployment/FINAL_PRE_EMBED_APPROVAL_GATE.md`
- Asset hosting decision: `docs/deployment/WIDGET_ASSET_HOSTING_DECISION.md`
- Readiness checklist: `docs/deployment/FINAL_EMBED_READINESS_CHECKLIST.md`
- Real-domain smoke plan: `docs/deployment/REAL_DOMAIN_WIDGET_SMOKE_PLAN.md`
- Rollback plan: `docs/deployment/WIDGET_EMBED_ROLLBACK_PLAN.md`
- Privacy/data approval record: `docs/deployment/PRIVACY_DATA_APPROVAL_RECORD.md`
- Selected widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Final asset URL: pending
- Privacy/data approval: pending
- Official content approval: pending
- Actual site embed: not done
- Real-domain browser smoke: pending
- Public launch: not complete

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_PRE_EMBED_GATE_READY_PENDING_APPROVALS
```

## Phase 9D Department-Aware Handover Routing

Department-aware routing has been added in backend code and Safe Pro widget context.

- Routing service: `backend/app/services/department_routing_service.py`
- Policy: `docs/deployment/DEPARTMENT_HANDOVER_ROUTING_POLICY.md`
- Result: `docs/deployment/PHASE_9D_DEPARTMENT_HANDOVER_RESULT.md`
- Safe production smoke script: `backend/app/scripts/production_department_handover_smoke.py`
- Widget context fields: `selected_department`, `selected_topic`, `page_url`, `widget_variant`
- Backend response fields: `route_department`, `department_key`, `routing_reason`

Production redeploy is required before Cloud Run serves the Phase 9D behavior.

Decision state:

```text
BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY
```

## Phase 9D-UI Safe Pro Sidebar Layout

The Safe Pro widget has been switched from compact PIP to the sidebar Pro layout requested for the final chat experience.

- Main widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Archived compact alternate: `widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html`
- Demo: `widget/standalone-safe-pro-demo.html`
- Sidebar departments drive backend context through `selected_department` and `selected_topic`.
- Frontend remains safe: no direct Anthropic call, no API key, no frontend CRM actions.
- Actual embed and public launch remain pending.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_SIDEBAR_WIDGET_READY_PENDING_REDEPLOY_AND_SITE_EMBED
```

## Phase 9D-UI-Final Exact Pro Sidebar Widget

The Safe Pro widget now implements the exact functional Pro Sidebar layout selected from the uploaded design ZIP/screenshots.

- Final widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Archived compact/PIP alternate: `widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html`
- Demo: `widget/standalone-safe-pro-demo.html`
- UI: left department sidebar, right chat area, header, KA/EN switch, reset control, trust/source bar, message bubbles, source cards, handover/operator card, contact request UI, quick chips, and composer.
- Functionality: sidebar clicks set `selected_department` and `selected_topic`; quick chips send context to backend; Human Operator sends a human request with active department context.
- Safety: browser calls only FastAPI backend endpoints; no direct Anthropic call; no frontend API key; no frontend CRM record creation; no frontend hardcoded tuition/deadline facts.
- Public launch remains blocked pending backend redeploy for department routing, reviewer decisions, official content approval, privacy/data approval, final asset URL, actual site embed, and real-domain browser smoke.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_PRO_SIDEBAR_WIDGET_FUNCTIONAL_READY_PENDING_REDEPLOY_AND_SITE_EMBED

## Phase 9D-Redeploy Department Routing Verification

Phase 9D backend code was deployed to Cloud Run as image `v0.9-department-routing-sidebar` on service `alte-ai-crm-backend`.

Production verification found:

- Endpoint checks passed: `/health`, `/version`, `/diagnostics/ai`
- Finance no-contact smoke passed: `24/24`
- Broader knowledge smoke passed: `25/25`
- Department routing smoke partially failed: `26/28`
- No contact details were sent
- No contact-flow test was run
- No intentional production customer/lead/task creation occurred

Open issue:

- Ambiguous sidebar messages with `selected_department=finance` or `selected_department=medicine` were routed to `Admissions` instead of preserving the selected sidebar department.

Public launch and actual site embed remain blocked until this routing bug is fixed, redeployed, and the department routing smoke passes.

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```

## Desktop Alte Study KB v3 Import

Additional study material was found at `C:\Users\Acer\Desktop\ალტე\სწავლა\alte_kb_complete_v3.py` and imported into the Knowledge Base.

Result:

- Normalized records: `27`
- Production KB sources created: `26`
- Production KB sources updated: `1`
- Production KB chunks created: `27`
- High-sensitivity records: `18`
- Review-required records: `18`

Added coverage includes programs, admissions, required documents, tuition/finance, deadlines, international admissions, Medicine/MD, Dentistry, visa/relocation, student services, and contact/routing guidance.

Sensitive exact facts remain `review_required=true`; this does not approve public launch.

Decision state:

```text
BACKEND_KB_UPDATED_DESKTOP_STUDY_V3_IMPORTED_PENDING_REVIEW_AND_ROUTING_FIX
```

## Phase 9E Sidebar Ambiguous Routing Fix

The Phase 9D-Redeploy production smoke found that ambiguous sidebar messages could route to `Admissions` instead of the selected sidebar department.

Fixed locally:

- `selected_department=finance` + `მაინტერესებს დეტალები` now routes to `finance`
- `selected_department=medicine` + `დეტალები მაინტერესებს` now routes to `medicine`
- ambiguous `international`, `it_support`, and `student_services` sidebar contexts are preserved
- strong explicit keywords still override sidebar context, for example portal/login -> IT Support and scholarship -> Finance
- no-contact guard remains unchanged

Production redeploy is required before this behavior changes on Cloud Run.

Decision state:

```text
BACKEND_CODE_FIXED_SIDEBAR_AMBIGUOUS_ROUTING_PENDING_REDEPLOY
```
```

## Phase 9E-Redeploy Sidebar Ambiguous Routing Verification

The Phase 9E sidebar ambiguous routing fix has been deployed to Cloud Run.

- Image tag: `v0.9-sidebar-ambiguous-routing-fix`
- Previous revision: `alte-ai-crm-backend-00005-px7`
- New revision: `alte-ai-crm-backend-00006-vs5`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Endpoint checks: `/health`, `/version`, and `/diagnostics/ai` returned 200.
- Department routing smoke: 28/28 passed.
- Previously failing Finance ambiguous sidebar case: PASS.
- Previously failing Medicine ambiguous sidebar case: PASS.
- Finance no-contact smoke: 24/24 passed.
- Broader knowledge smoke final run: 25/25 passed.
- No contact details sent.
- Contact-flow test not run.
- No intentional lead/task/customer creation.

Public launch remains blocked. Human reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, and real-domain browser smoke are still pending.

Decision state:

```text
BACKEND_DEPLOYED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

## Phase 9F Conservative Content Approval Decisions

Prepared a conservative official-content decision draft for the full imported Alte KB.

- Source reviewer file: `docs/reviewer_package/alte_kb_human_review_decisions.csv`
- Conservative decision file: `docs/reviewer_package/alte_kb_conservative_decisions_for_approval.csv`
- Total rows: 647
- `APPROVE`: 67
- `HANDOVER_ONLY`: 10
- `NEEDS_OFFICIAL_SOURCE`: 570
- High sensitivity rows: 379
- Sensitive blocked count: 580
- Public launch allowed by conservative draft: 67
- `apply_official_content_review --apply` run: NO
- Production DB modified: NO

This is not official human approval. Sensitive official facts remain blocked or require official source review. Public launch remains blocked.

Decision state:

```text
BACKEND_DEPLOYED_CONTENT_DECISIONS_PREPARED_PENDING_HUMAN_APPROVAL
```

## Phase 9G-H Privacy And Embed Preparation

Prepared the privacy/data approval and website embed package.

- Privacy package: `docs/privacy/CHATBOT_PRIVACY_DATA_APPROVAL_PACKAGE.md`
- Consent text draft: `docs/privacy/CHATBOT_CONSENT_TEXT_GEO_EN.md`
- Data retention/rights draft: `docs/privacy/CHATBOT_DATA_RETENTION_AND_RIGHTS_DRAFT.md`
- Final asset URL decision: `docs/deployment/FINAL_WIDGET_ASSET_URL_DECISION.md`
- Embed package: `docs/embed_package/`
- Actual site embed runbook: `docs/deployment/ACTUAL_SITE_EMBED_RUNBOOK.md`
- Real-domain smoke guide: `docs/deployment/REAL_DOMAIN_BROWSER_SMOKE_EXECUTION_GUIDE.md`

Status:

- Privacy approval: pending
- Final widget asset URL: pending
- Actual site embed: not executed
- Real-domain browser smoke: not executed
- Public launch: not complete

Decision state:

```text
BACKEND_DEPLOYED_PRIVACY_AND_EMBED_PACKAGE_READY_PENDING_FINAL_APPROVALS
```

## Phase 9I Asset Hosting Decision

Option A was selected: Alte-controlled hosting.

- Placeholder final asset URL: `https://alte.edu.ge/assets/alte-ai-chat-widget.js`
- Prepared asset files:
  - `dist/widget/alte-ai-chat-widget.html`
  - `dist/widget/alte-ai-chat-widget.js`
- Website developer handoff: `docs/embed_package/WEBSITE_DEVELOPER_HANDOFF_GEO.md`
- Embed snippets updated to use the Alte-controlled placeholder URL.
- Actual upload/embed: not executed.
- Real-domain smoke: not executed.
- Public launch: not complete.

Decision state:

```text
BACKEND_DEPLOYED_ASSET_HOSTING_SELECTED_ALTE_CONTROLLED_PENDING_UPLOAD_AND_SITE_EMBED
```

## Phase 9J Final Pre-Site-Embed Approval Gate

Created the final GO/NO-GO gate before actual website embed.

- Final gate: `docs/deployment/PHASE_9J_FINAL_PRE_SITE_EMBED_APPROVAL_GATE.md`
- Approval record template: `docs/deployment/SITE_EMBED_FINAL_APPROVAL_RECORD.md`
- GO/NO-GO checklist: `docs/deployment/SITE_EMBED_GO_NO_GO_CHECKLIST.md`
- Status: `NO_GO_PENDING_FINAL_APPROVALS`

Actual site embed, asset upload, real-domain smoke, and public launch remain blocked until final approvals are explicitly recorded.

Decision state:

```text
BACKEND_DEPLOYED_FINAL_PRE_EMBED_GATE_READY_NO_GO_PENDING_APPROVALS
```

## Phase 9K Pre-Launch Security And Reliability Fixes

Phase 9K fixes the audit findings locally in code, tests, docs, and verifiers only.

- AI provider/API/network failures now return a safe structured fallback instead of chat 500.
- Public `/chat/handover/{conversation_id}` requires a valid conversation session and is guarded against duplicate task creation and no-contact task spam.
- RBAC protected endpoints deny by default when permission mapping is missing.
- Production settings fail validation if `ENVIRONMENT=production` and `AUTH_REQUIRED=false`.
- Uploaded widget UI evidence is marked archive/reference only.
- Widget privacy placeholder `#privacy-policy-pending` remains a launch blocker until the official URL is approved.

Redeploy required: YES.
Public launch: `NOT_COMPLETE`.
Actual site embed: blocked.

Decision state:

```text
BACKEND_DEPLOYED_SECURITY_RELIABILITY_VERIFIED_PENDING_FINAL_APPROVALS_AND_SITE_EMBED
```

## Phase 9K-Redeploy Security Reliability Verification

Phase 9K fixes were deployed to Cloud Run.

- Image tag: `v0.9-security-reliability-fixes`
- Cloud Run revision: `alte-ai-crm-backend-00007-xmp`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- `/health`, `/version`, `/diagnostics/ai`: `200`
- `/dashboard/overview` without auth: `401`
- Security/reliability smoke: `16/16` passed
- Department routing smoke: `28/28` passed
- Finance no-contact smoke: `24/24` passed
- Broader knowledge smoke: `25/25` passed
- Contact-flow test was not run.
- No contact details were sent.
- No intentional production lead/task/customer creation was performed.

Public launch remains `NOT_COMPLETE`; actual site embed remains blocked pending final approvals.

## Phase 9Q Pro v2 Safe Widget

- Safe Pro v2 widget adaptation is prepared locally.
- Final widget: `widget/alte-ai-chatbot-pro-v2-safe.html`
- Deploy JS: `dist/widget/alte-ai-chat-widget.js`
- Netlify ZIP: `dist/netlify_test_site_deploy.zip`
- Browser smoke is pending Netlify redeploy and manual retest.
- Public launch remains NO-GO.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_SAFE_WIDGET_READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST
```

## Phase 9Q-9R Pro v2 Rebuild

- Uploaded Pro v2 standalone is now recorded as visual and functional source-of-truth.
- Safe widget was rebuilt toward the large Pro v2 modal layout.
- Functional inventory, gap matrix, implementation plan, and backend approval gaps are documented.
- Netlify ZIP was rebuilt and requires redeploy.
- Browser smoke remains pending; real Alte site remains untouched; public launch remains NO-GO.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_REBUILT_AND_FUNCTION_GAPS_AUDITED_PENDING_NETLIFY_REDEPLOY
```

## Phase 9S Exact ZIP Source Pro v2 Port

- Uploaded ZIP source `სრული ვერსია.zip` was extracted into evidence.
- Exact Pro v2 source files under `deploy/variants/` are now the implementation reference.
- Safe widget was ported to the ZIP `.cw-win` floating/expanded modal model.
- Unsafe Vercel/Claude browser logic was removed and replaced by FastAPI backend calls only.
- Netlify package was rebuilt and requires redeploy.
- Hosted browser smoke remains pending; real Alte site remains untouched; public launch remains NO-GO.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_ZIP_SOURCE_PRO_V2_WIDGET_READY_PENDING_NETLIFY_REDEPLOY
```
