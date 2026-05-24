# Final Preflight Gate

Current decision: `BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY`

Historical gate `NO-GO_FOR_ACTUAL_DEPLOYMENT` is superseded for backend deployment only. Keep full public launch blocked until every remaining website/privacy item below is checked.

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
