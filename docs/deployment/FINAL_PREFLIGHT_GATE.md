# Final Preflight Gate

Current decision: `NO-GO_FOR_ACTUAL_DEPLOYMENT`

Keep `NO-GO` until every required item below is checked.

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
| Google Cloud | Cloud SQL instance created | Not yet; requires approval |
| Google Cloud | Secret Manager values created | Not yet; requires approval |
| Google Cloud | Secret Manager creation | Blocked until explicit user approval |
| Google Cloud | Secret values runbook | Done: `SECRET_VALUES_RUNBOOK.md`; statuses `NOT_CREATED / PENDING` |
| Google Cloud | Secret preparation checklist | Done: `SECRET_PREPARATION_CHECKLIST.md`; values not created |
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
| Application | `AI_PROVIDER=mock` for tests | Required |
| Application | `AI_PROVIDER=claude` for production | Planned |
| Website | `alte.edu.ge` CORS confirmed | Done |
| Website | `join.alte.edu.ge` CORS confirmed | Done |
| Website | Website developer/admin access | Pending |
| Website | Privacy/consent text approval | Pending |
| Website | Website/privacy checklist | Done: `WEBSITE_AND_PRIVACY_APPROVAL.md`; statuses pending |
| Execution | Phase 8F execution plan | Done: `PHASE_8F_EXECUTION_PLAN.md`; do not run until approved |

## Decision

Do not proceed to actual Cloud Run deployment until:

- GitHub backup is pushed and tagged.
- Cloud SQL tier/cost is accepted.
- Cloud SQL cost/tier approval is explicitly confirmed by user/billing owner.
- Secret Manager values are created without exposing secrets.
- Alte website access is confirmed.
- Data privacy approval is confirmed.
