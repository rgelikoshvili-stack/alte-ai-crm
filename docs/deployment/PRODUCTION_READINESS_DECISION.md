# Production Readiness Decision

Current decision: `BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED`

Reason: GitHub backup/tag, deployment docs, Claude live validation, Docker/Cloud Run docs, project/region/CORS and billing are recorded. Cloud SQL pilot instance/database/user are created, Secret Manager containers are created, required secret versions including DATABASE_URL are added, production migrations/seed have completed, the backend is deployed to Cloud Run, a standalone production widget demo is prepared, backend/API smoke passed, production-domain CORS preflight passed, the website/privacy approval gate is prepared, the full standalone chatbot test site plus required test knowledge package are prepared, the no-contact lead/task guard has been deployed and verified, production test knowledge has been seeded with idempotency verified, the reviewer decision CSV is prepared, and local Alte study/planning documents have been imported into the Knowledge Base for controlled chatbot testing. Phase 8Y-Redeploy resolved the Phase 8W finance/tuition no-contact review item by deploying image `v0.8-finance-no-contact-guard`; finance no-contact smoke passed `24/24` and broader knowledge smoke passed `25/25`. No reviewer decisions are filled yet, so no content was automatically approved for full public launch. Full production launch remains blocked until reviewer decisions, official content review, website access, privacy approval, final widget asset URL, actual widget embed, real-domain browser widget smoke, and explicit launch approval are completed.

Previous backend deployment state `BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY` remains true. Historical deployment gate `NO-GO_FOR_ACTUAL_DEPLOYMENT` is superseded for backend deployment only. Full public launch remains blocked.
Previous smoke state `BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE` remains true.
Previous website/privacy gate state `BACKEND_DEPLOYED_WIDGET_READY_PENDING_WEBSITE_PRIVACY_APPROVAL` remains true.
Previous full standalone site state `BACKEND_DEPLOYED_FULL_STANDALONE_CHATBOT_READY_PENDING_REAL_SITE_EMBED` remains true.
Previous safe smoke state `BACKEND_DEPLOYED_STANDALONE_API_SMOKE_PASSED_PENDING_TEST_KNOWLEDGE_APPROVAL` remains true for the endpoint checks, with the no-contact lead/task side effect now tracked separately.
Previous no-contact guard state `BACKEND_DEPLOYED_STANDALONE_API_SMOKE_NEEDS_REDEPLOY_FOR_NO_CONTACT_GUARD` is resolved by Phase 8P-Redeploy.
Previous no-contact verification state `BACKEND_DEPLOYED_NO_CONTACT_GUARD_VERIFIED_PENDING_TEST_KNOWLEDGE_APPROVAL` is resolved by Phase 8Q.
Previous seeded state `BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_SAFE_SMOKE_PASSED_PENDING_OFFICIAL_REVIEW_AND_SITE_EMBED` remains true and now advances to the official content review gate.
Previous official content gate state `BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_PENDING_OFFICIAL_CONTENT_REVIEW` remains true and now advances to reviewer-decision-CSV-ready-pending-human-review.
Previous reviewer CSV state `BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW` remains true; study docs are now also imported into Knowledge Base pending official review.
Previous study-docs import state `BACKEND_DEPLOYED_STUDY_DOCS_KNOWLEDGE_IMPORTED_PENDING_OFFICIAL_REVIEW` remains true; Phase 8W smoke now requires review before public launch.

## Go Only If

- [x] GitHub remote exists. Current remote: `https://github.com/rgelikoshvili-stack/alte-ai-crm`.
- [x] Release tag exists. `v0.8-deployment-ready` was pushed.
- [x] Tests pass. Latest Phase 8D-GitHub check: `110 passed` with `AI_PROVIDER=mock`.
- [x] Docker build passes. Cloud Build image build completed for `v0.8-cloud-run`.
- [ ] `startup_check` passes with production-like env. Local/dev check passed; production-like Secret Manager values are not configured yet.
- [x] Google Cloud project selected. `PROJECT_ID=project-1e145fd0-c30e-4aac-a34`.
- [x] Billing understood. User confirmed billing is enabled.
- [x] Cloud SQL cost/tier direction accepted for pilot. Recommended option: Low-cost pilot production tier. Exact final price still must be reviewed during actual resource creation.
- [x] Anthropic key created and stored in Secret Manager.
- [x] CORS origins confirmed. `https://alte.edu.ge,https://join.alte.edu.ge`.
- [ ] Alte website admin/developer access confirmed.
- [x] Rollback plan documented. See `DEPLOYMENT_CHECKLIST.md` and `DEPLOYMENT_RISK_REGISTER.md`.
- [ ] Data privacy owner approves.

