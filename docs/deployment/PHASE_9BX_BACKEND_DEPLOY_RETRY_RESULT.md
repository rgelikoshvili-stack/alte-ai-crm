# Phase 9BX Backend Deploy Retry Result

Date: 2026-06-15

Branch: `phase-9s-agent-preview-cors-note`

Predeploy commit SHA for this retry: `23d83267888ae685f8f670c699b4cf4725e4a89c`

Previous production revision before Phase 9BX deploy: `alte-ai-crm-backend-00052-mjq`

Active production revision during this retry: `alte-ai-crm-backend-00053-pbz`

Current traffic: 100% to `alte-ai-crm-backend-00053-pbz`

Public launch: `NO-GO`

## Predeploy Clean Status

Worktree clean before deploy checks: YES

Commands:

- `git status --short --branch`: clean on `phase-9s-agent-preview-cors-note`
- `git rev-parse HEAD`: `23d83267888ae685f8f670c699b4cf4725e4a89c`

## Billing / Deploy Permission Status

Billing status: RESTORED

Deploy permission status: AVAILABLE

Observed Cloud Run state at retry start:

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Latest ready revision: `alte-ai-crm-backend-00053-pbz`
- Traffic: `alte-ai-crm-backend-00053-pbz=100%`

The queued image was already deployed and serving 100% traffic when this retry started, so no redundant rebuild or redeploy was executed during this retry.

## Local Validation

Commands run from `C:\tmp\alte-ai-crm\backend` during this retry:

- `.venv\Scripts\python.exe -m compileall app`: PASS
- `.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_9bx_retry_predeploy_full`: PASS, 1108 passed
- `.venv\Scripts\python.exe -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `.venv\Scripts\python.exe -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: PASS, 30/30 calendar QA, 23/23 over-capture, 7/7 fallback over-capture, 4/4 stale-date regression
- `.venv\Scripts\python.exe -m pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9bx_retry_9bf_9bg`: PASS, 12 passed

## Deploy

Deploy attempted during this retry: NO

Reason: the requested queued image tag was already deployed to Cloud Run and serving 100% traffic as revision `alte-ai-crm-backend-00053-pbz`.

Prior Phase 9BX deploy result retained:

- Deploy attempted: YES
- Deploy result: SUCCESS
- Build method: Cloud Build from `.\backend`
- Build ID: `ef840cd5-03cb-4b6e-be83-b38531230c14`

Image tag:

- `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9bf-9bg-9be-clean-hygiene`

Image digest:

- `sha256:d6f2ee8940e63086b7641e1ecc634de667aa34405c549f346a46e2af594fcb84`

Cloud Run revision:

- `alte-ai-crm-backend-00053-pbz`

Traffic allocation:

- `alte-ai-crm-backend-00053-pbz=100%`

Service URL:

- `https://alte-ai-crm-backend-oobzrmikna-ew.a.run.app`

Deploy command summary from the prior Phase 9BX deploy:

```powershell
gcloud builds submit .\backend --tag europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9bf-9bg-9be-clean-hygiene
gcloud run deploy alte-ai-crm-backend --image europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9bf-9bg-9be-clean-hygiene --region europe-west1 --platform managed --quiet
```

No deploy command printed or changed secrets.

## Rollback

Rollback readiness: READY

Rollback target:

- `alte-ai-crm-backend-00052-mjq`

Rollback command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions alte-ai-crm-backend-00052-mjq=100 --quiet
```

Rollback executed: NO

Reason: no owner approval was given to rollback. Production QA now has one full 9AS failure and public launch remains blocked.

## Production QA

Production health smoke:

- `/health`: PASS, HTTP 200

Production QA after active deployment:

- Focused 9AT QA: PASS, 7/7
- Full 9AS QA: FAILED, 52/53
- Operator alignment QA: PASS, 7/7
- Program Catalog source QA: PASS, 10/10 using available production script `production_phase_9ay_program_catalog_source_qa`; no 20-question production script was present in the current tree
- 9BE Academic Calendar QA: local verifier and 30/30 local QA PASS; full 9AS production failed one academic-calendar case
- 9BF Georgian controls focused checks: local focused tests PASS, 12-test combined 9BF/9BG suite; no dedicated production 9BF script was present in the current tree
- 9BG source display/source-label safety checks: local focused tests PASS, 12-test combined 9BF/9BG suite; no dedicated production 9BG script was present in the current tree

Full 9AS failure detail:

- Failed case: `calendar_bachelor_spring_registration_ka`
- Category: `academic_calendar`
- Summary: production answered with the spring semester start date instead of a registration answer.
- Result: 52 passed, 1 failed.

Production QA safety:

- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO
- Public launch: NO-GO

## Current Production State

Cloud Run service:

- `alte-ai-crm-backend`

Region:

- `europe-west1`

Current production revision:

- `alte-ai-crm-backend-00053-pbz`

Current traffic:

- `alte-ai-crm-backend-00053-pbz=100%`

Previous revision retained for rollback:

- `alte-ai-crm-backend-00052-mjq`

## Safety Confirmations

- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS changed: NO
- Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Sensitive local-hold contents exposed: NO
- Public launch marked GO: NO

## Final State

Deploy status: `BACKEND_DEPLOYED_PRODUCTION_9AS_FAILED_PENDING_FIX_OR_ROLLBACK_DECISION`

Production revision: `alte-ai-crm-backend-00053-pbz`

Public launch: `NO-GO`
