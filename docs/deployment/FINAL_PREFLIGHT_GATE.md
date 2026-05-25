# Final Preflight Gate

Current decision: `BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW`

Previous backend deployment state `BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY` remains true. Historical gate `NO-GO_FOR_ACTUAL_DEPLOYMENT` is superseded for backend deployment only. Keep full public launch blocked until every remaining website/privacy item below is checked.
Previous smoke state `BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE` remains true.
Previous website/privacy gate state `BACKEND_DEPLOYED_WIDGET_READY_PENDING_WEBSITE_PRIVACY_APPROVAL` remains true.
Previous full standalone site state `BACKEND_DEPLOYED_FULL_STANDALONE_CHATBOT_READY_PENDING_REAL_SITE_EMBED` remains true.
Previous safe smoke state `BACKEND_DEPLOYED_STANDALONE_API_SMOKE_PASSED_PENDING_TEST_KNOWLEDGE_APPROVAL` remains true for endpoint availability; no-contact lead/task creation now requires redeploy.
Previous no-contact guard redeploy state `BACKEND_DEPLOYED_STANDALONE_API_SMOKE_NEEDS_REDEPLOY_FOR_NO_CONTACT_GUARD` is resolved.
Previous no-contact verification state `BACKEND_DEPLOYED_NO_CONTACT_GUARD_VERIFIED_PENDING_TEST_KNOWLEDGE_APPROVAL` is resolved by Phase 8Q.
Previous seeded state `BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_SAFE_SMOKE_PASSED_PENDING_OFFICIAL_REVIEW_AND_SITE_EMBED` remains true and now advances to the official content review gate.
Previous official content gate state `BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_PENDING_OFFICIAL_CONTENT_REVIEW` remains true and now advances to reviewer-decision-CSV-ready-pending-human-review.