## Current Recommended Values

- `PROJECT_ID=project-1e145fd0-c30e-4aac-a34`
- `REGION=europe-west1`
- `SERVICE_NAME=alte-ai-crm-backend`
- `ARTIFACT_REPOSITORY=alte-ai-crm`
- `CLOUD_SQL_INSTANCE=alte-ai-crm-db`
- `DB_NAME=alte_ai_crm`
- `DB_USER=alte_app`
- Secret names:
  - `alte-db-password`
  - `alte-database-url`
  - `alte-jwt-secret`
  - `alte-anthropic-api-key`
- `CORS_ORIGINS=https://alte.edu.ge,https://join.alte.edu.ge`
- `GITHUB_REMOTE_URL=https://github.com/rgelikoshvili-stack/alte-ai-crm`

## Required Before Phase 8D Actual Deployment

- Confirm Cloud SQL cost/tier.
- Confirm Secret Manager values are created without exposing them.
- Confirm Alte website admin/developer access.
- Confirm data privacy approval.

## Completed Deployment Readiness Items

- GitHub remote configured.
- GitHub push completed.
- Release tag created: `v0.8-deployment-ready`.
- Deployment docs prepared.
- Claude live validation completed.
- Docker/Cloud Run docs prepared.
- Cloud SQL tier/cost decision document prepared.
- Cloud SQL cost approval form prepared; status `APPROVED_FOR_PILOT`.
- Cloud SQL pilot tier approved.
- Recommended Cloud SQL option: Low-cost pilot production tier.
- Secret Manager values runbook prepared.
- Secret preparation checklist prepared.
- Secret values preparation worksheet prepared.
- Secret Manager approval gate prepared; status `APPROVED_FOR_NEXT_EXECUTION`.
- Secret Manager creation approval recorded for the next execution phase.
- Secret Manager execution approved and container creation completed.
- Secret containers created/existing:
  - `alte-db-password`: `CONTAINER_CREATED / VERSION_PENDING`
  - `alte-jwt-secret`: `CONTAINER_CREATED / VERSION_PENDING`
  - `alte-anthropic-api-key`: `CONTAINER_CREATED / VERSION_PENDING`
  - `alte-database-url`: `CONTAINER_CREATED / VERSION_PENDING_UNTIL_CLOUD_SQL_EXISTS`
- Secret Manager versions added:
  - `alte-db-password`: `CONTAINER_CREATED / VERSION_ADDED`
  - `alte-jwt-secret`: `CONTAINER_CREATED / VERSION_ADDED`
  - `alte-anthropic-api-key`: `CONTAINER_CREATED / VERSION_ADDED`
  - `alte-database-url`: `CONTAINER_CREATED / VERSION_ADDED`
- Corrected Cloud SQL approach documented: Enterprise edition, low-cost pilot tier, no Enterprise Plus/performance-optimized tier.
- Cloud SQL instance status: `CLOUD_SQL_INSTANCE_CREATED`
- Cloud SQL database status: `DATABASE_CREATED`
- Cloud SQL app user status: `DB_USER_CREATED`
- `DATABASE_URL` construction guide prepared.
- Local secret preparation helper script prepared.
- Production env mapping reviewed.
- Production migration/seed runbook prepared.
- Alembic version table width correction applied: `alembic_version.version_num VARCHAR(128)`.
- Production DB connectivity checked: `PASS`.
- Production migrations completed against Cloud SQL: `MIGRATIONS_COMPLETED`.
- Current Alembic revision: `006_phase_7b_knowledge_governance`.
- Production schema verification completed.
- Production-safe bootstrap completed: `PRODUCTION_SAFE_BOOTSTRAP_COMPLETED`.
- Production knowledge seed completed: `KNOWLEDGE_SEED_COMPLETED`.
- Production DB seed verification completed: `PRODUCTION_DB_SEED_VERIFIED`.
- Artifact Registry repository created: `alte-ai-crm`.
- Docker image built and pushed: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.8-cloud-run`.
- Cloud Run deployment completed: `CLOUD_RUN_DEPLOYED`.
- Cloud Run service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`.
- Cloud SQL attached: `CLOUD_SQL_ATTACHED`.
- Secret Manager mapped: `SECRET_MANAGER_MAPPED`.
- Unauthenticated access enabled for public website widget API.
- Endpoint verification completed:
  - `/health: 200`
  - `/version: 200`
  - `/diagnostics/ai: 200`
  - `/diagnostics/local-demo: 200`
  - `/dashboard/overview: 401` without bearer token, expected with `AUTH_REQUIRED=true`.
