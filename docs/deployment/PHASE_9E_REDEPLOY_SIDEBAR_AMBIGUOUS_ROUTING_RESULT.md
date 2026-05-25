# Phase 9E-Redeploy Sidebar Ambiguous Routing Result

Date/time: 2026-05-25 11:46:30 +04:00

## Deployment

- Image tag: `v0.9-sidebar-ambiguous-routing-fix`
- Image path: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-sidebar-ambiguous-routing-fix`
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Previous revision: `alte-ai-crm-backend-00005-px7`
- New revision: `alte-ai-crm-backend-00006-vs5`

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
- Passed: 28
- Failed: 0
- No contact details sent: yes
- Contact-flow test not run: yes
- Intentional lead/task/customer creation: no
- No-contact guard confirmed: yes
- Department context confirmed: yes
- Handover routing confirmed: yes

Previously failing cases:

- Finance ambiguous sidebar case: PASS. With `selected_department=finance`, `selected_topic=tuition`, and message `მაინტერესებს დეტალები`, production preserved Finance routing.
- Medicine ambiguous sidebar case: PASS. With `selected_department=medicine`, `selected_topic=medicine`, and message `დეტალები მაინტერესებს`, production preserved Medicine / MD routing.

## Additional Smoke Checks

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
- Final run total tests: 25
- Final run passed: 25
- Final run failed: 0
- No contact details sent: yes
- Contact-flow test not run: yes
- Intentional lead/task/customer creation: no

Note: one earlier broader-knowledge run reported a transient deadline-conservatism assertion failure. A follow-up detailed run and the final rerun passed, with no contact data sent and no lead/task/customer created.

## Status

PHASE_9E_REDEPLOY_STATUS=PASSED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED

Decision state:

```text
BACKEND_DEPLOYED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

## Remaining Blockers

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
