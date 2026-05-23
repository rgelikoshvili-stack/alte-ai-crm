# Production Readiness Decision

Current decision: `NO-GO_FOR_ACTUAL_DEPLOYMENT`

Reason: GitHub backup/tag, deployment docs, Claude live validation, Docker/Cloud Run docs, project/region/CORS and billing are recorded. Cloud SQL tier/cost draft is prepared but not approved. Actual deployment remains blocked until Cloud SQL tier/cost approval, Secret Manager values, website access and privacy approval are completed.

## Go Only If

- [x] GitHub remote exists. Current remote: `https://github.com/rgelikoshvili-stack/alte-ai-crm`.
- [x] Release tag exists. `v0.8-deployment-ready` was pushed.
- [x] Tests pass. Latest Phase 8D-GitHub check: `110 passed` with `AI_PROVIDER=mock`.
- [ ] Docker build passes. Not run in this prep step.
- [ ] `startup_check` passes with production-like env. Local/dev check passed; production-like Secret Manager values are not configured yet.
- [x] Google Cloud project selected. `PROJECT_ID=project-1e145fd0-c30e-4aac-a34`.
- [x] Billing understood. User confirmed billing is enabled.
- [ ] Cloud SQL cost accepted. Recommended option: Low-cost pilot production tier. Cost/financial approval still pending.
- [ ] Anthropic key created and stored in Secret Manager.
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
- Cloud SQL cost approval form prepared; status remains `PENDING_USER_APPROVAL`.
- Cloud SQL tier/cost draft prepared, but not approved.
- Recommended Cloud SQL option: Low-cost pilot production tier.
- Secret Manager values runbook prepared.
- Secret preparation checklist prepared.
- Production env mapping reviewed.
- Production migration/seed runbook prepared.
- Website/privacy approval checklist prepared.
- Phase 8F execution plan prepared for later explicit approval.
- Cloud SQL creation still blocked until explicit user approval.
- Secret Manager creation still blocked until explicit user approval.

## No-Go If

- [ ] Real secrets are in Git, docs, chat, or screenshots. Current docs scan passed; do not paste new secrets.
- [ ] `.env` is tracked. Current release verification says `.env` is not tracked.
- [ ] Tests fail.
- [ ] Claude live test fails.
- [ ] Cloud SQL is not planned.
- [ ] CORS uses wildcard.
- [ ] No rollback plan exists.