- Website/privacy approval checklist prepared.
- Production widget embed guide prepared.
- Production widget smoke checklist prepared.
- Production widget config examples prepared for `alte.edu.ge` and `join.alte.edu.ge`.
- Versioned widget asset prepared: `widget/alte-chat-widget.v0.8.js`.
- Widget asset hosting decision prepared; recommended Option A website/CMS static asset hosting.
- Final embed snippets prepared: `WIDGET_EMBED_SNIPPETS_FINAL.md`.
- Website developer handoff prepared: `WEBSITE_DEVELOPER_HANDOFF.md`.
- Staging/test page package prepared: `widget/production-embed-test.html`.
- Actual website embed status: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`.
- Standalone production widget demo prepared: `widget/standalone-production-demo.html`.
- Standalone production demo README prepared: `widget/STANDALONE_PRODUCTION_DEMO.md`.
- Standalone smoke checklist prepared: `STANDALONE_WIDGET_SMOKE_CHECKLIST.md`.
- Transfer package prepared: `WIDGET_TRANSFER_TO_ALTE_SITE.md`.
- Phase 8M standalone backend/API smoke passed:
  - local static demo page returned `200`
  - widget JS asset returned `200`
  - production `/health`, `/version`, and `/diagnostics/ai` returned `200`
  - Claude enabled; no secrets exposed
  - `alte.edu.ge` / `ka` backend API smoke PASS
  - `join.alte.edu.ge` / `en` backend API smoke PASS
- Production CORS preflight passed for `https://alte.edu.ge`.
- Production CORS preflight passed for `https://join.alte.edu.ge`.
- Localhost browser CORS blocked as expected: `http://127.0.0.1:5500` returned `400`.
- CORS localhost decision recorded: `LOCALHOST_CORS_NOT_APPROVED_FOR_PRODUCTION`.
- Phase 8N website/privacy approval gate created:
  - `WEBSITE_EMBED_APPROVAL_GATE.md`
  - `PRIVACY_CONSENT_APPROVAL.md`
  - `FINAL_WIDGET_EMBED_GO_NO_GO.md`
  - `WIDGET_FINAL_ASSET_URL_DECISION.md`
- Final widget embed decision: `NO-GO_FOR_ACTUAL_SITE_EMBED`.
- Phase 8O sandbox package prepared:
  - full standalone chatbot test site: `widget/full-standalone-chatbot-test.html`
  - required test knowledge seed: `alte_required_test_knowledge_v1.json`
  - seed command: `python -m app.scripts.seed_required_test_knowledge`
  - API smoke command: `python -m app.scripts.standalone_chatbot_api_smoke`
  - standalone test runbooks prepared
- Production seed was not run in Phase 8O.
- Phase 8P safe standalone API smoke completed:
  - `/health`, `/version`, `/diagnostics/ai`: PASS
  - `alte.edu.ge` / `ka` greeting: PASS
  - `alte.edu.ge` / `ka` finance question: PASS, no exact invented price, handover true
  - `join.alte.edu.ge` / `en` medicine/international question: PASS, routed to international admissions
  - contact-flow flag was not used
  - no phone/email/contact details were submitted
  - no lead/task was intentionally created
  - observed side effect: medicine/international admission message triggered existing backend business rules to create a lead/task
- Phase 8P-Fix no-contact guard applied locally:
  - no contact -> no lead/task for admissions, consultation, international, or medicine admission intent
  - contact present -> create/update customer, lead, and follow-up task
  - human request chat behavior remains contact-gated for task creation; the explicit handover endpoint still creates a handover task
- Phase 8P-Redeploy completed:
  - image tag: `v0.8-no-contact-guard`
  - Cloud Run revision: `alte-ai-crm-backend-00003-x84`
  - `/health`, `/version`, `/diagnostics/ai`: PASS
  - safe standalone API smoke rerun: PASS
  - medicine/international no-contact side effect fixed: `created_lead_id=null`, `created_task_id=null`, `should_create_lead=false`
  - contact-flow test was not run
- Production test knowledge seed approval gate created: `TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md`; status `APPROVED_AND_EXECUTED`.
- Phase 8Q production test knowledge seed completed:
  - first run: `sources_created=12`, `snippets_created=13`, `skipped_existing=0`, `review_required_count=11`
  - second run/idempotency: `sources_created=0`, `snippets_created=0`, `skipped_existing=13`
  - required test knowledge verification: PASS
  - safe API smoke after seed: PASS
  - contact-flow test was not run
  - no intentional production lead/task creation
  - official content review still required before public launch
