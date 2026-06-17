# Phase 9AA Selected 45 Docs Routing Deploy Result

PHASE_9AA_SELECTED_45_DOCS_ROUTING_DEPLOY_STATUS=DEPLOYED_AND_SMOKE_PASSED

Decision state:
BACKEND_DEPLOYED_SELECTED_45_DOCS_SOURCE_BACKED_QA_PASSED_PENDING_BROADER_BROWSER_QA

## Scope

- Source branch: `phase-9s-agent-preview-cors-note`
- Source commit: `f79386d`
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Public backend URL verified: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Latest ready revision after traffic update: `alte-ai-crm-backend-00022-c5n`
- Traffic: `100%` to latest revision

## Build And Deploy

- First build ID: `b12aacf4-ec96-4844-8039-707f0c90394a`
- First image tag: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9aa-selected-docs-routing`
- First image digest: `sha256:37722d12f3615ff1634c6188f7d1446b7817ef230f20bb43df5a50b93fa18594`
- No-cache build ID: `63725985-4438-4699-9a9a-bb0d0486f608`
- No-cache image tag: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9aa-selected-docs-routing-nocache`
- No-cache image digest: `sha256:e4cf63a289d191d3a068cf4ef2b5584b667ef159f652e2d4619e98716f49a6db`

Note: Cloud Run initially kept traffic on the previous named revision. Traffic was explicitly moved to the latest ready revision with no env, secret, CORS, DB, migration, or schema changes.

## Production Smoke Result

All smoke tests used `/chat/session/start` and `/chat/message` only. Output was sanitized; no passwords, tokens, hashes, or database URLs were printed.

| Topic | HTTP | Source status | Used sources | Lead created | Task created | Result |
| --- | ---: | --- | ---: | --- | --- | --- |
| AI policy | 200 | `answered_from_approved_source` | 10 | no | no | PASS |
| Ombudsman | 200 | `answered_from_approved_source` | 10 | no | no | PASS |
| Library | 200 | `answered_from_approved_source` | 10 | no | no | PASS |
| Plagiarism | 200 | `answered_from_approved_source` | 10 | no | no | PASS |
| Career service | 200 | `answered_from_approved_source` | 10 | no | no | PASS |
| Program catalog | 200 | `answered_from_approved_source` | 10 | no | no | PASS |

## Safety Confirmation

- No production migration was run.
- No production seed was run.
- No DB schema change was made.
- No Secret Manager change was made.
- No CORS change was made.
- No real `alte.edu.ge` or `join.alte.edu.ge` site change was made.
- No contact-flow test was run.
- No lead, task, or customer was intentionally created by the informational smoke tests.
- `.env` and `.local-secrets` were not committed.
- Public launch remains NO-GO.

## Follow-Up

The selected 45 documentation package is now source-backed in production for the tested policy, student service, academic integrity, library, career service, and program catalog questions. Broader browser QA can continue, but public launch is not complete.