| Area | Check | Status |
| --- | --- | --- |
| GitHub | Remote configured | Done: `https://github.com/rgelikoshvili-stack/alte-ai-crm` |
| GitHub | Code pushed | Done: `master` pushed to `origin/master` at `162db35` |
| GitHub | Release tag `v0.8-deployment-ready` created | Done: tag pushed to origin at `162db35` |
| Google Cloud | `PROJECT_ID` confirmed | Done: `project-1e145fd0-c30e-4aac-a34` |
| Google Cloud | Billing enabled | Done: user confirmed |
| Google Cloud | Region confirmed | Done: `europe-west1` |
| Google Cloud | APIs ready to enable | Planned |
| Google Cloud | Cloud SQL tier/cost accepted | Done for pilot direction; exact price review still required during resource creation |
| Google Cloud | Cloud SQL tier/cost decision doc | Done: `CLOUD_SQL_TIER_DECISION.md`; status `PENDING_APPROVAL` |
| Google Cloud | Cloud SQL cost approval form | Done: `CLOUD_SQL_COST_APPROVAL_FORM.md`; recommended option: Low-cost pilot production tier; status `APPROVED_FOR_PILOT` |
| Google Cloud | Cloud SQL instance created | Done: `CLOUD_SQL_INSTANCE_CREATED`, Enterprise edition, `db-f1-micro`, `europe-west1` |
| Google Cloud | Cloud SQL database created | Done: `DATABASE_CREATED`, `alte_ai_crm` |
| Google Cloud | Cloud SQL app user created | Done: `DB_USER_CREATED`, `alte_app` |
| Google Cloud | Secret Manager containers created | Done: four `alte-*` secret containers created |
| Google Cloud | Secret Manager DB/JWT/Anthropic values created | Done: versions added without printing payloads |
| Google Cloud | Secret Manager DATABASE_URL value created | Done: `VERSION_ADDED` without printing value |
| Google Cloud | Artifact Registry repository | Done: `alte-ai-crm` |
| Google Cloud | Docker image pushed | Done: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.8-cloud-run` |
| Google Cloud | Cloud Run deployment | Done: `CLOUD_RUN_DEPLOYED` |
| Google Cloud | Cloud Run service URL | Done: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app` |
| Google Cloud | No-contact guard image deployed | Done: `v0.8-no-contact-guard`, revision `alte-ai-crm-backend-00003-x84` |
| Google Cloud | Cloud SQL attached to Cloud Run | Done: `CLOUD_SQL_ATTACHED` |
| Google Cloud | Secret Manager mapped to Cloud Run | Done: `SECRET_MANAGER_MAPPED` |
| Google Cloud | Unauthenticated access for widget API | Done: enabled for public widget API |
| Google Cloud | Secret Manager creation approval | Done for next execution phase: `APPROVED_FOR_NEXT_EXECUTION` |
| Google Cloud | Secret Manager execution | Container creation completed; DB/JWT/Anthropic versions added |
| Google Cloud | Secret values runbook | Done: `SECRET_VALUES_RUNBOOK.md`; statuses `NOT_CREATED / PENDING` |
| Google Cloud | Secret preparation checklist | Done: `SECRET_PREPARATION_CHECKLIST.md`; values not created |
| Google Cloud | Secret values preparation worksheet | Done: `SECRET_VALUES_PREPARATION_WORKSHEET.md`; no real values |
| Google Cloud | Secret Manager approval gate | Done: `SECRET_MANAGER_APPROVAL_GATE.md`; status `APPROVED_FOR_NEXT_EXECUTION` |
| Google Cloud | DATABASE_URL construction guide | Done: `DATABASE_URL_CONSTRUCTION.md`; placeholders only |
| Google Cloud | DATABASE_URL secret version | Done |
| Google Cloud | Local secret helper script | Done: `scripts/prepare_secret_values.ps1`; guidance only |
| Security | `.env` not tracked | Done |
| Security | No secrets in docs | Done by verifier |
| Security | Anthropic key rotated if previously exposed | Pending owner confirmation |
| Security | Secrets stored only in Secret Manager | Pending |
| Security | `AUTH_REQUIRED=true` for production | Planned in production env |
| Application | Tests pass | Done: `106 passed` in Phase 8D-Prep |
| Application | Release checkpoint passes | Done |
| Application | Deployment docs verifier passes | Done |
| Application | `startup_check` passes with production-like env | Pending |
| Application | Docker build check planned/pass | Planned, not run in final preflight |
| Application | Claude live validation passed | Done |
| Application | Alembic version table width correction | Done: `alembic_version.version_num VARCHAR(128)` |
| Application | Production migrations against Cloud SQL | Done: `MIGRATIONS_COMPLETED`, current revision `006_phase_7b_knowledge_governance` |
| Application | Production-safe core bootstrap | Done: `PRODUCTION_SAFE_BOOTSTRAP_COMPLETED`; no fake customers/leads/messages |
| Application | Knowledge seed against Cloud SQL | Done: `KNOWLEDGE_SEED_COMPLETED` |
| Application | Production DB seed verification | Done: `PRODUCTION_DB_SEED_VERIFIED` |
| Application | `/health` check | Done: `/health: 200` |
| Application | `/version` check | Done: `/version: 200` |
| Application | `/diagnostics/ai` check | Done: `/diagnostics/ai: 200` |
| Application | `/diagnostics/local-demo` check | Done: `/diagnostics/local-demo: 200` |
| Application | `/dashboard/overview` read-only check | Done: `/dashboard/overview: 401` without bearer token, expected with `AUTH_REQUIRED=true` |
| Application | `AI_PROVIDER=mock` for tests | Required |
| Application | `AI_PROVIDER=claude` for production | Planned |
| Website | `alte.edu.ge` CORS confirmed | Done |
| Website | `join.alte.edu.ge` CORS confirmed | Done |
| Website | Website developer/admin access | Pending: Website admin/developer access pending |
| Website | Privacy/consent text approval | Pending: Privacy/data approval pending |
| Website | Actual website widget embed | Pending: Actual website widget embed pending |
| Website | Production widget smoke | Pending |
| Website | Website/privacy checklist | Done: `WEBSITE_AND_PRIVACY_APPROVAL.md`; statuses pending |
| Website | Production embed guide | Done: `WEBSITE_WIDGET_PRODUCTION_EMBED.md` |
| Website | Production widget smoke checklist | Done: `PRODUCTION_WIDGET_SMOKE_CHECKLIST.md` |
| Website | Alte config example | Done: `widget/production-config.alte.example.js` |
| Website | Join config example | Done: `widget/production-config.join.example.js` |
| Website | Versioned widget asset | Done: `widget/alte-chat-widget.v0.8.js` |
| Website | Widget asset hosting decision | Done: `WIDGET_ASSET_HOSTING_DECISION.md`; recommended Option A website/CMS static asset hosting |
| Website | Final widget snippets | Done: `WIDGET_EMBED_SNIPPETS_FINAL.md` |
| Website | Website developer handoff | Done: `WEBSITE_DEVELOPER_HANDOFF.md` |
| Website | Staging/test page package | Done: `widget/production-embed-test.html` |
| Website | Standalone production widget demo | Done: `widget/standalone-production-demo.html` |
| Website | Standalone demo README | Done: `widget/STANDALONE_PRODUCTION_DEMO.md` |
| Website | Transfer package | Done: `WIDGET_TRANSFER_TO_ALTE_SITE.md` |
| Website | Standalone smoke checklist | Done: `STANDALONE_WIDGET_SMOKE_CHECKLIST.md` |
| Website | Standalone backend/API smoke | Done: local page `200`, widget asset `200`, backend `/health`, `/version`, `/diagnostics/ai` `200`, safe chat API PASS for `alte.edu.ge` / `ka` and `join.alte.edu.ge` / `en` |
| Website | Production domain CORS preflight | Done: `https://alte.edu.ge` PASS, `https://join.alte.edu.ge` PASS |
| Website | Localhost browser CORS | Blocked as expected: `http://127.0.0.1:5500` FAIL `400`; `LOCALHOST_CORS_NOT_APPROVED_FOR_PRODUCTION` |
| Website | Real-domain browser widget smoke | Pending |
| Website | Website embed approval gate | Done: `WEBSITE_EMBED_APPROVAL_GATE.md`; statuses pending |
| Website | Privacy consent approval doc | Done: `PRIVACY_CONSENT_APPROVAL.md`; status pending |
| Website | Final widget embed go/no-go | Done: `FINAL_WIDGET_EMBED_GO_NO_GO.md`; `NO-GO_FOR_ACTUAL_SITE_EMBED` |
| Website | Final widget asset URL decision | Done: `WIDGET_FINAL_ASSET_URL_DECISION.md`; `FINAL_WIDGET_ASSET_URL=PENDING` |
| Website | Full standalone chatbot test site | Done: `widget/full-standalone-chatbot-test.html` |
| Website | Required standalone test knowledge package | Done: `alte_required_test_knowledge_v1.json`; production seed not run in Phase 8O |
| Website | Standalone chatbot API smoke script | Done: `standalone_chatbot_api_smoke.py` |
| Website | Standalone test runbooks | Done: `STANDALONE_TEST_SITE_RUNBOOK.md`, `STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md`, `FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md` |
| Website | Safe standalone API smoke | Done: `/health`, `/version`, `/diagnostics/ai`, KA greeting, KA finance, EN medicine/international PASS |
| Website | Contact-flow smoke | Not run |
| Website | Intentional lead/task creation | No; observed backend side effect for medicine/international admission message |
| Website | No-contact lead/task guard | Deployed and verified: admissions/international/medicine require phone or email before lead/task creation |
| Website | Safe smoke after no-contact redeploy | Done: contact-flow not run; no contact details sent; medicine/international no-contact returned no lead/task |
| Website | Production test knowledge seed approval | Done: `TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md`, status `APPROVED_AND_EXECUTED` |
| Website | Production test knowledge seed execution | Done: first run created 12 sources / 13 snippets; second run created zero duplicates |
| Website | Required test knowledge verification | Done: contact, admissions, finance, international, medicine, deadlines PASS |
| Website | Safe smoke after test knowledge seed | Done: contact-flow not run; no intentional lead/task creation |
| Website | Official content review gate | Done: report, checklist, public-answer policy, review queue template |
| Website | Official content review status | Pending: `OFFICIAL_CONTENT_REVIEW_STATUS=PENDING` |
| Website | Official content review apply dry-run | Done: reviewer `decision` column missing, no explicit reviewer decisions, no apply run, no content auto-approved |
| Website | Reviewer decision CSV | Done: `backend/reports/knowledge_review_queue_for_review.csv` prepared with blank `decision` column |
| Website | Alte study docs Knowledge Base import | Done: copied local study docs, normalized 11 records, imported 11 sources / 11 snippets into Knowledge Base; sensitive records remain review-required |
| Website | Full local Alte KB import | Done: copied local full KB/prototype evidence, normalized 647 records, imported 240 sources and 645 snippets into Knowledge Base; 379 sensitive records remain review-required |
| Website | Production knowledge smoke after study docs | Original Phase 8W review item resolved by Phase 8Y-Redeploy; latest broader knowledge smoke `25 passed`, `0 failed` |
| Website | Finance no-contact lead guard | Deployed and verified: finance/tuition/scholarship/deadline info questions without phone/email force `should_create_lead=false`; finance smoke `24 passed`, `0 failed` |
| Website | Phase 8Y-Redeploy finance no-contact guard | Done: deployed image `v0.8-finance-no-contact-guard` to `alte-ai-crm-backend-00004-gsn`; finance smoke `24 passed`, broader knowledge smoke `25 passed`; no contact-flow/contact details/intentional lead-task-customer creation |
| Website | Phase 9A human reviewer package | Done: `docs/reviewer_package/` created with 647 rows, 379 high-sensitivity rows, 379 review-required rows; human decisions still pending |
| Website | Actual website embed status | Blocked: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL` |
| Execution | Phase 8F execution plan | Done: `PHASE_8F_EXECUTION_PLAN.md`; do not run until approved |

## Decision

Do not proceed to full public launch until:

- GitHub backup is pushed and tagged.
- Cloud SQL tier/cost is accepted.
- Cloud SQL cost/tier approval is explicitly confirmed by user/billing owner.
- Secret Manager payload versions are created without exposing secrets.
- Secret Manager Phase 8F-Execution is explicitly approved.
- Production migrations are run against Cloud SQL. Done in Phase 8H-Correction.
- Production seed is run against Cloud SQL. Done in Phase 8H-Correction.
- Alte website access is confirmed.
- Data privacy approval is confirmed.

## Phase 9B Safe Pro Widget Candidate

- Uploaded widget design concepts imported to `docs/knowledge_evidence/uploaded_widget_design_concepts/`.
- Safe Pro candidate created at `widget/alte-university-ai-chatbot-safe-pro.html`.
- Standalone preview created at `widget/standalone-safe-pro-demo.html`.
- Embed snippet draft created at `docs/deployment/WIDGET_SAFE_PRO_EMBED_SNIPPET.md`.
- Recommended design direction: compact PIP-style public widget with selected Pro-style polish.
- Direct browser Anthropic calls are forbidden.
- Backend remains the only AI/CRM integration point.
- Public launch is not complete.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_CANDIDATE_READY_PENDING_REVIEW_AND_SITE_EMBED
```