- Phase 8R official content review gate created:
  - `OFFICIAL_CONTENT_REVIEW_REPORT.md`
  - `OFFICIAL_CONTENT_REVIEW_CHECKLIST.md`
  - `CHATBOT_PUBLIC_ANSWER_POLICY.md`
  - `KNOWLEDGE_REVIEW_QUEUE_TEMPLATE.csv`
  - content review status: `OFFICIAL_CONTENT_REVIEW_STATUS=PENDING`
  - public launch remains blocked until official review is approved
- Phase 8S official content review apply dry-run completed:
  - explicit reviewer decisions found: 0
  - reviewer `decision` column present: NO
  - `recommended_action` values treated as reviewer decisions: NO
  - `--apply` run: NO
  - applied count: 0
  - sensitive fully approved count: 0
  - sensitive pending review count: 7
  - apply status: `OFFICIAL_CONTENT_REVIEW_APPLY_STATUS=DRY_RUN_ONLY_PENDING_REVIEWER_DECISIONS`
- Phase 8T reviewer decision CSV prepared:
  - reviewer CSV: `backend/reports/knowledge_review_queue_for_review.csv`
  - rows prepared: 26
  - reviewer `decision` column added: YES
  - decision column prefilled: NO
  - `--apply` run: NO
  - decision state: `BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW`
- Alte study docs Knowledge Base import completed:
  - source evidence copied to `docs/knowledge_evidence/alte_study_docs/`
  - normalized seed: `backend/app/knowledge_seed/alte_study_docs/alte_study_docs_seed_v1.json`
  - production Knowledge Base import: `sources_created=11`, `snippets_created=11`
  - sensitive records remain `review_required=true`
  - decision state: `BACKEND_DEPLOYED_STUDY_DOCS_KNOWLEDGE_IMPORTED_PENDING_OFFICIAL_REVIEW`
- Full local Alte KB import completed:
  - evidence copied to `docs/knowledge_evidence/alte_full_local_kb/`
  - normalized seed: `backend/app/knowledge_seed/full_alte_local_kb/full_alte_local_kb_normalized.jsonl`
  - source pages: 123
  - knowledge chunks: 647
  - production Knowledge Base import: 240 sources created, 390 sources updated, 645 snippets created, 2 duplicate snippets skipped
  - high-sensitivity records: 379
  - review-required records: 379
  - sensitive official facts remain review-required and are not public-approved automatically
  - decision state: `BACKEND_DEPLOYED_FULL_LOCAL_KB_IMPORTED_PENDING_HUMAN_REVIEW`
- Phase 8Y finance no-contact lead guard deployed and verified:
  - tuition/finance no-contact lead bug found in Phase 8W
  - finance/tuition/scholarship/deadline information questions without phone/email now force `should_create_lead=false`
  - no customer/lead/task is created for no-contact finance information requests
  - deployed to Cloud Run with image tag `v0.8-finance-no-contact-guard`
  - finance no-contact smoke passed `24/24`; broader knowledge smoke passed `25/25`
  - decision state: `BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED`
- Phase 8F execution plan prepared for later explicit approval.

## Remaining Full Launch Blockers

- Website admin/developer access pending.
- Privacy/data approval pending.
- Actual website widget embed pending.
- Final widget asset URL pending.
- Real-domain browser widget smoke from `alte.edu.ge` / `join.alte.edu.ge` pending.
- Official content/privacy review pending before public launch.
- Official content review pending before public launch.
- Phase 8W tuition no-contact `should_create_lead=true` behavior resolved by Phase 8Y-Redeploy.
- Full public launch approval pending.

## No-Go If

- [ ] Real secrets are in Git, docs, chat, or screenshots. Current docs scan passed; do not paste new secrets.
- [ ] `.env` is tracked. Current release verification says `.env` is not tracked.
- [ ] Tests fail.
- [ ] Claude live test fails.
- [ ] Cloud SQL is not planned.
- [ ] CORS uses wildcard.
- [ ] No rollback plan exists.
## Phase 8Y-Redeploy Update

The finance/tuition no-contact guard has been deployed to Cloud Run and verified in production.

