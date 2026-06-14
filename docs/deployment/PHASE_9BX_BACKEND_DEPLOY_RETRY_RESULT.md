# Phase 9BX Backend Deploy Retry Result

Date: 2026-06-14

Branch: `phase-9s-agent-preview-cors-note`

Predeploy commit SHA: `4cafd76b0012f18fcaec4c66fd3cc7c2a76815a1`

Previous production revision: `alte-ai-crm-backend-00052-mjq`

Current production revision: `alte-ai-crm-backend-00053-pbz`

Current traffic: 100% to `alte-ai-crm-backend-00053-pbz`

Public launch: `NO-GO`

## Predeploy Clean Status

Worktree clean before deploy checks: YES

Commands:

- `git status --short --branch`: clean on `phase-9s-agent-preview-cors-note`
- `git rev-parse HEAD`: `4cafd76b0012f18fcaec4c66fd3cc7c2a76815a1`

## Billing / Deploy Permission Status

Billing status: RESTORED

Deploy permission status: AVAILABLE

Non-mutating checks performed:

- Active project/account check: PASS
- Current Cloud Run service describe before deploy: PASS
- Artifact Registry repository describe: PASS

Observed predeploy Cloud Run state:

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Latest ready revision: `alte-ai-crm-backend-00052-mjq`
- Traffic: `alte-ai-crm-backend-00052-mjq=100%`

## Local Validation

Commands run from `C:\tmp\alte-ai-crm\backend` before deploy:

- `.venv\Scripts\python.exe -m compileall app`: PASS
- `.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_9bx_predeploy_full`: PASS, 1108 passed
- `.venv\Scripts\python.exe -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `.venv\Scripts\python.exe -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: PASS, 30/30 calendar QA, 23/23 over-capture, 7/7 fallback over-capture, 4/4 stale-date regression
- `.venv\Scripts\python.exe -m pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9bx_9bf_9bg`: PASS, 12 passed

## Deploy

Deploy attempted: YES

Deploy result: SUCCESS

Build method:

- Cloud Build from `.\backend`

Build ID:

- `ef840cd5-03cb-4b6e-be83-b38531230c14`

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

Deploy command summary:

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

Reason: deploy succeeded and no owner approval was given to rollback. Production QA was blocked by rate limiting/connectivity from the QA client, not completed as a product failure.

## Production QA

Production QA after deploy: BLOCKED / INCONCLUSIVE

Reason:

- Session-based production QA requests returned `429 Rate exceeded` at session start.
- A later `/health` request from the same QA client returned no HTTP status (`000`) after a wait.
- Cloud Run still reported `alte-ai-crm-backend-00053-pbz` as Ready and serving 100% traffic.

Production QA attempts:

- Focused 9AT QA: BLOCKED, session start returned `429 Rate exceeded`
- Full 9AS QA: BLOCKED, session start returned `429 Rate exceeded`
- Health smoke: BLOCKED from QA client, `/health` returned `429` then later no HTTP status after wait
- Operator alignment QA: NOT RUN after rate limiting to avoid more production traffic
- Program Catalog QA: NOT RUN after rate limiting to avoid more production traffic
- 9BE Academic Calendar QA: NOT RUN after rate limiting to avoid more production traffic
- 9BF Georgian controls focused production checks: NOT RUN after rate limiting to avoid more production traffic
- 9BG source display/source-label safety checks: NOT RUN after rate limiting to avoid more production traffic

Required production QA remains pending before any public launch decision:

- Full 9AS QA, expected 53/53
- Focused 9AT QA, expected 7/7
- Operator alignment QA, expected 7/7
- Program Catalog QA, expected 20/20
- 9BE Academic Calendar QA, expected 30/30
- 9BF Georgian controls focused production checks
- 9BG public source display/source-label safety checks

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

Deploy status: `BACKEND_DEPLOYED_PRODUCTION_QA_BLOCKED_BY_RATE_LIMIT_PENDING_QA`

Production unchanged except backend revision: NO, backend is now `alte-ai-crm-backend-00053-pbz`

Public launch: `NO-GO`
