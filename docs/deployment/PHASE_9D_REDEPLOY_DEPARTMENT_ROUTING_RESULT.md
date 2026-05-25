# Phase 9D-Redeploy Department Routing Result

Date/time: 2026-05-25 10:44:34 +04:00

## Deployment

- Image tag: `v0.9-department-routing-sidebar`
- Image path: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-department-routing-sidebar`
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Previous revision: `alte-ai-crm-backend-00004-gsn`
- New revision: `alte-ai-crm-backend-00005-px7`

## Endpoint Verification

- `/health`: 200
- `/version`: 200
- `/diagnostics/ai`: 200, Claude enabled, no secret values exposed

Cloud Run settings were preserved:

- Cloud SQL attachment present
- Secret Manager environment mappings present
- Existing non-secret environment variable names present
- CORS environment configuration present

## Department Routing Smoke

- Command: `python -m app.scripts.production_department_routing_sidebar_smoke`
- Total tests: 28
- Passed: 26
- Failed: 2
- No contact details sent: yes
- Contact-flow test not run: yes
- Intentional lead/task/customer creation: no
- No-contact guard confirmed: yes
- Handover routing confirmed: yes
- Department context confirmed: no

Failures:

- `finance_sidebar_ambiguous route department`: with `selected_department=finance`, `selected_topic=tuition`, and message `მაინტერესებს დეტალები`, production routed to `department_key=admissions` instead of `finance`.
- `medicine_sidebar_ambiguous route department`: with `selected_department=medicine`, `selected_topic=medicine`, and message `დეტალები მაინტერესებს`, production routed to `department_key=admissions` instead of `medicine`.

Observed behavior:

- No customer, lead, or task IDs were created in the failed cases.
- `should_create_lead=false` in the failed cases.
- The remaining department-specific cases passed.
- The routing issue is isolated to ambiguous messages where sidebar context should override or strongly influence fallback routing.

## Per-Department Result

- Finance: direct tuition routing passed; ambiguous sidebar-only finance context failed.
- Admissions/deadline: passed, no invented exact deadline and no lead/task/customer side effect.
- International: passed, no lead/task/customer side effect.
- Medicine: direct medicine/international routing passed; ambiguous sidebar-only medicine context failed.
- IT Support: passed.
- Student Services: passed.
- Human/operator selected department: passed with no contact details and no CRM record creation.

## Existing Smoke Summaries

Finance no-contact smoke:

- Command: `python -m app.scripts.production_finance_no_contact_smoke`
- Total tests: 24
- Passed: 24
- Failed: 0
- No contact details sent: yes
- Contact-flow test not run: yes
- Intentional lead/task/customer creation: no

Broader knowledge smoke:

- Command: `python -m app.scripts.production_knowledge_smoke_after_study_docs`
- Total tests: 25
- Passed: 25
- Failed: 0
- No contact details sent: yes
- Contact-flow test not run: yes
- Intentional lead/task/customer creation: no

## Status

PHASE_9D_REDEPLOY_STATUS=FAILED_DEPARTMENT_ROUTING_NEEDS_REVIEW

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```

## Phase 9E Follow-Up

The ambiguous sidebar routing bug has been fixed in backend code after this redeploy result.

Fix summary:

- `selected_department=finance` + `მაინტერესებს დეტალები` now routes to Finance in local tests.
- `selected_department=medicine` + `დეტალები მაინტერესებს` now routes to Medicine / MD in local tests.
- Strong explicit keywords still override sidebar context.
- No-contact guard remains unchanged.

Production redeploy is still required before this result changes in Cloud Run.

Follow-up decision state:

```text
BACKEND_CODE_FIXED_SIDEBAR_AMBIGUOUS_ROUTING_PENDING_REDEPLOY
```

## Required Follow-Up

- Fix routing priority so an explicit `selected_department` and `selected_topic` are preserved for ambiguous sidebar messages.
- Rebuild and redeploy after the routing fix.
- Rerun `production_department_routing_sidebar_smoke`.
- Do not proceed to actual site embed or public launch until department routing smoke passes.

## Remaining Blockers

- Department routing ambiguity bug needs review/fix/redeploy
- Human reviewer decisions pending
- Official content approval pending
- Privacy/data approval pending
- Final widget asset URL pending
- Actual site embed pending
- Real-domain browser smoke pending

## Safety Confirmation

- Cloud Run deployed only approved service: `alte-ai-crm-backend`
- Docker image pushed only to approved Artifact Registry: `alte-ai-crm`
- No Cloud SQL schema changes
- No migrations run
- No production seed run
- No Secret Manager changes
- No secrets printed
- `DATABASE_URL` not printed
- No contact-flow test run
- No contact details sent
- No intentional production leads/tasks/customers created
- No live website scraping/crawling
- No real Alte website modified
- No Google Cloud resources changed except approved Cloud Run revision/image
- `.env` not committed
- `.local-secrets` not committed
- Bridge Hub not touched
- Public launch not marked complete