- Image tag: `v0.8-finance-no-contact-guard`
- Previous revision: `alte-ai-crm-backend-00003-x84`
- New revision: `alte-ai-crm-backend-00004-gsn`
- Endpoint checks: `/health=200`, `/version=200`, `/diagnostics/ai=200`
- Finance no-contact smoke: `24 passed`, `0 failed`
- Broader knowledge smoke: `25 passed`, `0 failed`
- Contact-flow test: not run
- Contact details sent: no
- Intentional production lead/task/customer creation: no
- Finance/tuition/scholarship/deadline no-contact responses now keep `should_create_lead=false` and no created IDs.

Decision state:

```text
BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

Public launch remains blocked until human reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, real-domain browser smoke, and explicit launch approval are completed.

## Phase 9D-UI-Final Exact Pro Sidebar Widget

The final preferred widget UI is the exact functional Pro Sidebar layout from the uploaded design ZIP/screenshots.

- Final widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Archived compact/PIP alternate: `widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html`
- Standalone demo: `widget/standalone-safe-pro-demo.html`
- Sidebar departments and quick chips send `selected_department` and `selected_topic` context to the backend.
- The browser calls only the FastAPI backend endpoints: `/chat/session/start` and `/chat/message`.
- The frontend does not call Anthropic directly, expose secrets, own the system prompt, create CRM records, or hardcode sensitive official facts.
- Actual site embed and public launch remain blocked.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_PRO_SIDEBAR_WIDGET_FUNCTIONAL_READY_PENDING_REDEPLOY_AND_SITE_EMBED
```

## Phase 9C Final Pre-Embed Gate

The final pre-embed approval gate has been created.

- Gate: `docs/deployment/FINAL_PRE_EMBED_APPROVAL_GATE.md`
- Selected widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Asset hosting status: `WIDGET_ASSET_HOSTING_STATUS=PENDING_FINAL_URL`
- Privacy/data approval status: `PRIVACY_DATA_APPROVAL_STATUS=PENDING`
- Pre-embed status: `FINAL_PRE_EMBED_STATUS=NO_GO_PENDING_APPROVALS`
- Actual site embed: not complete.
- Public launch: not complete.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_PRE_EMBED_GATE_READY_PENDING_APPROVALS
```

Do not proceed to actual site embed until human reviewer decisions, official content approval, privacy/data approval, final widget asset URL, website admin/developer confirmation, and real-domain smoke approval are complete.

## Phase 9D Department-Aware Handover Routing

Department-aware routing is ready in code.

- Admissions, International Admissions, Finance, Medicine / MD, Student Services, IT Support, and General / Operator routing rules are implemented.
- Safe Pro widget sends sidebar context to backend.
- Backend decides handover, routing, and CRM actions.
- Frontend does not create customers/leads/tasks.
- Production redeploy is required before Cloud Run uses the new routing behavior.

Decision state:

```text
BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY
```

Public launch and actual embed remain blocked.

## Phase 9A Human Reviewer Package

The final human reviewer decision package has been created.

- Reviewer package folder: `docs/reviewer_package/`
- Full reviewer CSV: `docs/reviewer_package/alte_kb_human_review_decisions.csv`
- Compact reviewer CSV: `docs/reviewer_package/alte_kb_human_review_compact.csv`
- Georgian instructions and summary are included.
- Rows: 647
- High-sensitivity rows: 379
- Review-required rows: 379
- Human decisions filled: 0
- Validation status: `PENDING_HUMAN_DECISIONS`

Decision state:

```text
BACKEND_DEPLOYED_REVIEWER_PACKAGE_READY_PENDING_HUMAN_DECISIONS
```

Public launch remains blocked until reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, real-domain browser smoke, and explicit launch approval are completed.

## Phase 9B Widget Design Concepts

Uploaded widget design concepts were imported and reviewed as UI evidence.

- Evidence folder: `docs/knowledge_evidence/uploaded_widget_design_concepts/`
- Concept review: `docs/deployment/WIDGET_DESIGN_CONCEPTS_REVIEW.md`
- Safe Pro candidate: `widget/alte-university-ai-chatbot-safe-pro.html`
- Standalone preview: `widget/standalone-safe-pro-demo.html`
- Embed snippet draft: `docs/deployment/WIDGET_SAFE_PRO_EMBED_SNIPPET.md`
- Recommended candidate: compact PIP-style widget with selected Pro-style polish.
- Direct browser Anthropic calls are forbidden.
- The browser widget must call the FastAPI backend only.
- The frontend must not own the system prompt, Knowledge Base truth, or CRM lead creation.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_CANDIDATE_READY_PENDING_REVIEW_AND_SITE_EMBED
```

Public launch remains blocked until human reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, real-domain browser smoke, and explicit launch approval are completed.
