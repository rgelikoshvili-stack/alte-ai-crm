# Phase 9K Redeploy Security Reliability Result

PHASE_9K_REDEPLOY_STATUS=PASSED_SECURITY_RELIABILITY_VERIFIED

Date/time: 2026-05-25T18:58:50+04:00

Decision state:

```text
BACKEND_DEPLOYED_SECURITY_RELIABILITY_VERIFIED_PENDING_FINAL_APPROVALS_AND_SITE_EMBED
```

## Deployment

- Image tag: `v0.9-security-reliability-fixes`
- Image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-security-reliability-fixes`
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Previous revision: `alte-ai-crm-backend-00006-vs5`
- New revision: `alte-ai-crm-backend-00007-xmp`
- Previous image: `v0.9-sidebar-ambiguous-routing-fix`
- Cloud SQL attachment: confirmed present
- Secret Manager env mappings: confirmed present without printing secret values
- CORS env presence: confirmed, unchanged

## Endpoint Verification

- `/health`: `200`
- `/version`: `200`
- `/diagnostics/ai`: `200`
- Claude enabled: yes
- Diagnostics exposed no secret values

Production auth guard:

- Protected endpoint without auth: `/dashboard/overview` returned `401`
- `ENVIRONMENT=production`: confirmed
- `AUTH_REQUIRED=true`: confirmed

## Security/Reliability Smoke

`python -m app.scripts.production_security_reliability_smoke`

- total tests: 16
- passed: 16
- failed: 0
- auth guard confirmed: true
- handover spam guard confirmed: true
- AI provider failure fallback: code/test verified locally; production fault simulation not executed
- no contact details sent: true
- contact-flow test run: false
- intentional lead/task/customer creation: no

Handover spam guard result:

- public handover endpoint accepted only the session returned by `/chat/session/start`
- repeated no-contact handover calls did not create a task
- no customer/lead/task creation was intentionally triggered

## Existing Safe Production Smoke

Department routing sidebar smoke:

- total tests: 28
- passed: 28
- failed: 0
- contact details sent: false
- contact-flow test run: false
- intentional lead/task/customer creation: false

Finance no-contact smoke:

- total tests: 24
- passed: 24
- failed: 0
- no-contact guard confirmed: true
- contact details sent: false
- contact-flow test run: false
- intentional lead/task creation: false

Broader knowledge smoke after study docs:

- total tests: 25
- passed: 25
- failed: 0
- no-contact guard confirmed: true
- contact details sent: false
- contact-flow test run: false
- intentional lead/task creation: false

## Remaining Blockers

- Official content approval remains pending.
- Privacy/data approval and official privacy URL remain pending.
- Final asset upload path remains pending.
- Actual site embed remains pending.
- Real-domain smoke remains pending.
- Public launch approval remains pending.

## Safety Confirmation

- Cloud Run deployed only approved service: `alte-ai-crm-backend`
- Docker image pushed only to approved Artifact Registry: `alte-ai-crm`
- No Cloud SQL schema changes
- No migrations run
- No production seed run
- No Secret Manager changes
- No secrets printed
- Database URL not printed
- No contact-flow test run
- No contact details sent
- No intentional production leads/tasks/customers created
- No live website scraping/crawling
- No real Alte website modified
- No actual asset upload
- No actual site embed
- No Google Cloud resources changed except approved Cloud Run revision/image
- `.env` not committed
- `.local-secrets` not committed
- Bridge Hub untouched
- Public launch not marked complete
- Privacy approval not falsely marked complete
- Content approval not falsely marked complete