## Phase 9C Final Pre-Embed Gate

- Final pre-embed gate created: `docs/deployment/FINAL_PRE_EMBED_APPROVAL_GATE.md`
- Selected widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Widget asset hosting status: `WIDGET_ASSET_HOSTING_STATUS=PENDING_FINAL_URL`
- Privacy/data approval status: `PRIVACY_DATA_APPROVAL_STATUS=PENDING`
- Real-domain smoke plan: `docs/deployment/REAL_DOMAIN_WIDGET_SMOKE_PLAN.md`
- Rollback plan: `docs/deployment/WIDGET_EMBED_ROLLBACK_PLAN.md`
- Actual embed is not complete.
- Public launch is not complete.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_PRE_EMBED_GATE_READY_PENDING_APPROVALS
```

## Phase 9D Department Routing Gate

- Department-aware fallback/handover routing is implemented in backend code.
- Safe Pro widget sends `selected_department` and `selected_topic`.
- Backend response includes `route_department`, `department_key`, and `routing_reason`.
- Production redeploy is required.
- Public launch is not complete.

Decision state:

```text
BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY
```

## Phase 9D-UI-Final Exact Pro Sidebar Widget

- Final widget rebuilt as exact functional Pro Sidebar layout: `widget/alte-university-ai-chatbot-safe-pro.html`.
- Compact/PIP alternate archived: `widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html`.
- Standalone demo updated: `widget/standalone-safe-pro-demo.html`.
- Sidebar departments and quick chips send `selected_department` and `selected_topic` context to backend.
- Handover/operator UI, contact request UI, source cards, trust bar, KA/EN switch, reset, and composer are present.
- Browser calls only FastAPI backend endpoints.
- Frontend does not call Anthropic, expose secrets, create CRM records, or hardcode sensitive official facts.
- Public launch and actual embed are not complete.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_PRO_SIDEBAR_WIDGET_FUNCTIONAL_READY_PENDING_REDEPLOY_AND_SITE_EMBED

## Phase 9D-Redeploy Department Routing Gate

Result: NO-GO for site embed.

The backend was redeployed with image `v0.9-department-routing-sidebar`, and production endpoints remained healthy. Finance no-contact and broader knowledge smoke tests passed after deploy.

Department routing smoke did not fully pass:

- Total: `28`
- Passed: `26`
- Failed: `2`
- Failed cases: ambiguous Finance sidebar context and ambiguous Medicine sidebar context routed to `Admissions`

No contact details were sent, no contact-flow test was run, and no intentional production customer/lead/task creation occurred.

Required before embed:

- Fix ambiguous sidebar department priority.
- Redeploy.
- Pass department routing smoke.

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```
```
