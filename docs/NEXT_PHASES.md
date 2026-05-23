# Next Phases

## Phase 8B: Real Claude Live Validation

- Requires a real Anthropic API key configured locally.
- Run `GET /diagnostics/ai`.
- Run `python -m app.scripts.ai_direct_dry_run`.
- Run `python -m app.scripts.claude_live_smoke`.
- Verify `ai_interactions.provider = claude`.
- Confirm customer, lead, task, conversation, and message side effects are still created by CRM services, not by Claude directly.

## Phase 8C: Production Deployment Preparation

Status: prepared in repository; no real Google Cloud deployment yet.

- Dockerfile review.
- Cloud Run configuration.
- Cloud SQL configuration.
- Secret Manager mapping.
- Production CORS.
- Health and diagnostics checks.
- No real deployment until explicit approval.

## Phase 8D: Actual Cloud Run Deployment

Pre-deployment planning package:

- `docs/deployment/DEPLOYMENT_VARIABLES.template.md`
- `docs/deployment/GOOGLE_CLOUD_PREFLIGHT.md`
- `docs/deployment/COMMAND_PLAN_GCLOUD.md`
- `docs/deployment/DEPLOYMENT_RISK_REGISTER.md`
- `docs/deployment/PRODUCTION_READINESS_DECISION.md`
- `docs/deployment/GITHUB_BACKUP_AND_RELEASE.md`
- `docs/deployment/FINAL_PREFLIGHT_GATE.md`

- Create/confirm Google Cloud project resources.
- Build and push backend image.
- Configure Cloud Run, Cloud SQL, and Secret Manager.
- Run migrations and approved seed.
- Verify production health and diagnostics.

## Phase 8D-Final-Preflight: GitHub Backup And Deployment Gate

- Verify GitHub remote.
- Push backup only after approval.
- Create `v0.8-deployment-ready` tag only after approval.
- Run `python -m app.scripts.verify_final_preflight`.
- Keep `NO-GO_FOR_ACTUAL_DEPLOYMENT` until all blockers are cleared.

Preconditions before actual deployment:

- Cloud SQL tier/cost accepted.
- Secret Manager values created without exposing secrets.
- GitHub pushed and tagged.
- Website access confirmed.
- Privacy approval confirmed.

## Phase 8E: Staging Website Widget Embed

Before staging embed, Phase 8E infrastructure gate must be closed:

- Cloud SQL tier/cost decision.
- Secret values runbook.
- Production env mapping.
- Production migration/seed runbook.
- Website and privacy approval checklist.

Next possible phase: Phase 8F - Actual Secret Manager and Cloud SQL creation.

Only after:

- Cloud SQL cost/tier approved.
- Privacy approval owner confirmed.
- Website access confirmed or accepted as pending for backend-only deployment.

## Phase 8F-Prep: Cloud SQL Cost Approval And Secret Execution Checklist

- Cloud SQL cost approval form.
- Secret preparation checklist.
- Phase 8F execution plan.
- Pre-execution verifier.
- No cloud resource creation.

Next possible phase: Phase 8F-Execution - Actual Secret Manager and Cloud SQL creation.

Only after:

- Cloud SQL pilot tier approved.
- Next recommended phase: Phase 8F-Secrets-Prep - prepare secret values locally and document Secret Manager creation approval.
- Secret values prepared locally and not exposed.
- User explicitly approves resource creation.

## Phase 8F-Secrets-Prep: Secret Values Preparation Gate

- Secret values preparation worksheet.
- Secret Manager approval gate.
- `DATABASE_URL` construction guide.
- Local guidance-only helper script.
- Secret preparation verifier.
- No Secret Manager creation.
- No Cloud SQL creation.
- No Google Cloud resource creation.

Secret Manager creation is approved for the next execution phase, but no secrets have been created.

Next recommended phase: Phase 8F-Execution-Prep - confirm actual secret values are ready locally and prepare interactive `gcloud` steps without printing values.

Actual Secret Manager creation requires the exact approval phrase:

`Approve Phase 8F-Execution for Secret Manager creation`

Next possible phase after that approval: Phase 8F-Execution - Secret Manager and Cloud SQL resource creation.

## Phase 8F-Secret-Values-Local-Prep: Local Secret Generation Readiness

- `.gitignore` excludes `.local-secrets/` and local secret file patterns.
- Local preparation guide: `LOCAL_SECRET_VALUES_PREP.md`.
- Local helper script: `scripts/prepare_local_secret_values.ps1`.
- Local verifier: `python -m app.scripts.verify_local_secret_values_prep`.
- No real secrets are committed.
- `DATABASE_URL` remains pending until Cloud SQL exists.

Next step for Secret Manager execution:

- User prepares DB password and JWT secret locally.
- User confirms Anthropic key readiness without sharing the value.
- User approves the exact Secret Manager execution phase.

## Phase 8F-Secret-Manager-Execution: Secret Container Creation

- Secret Manager API enabled.
- Secret containers created:
  - `alte-db-password`
  - `alte-jwt-secret`
  - `alte-anthropic-api-key`
  - `alte-database-url`
- Secret payload versions are pending because local secret files were not present.
- `alte-database-url` version remains pending until Cloud SQL exists.
- No Cloud SQL, Cloud Run, Docker image, or deployment was created.

Next recommended phase:

- Prepare local secret files and add Secret Manager versions, or create Cloud SQL first if DATABASE_URL is required.
- Keep `NO-GO_FOR_ACTUAL_DEPLOYMENT` until Cloud SQL, DATABASE_URL, website access, privacy/data approval, and deployment approval are complete.

## Phase 8F-Secret-Versions-Execution: Secret Versions Added

- `alte-db-password` version added.
- `alte-jwt-secret` version added.
- `alte-anthropic-api-key` version added.
- `alte-database-url` version remains pending until Cloud SQL exists.
- No secret payloads were printed.
- No Cloud SQL, Cloud Run, Docker image, or deployment was created.

Next recommended phase:

- Phase 8G-Cloud-SQL-Prep or Phase 8G-Cloud-SQL-Execution after explicit approval.
- Build final `DATABASE_URL` only after Cloud SQL exists.

## Phase 8G-Execution: Cloud SQL Pilot Database

- Initial Enterprise Plus/default attempt with `db-f1-micro` failed and was stopped safely.
- Corrected approach used Cloud SQL Enterprise edition with low-cost/shared-core pilot tier.
- Instance status: `CLOUD_SQL_INSTANCE_CREATED`
- Instance: `alte-ai-crm-db`
- Region: `europe-west1`
- Tier: `db-f1-micro`
- Database status: `DATABASE_CREATED`
- Database: `alte_ai_crm`
- App user status: `DB_USER_CREATED`
- App user: `alte_app`
- `alte-database-url` secret version: `VERSION_ADDED`
- Cloud Run was not deployed.
- Docker image was not pushed.

Next recommended phase:

- Phase 8H: production migration/seed planning or execution after explicit approval.
- Keep `NO-GO_FOR_ACTUAL_DEPLOYMENT` until migrations, seed, Cloud Run deployment, website access, privacy/data approval, and deployment approval are complete.

Only after:

- Secret Manager creation is explicitly approved.
- Secret values are generated locally and not exposed.
- Website/privacy blockers are accepted or deferred for backend-only deployment.
- User explicitly approves actual resource creation.

- Backend public URL.
- Widget public URL.
- CORS for `https://alte.edu.ge` and `https://join.alte.edu.ge`.
- Script snippet.
- Privacy/consent text review.
- Staging test page.

## Phase 9: Omnichannel Planning

- Meta Developers account.
- WhatsApp Business API.
- Messenger.
- Instagram.
- Email.
- SMS.

No omnichannel implementation before the website chat flow is stable.

## Phase 10: Advanced CRM

- Agent module.
- Bulk messaging approval.
- Calendar integration.
- SLA automation.
- Advanced analytics.
