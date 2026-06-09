# Phase 9BF + 9BG Billing-Restored Deploy Retry Checklist

PHASE_9BF_9BG_RETRY_STATUS=PENDING_BILLING_RESTORATION_AND_EXPLICIT_APPROVAL
DECISION_STATE=BACKEND_DEPLOY_BLOCKED_BILLING_PENDING_RETRY
PUBLIC_LAUNCH=NO-GO

## Billing Blocker Summary

- Previous backend deploy attempt did not reach Cloud Run deployment.
- Cloud Build was blocked before upload because project billing was disabled/delinquent.
- Local Docker build passed, but Artifact Registry push was also blocked because billing is required for project `226875230147`.
- This is an infrastructure/billing blocker, not a product QA failure.
- Production QA after deploy was not run because no new backend revision was deployed.

## Current Production State

- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Current production revision: `alte-ai-crm-backend-00052-mjq`
- Current traffic split: `100%` to `alte-ai-crm-backend-00052-mjq`
- Backend deploy status: `NOT_DEPLOYED_BLOCKED_BY_GCP_BILLING`

## Current Branch and Commits

- Branch: `phase-9s-agent-preview-cors-note`
- Phase 9BF/9BG implementation commit: `ece82c6f72d6be4ddec7243b4644b7de75862266`
- Commit readiness commit: `551e9db3c4889817a8b8c7fcf885a064ccd68d56`
- Phase 9BH visual QA commit: `e74e9e0a21ab145d0a49e03c49d4d3bcae2b4bf5`
- Blocked deploy audit commit: `c4ef3d9833e1a341b769ba551da3b8336346aeb0`

## Image Tag to Retry

- Image tag: `v0.9-phase-9bf-9bg-public-source-display`
- Full image name: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9bf-9bg-public-source-display`
- Previous local image digest: `sha256:cc0593511be7d9856da76f5bed787b30151e4d49f44d1b02d8d7f0c16d74bc23`
- Registry digest: not available until billing is restored and image publish succeeds.

## Retry Gate

Do not retry deployment until both conditions are true:

1. GCP billing is restored for project `226875230147` / `project-1e145fd0-c30e-4aac-a34`.
2. Owner explicitly approves the backend deploy retry.

After billing is restored, confirm:

- Cloud Build can upload/build successfully, or the local Docker image can be pushed to Artifact Registry.
- Artifact Registry push works for the requested image tag.
- No permission/auth change is required beyond the existing deployment identity.
- Existing Cloud Run service configuration is preserved.

## Predeploy Checks to Rerun

Run from `C:\tmp\alte-ai-crm\backend`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m compileall app
pytest --basetemp .pytest_tmp_9bf_9bg_billing_retry_predeploy
```

Expected:

- `compileall`: PASS
- Full backend pytest: PASS, expected around `1108 passed`

## Backend-Only Deploy Command Placeholder

Use the same Cloud Run service, project, and region. Preserve the existing DB attachment, Secret Manager mappings, CORS/env vars, and service settings. Do not run migrations, seeds, schema changes, or imports.

Build/publish option:

```powershell
gcloud builds submit .\backend --tag europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9bf-9bg-public-source-display
```

Deploy option after image publish:

```powershell
gcloud run deploy alte-ai-crm-backend `
  --image europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9bf-9bg-public-source-display `
  --region europe-west1 `
  --platform managed `
  --quiet
```

Record after deploy:

- Registry image digest
- Cloud Run revision
- Traffic split
- Deploy command summary without secrets

## Production QA After Successful Deploy

Run production-safe checks only. Do not submit contact forms or real personal data.

- Focused 9AT QA
- Full 9AS QA
- Operator alignment QA
- Program Catalog QA
- Phase 9BF Georgian control repaired questions or safe 40-question QA if available
- Phase 9BG source-display API/static safety

Expected:

- Focused 9AT: `7/7 PASS`
- Full 9AS: `53/53 PASS`
- Operator alignment: `7/7 PASS`
- Program Catalog: `20/20 PASS`
- Phase 9BF Georgian controls: PASS or documented count
- Phase 9BG source-display: PASS
- No internal source IDs
- No raw `used_sources`
- `public_source_label` is source-group/whitelist-derived only
- Unsupported, clarification, handover, wait, and fallback answers have no source label
- No contact flow submitted
- No lead/customer/task created

## Rollback Plan

If the deploy succeeds but production QA fails:

1. Keep previous good revision `alte-ai-crm-backend-00052-mjq` available.
2. Shift traffic back to `alte-ai-crm-backend-00052-mjq`.
3. Document the failing QA scenario, observed revision, and rollback action.
4. Do not mark public launch GO.
5. Public launch remains `NO-GO`.

Rollback command placeholder:

```powershell
gcloud run services update-traffic alte-ai-crm-backend `
  --region europe-west1 `
  --to-revisions alte-ai-crm-backend-00052-mjq=100 `
  --quiet
```

## Safety Confirmations

- Backend-only retry.
- No frontend/Netlify changes.
- No real `alte.edu.ge` / `join.alte.edu.ge` changes.
- No real site upload/embed changes.
- No DB/schema/migration/seed/import changes.
- No Secret Manager changes.
- No CORS changes.
- No Bridge Hub changes.
- No contact-flow submission with real data.
- No lead/customer/task creation.
- Public launch remains `NO-GO`.
