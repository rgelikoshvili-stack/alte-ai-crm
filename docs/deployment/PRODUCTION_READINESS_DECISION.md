# Production Readiness Decision

Current decision: `NO-GO_FOR_ACTUAL_DEPLOYMENT`

Reason: the repository is deployment-prepared and project/region/CORS/billing/repo URL are recorded, but Cloud SQL cost confirmation, Secret Manager values, release tag, GitHub push backup, and website access confirmation are not all recorded yet.

## Go Only If

- [x] GitHub remote exists. Current remote: `https://github.com/rgelikoshvili-stack/alte-ai-crm`.
- [ ] Release tag exists. Current check: no local tag found.
- [x] Tests pass. Latest Phase 8D-Prep check: `106 passed` with `AI_PROVIDER=mock`.
- [ ] Docker build passes. Not run in this prep step.
- [ ] `startup_check` passes with production-like env. Local/dev check passed; production-like Secret Manager values are not configured yet.
- [x] Google Cloud project selected. `PROJECT_ID=project-1e145fd0-c30e-4aac-a34`.
- [x] Billing understood. User confirmed billing is enabled.
- [ ] Cloud SQL cost accepted.
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
- Confirm GitHub push backup and release tag.
- Confirm Alte website admin/developer access.
- Confirm data privacy approval.

## No-Go If

- [ ] Real secrets are in Git, docs, chat, or screenshots. Current docs scan passed; do not paste new secrets.
- [ ] `.env` is tracked. Current release verification says `.env` is not tracked.
- [ ] Tests fail.
- [ ] Claude live test fails.
- [ ] Cloud SQL is not planned.
- [ ] CORS uses wildcard.
- [ ] No rollback plan exists.
