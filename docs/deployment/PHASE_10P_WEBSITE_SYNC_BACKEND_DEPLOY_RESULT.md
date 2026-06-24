# Phase 10P Website Sync Backend Deploy Result

Date: 2026-06-25
Branch: `phase-9s-agent-preview-cors-note`

## Feature Summary

Phase 10P deployed the backend/admin API stack from Phases 10M-10O to the production Cloud Run backend only.

Included backend capabilities:

- Website Sync source configuration APIs
- Website Sync preview/draft APIs
- Website Sync approval/reject APIs
- Website Sync approved content listing
- Website Sync diff/review metadata
- Website Sync archive/rollback behavior
- Approved website retrieval integration for `/api/knowledge/ask` and `/chat/message`
- Draft/public isolation safeguards
- Archived-content retrieval exclusion

This phase did not deploy frontend/Netlify and did not modify the real Alte websites.

## Deploy Image

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Image tag: `v1.0-phase-10p-website-sync-backend`
- Image URL: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v1.0-phase-10p-website-sync-backend`
- Image digest: `sha256:45d2d3e39360bda8a80903cefcb73f12f276fdb0c092469a3a127702a177cfc9`
- Cloud Build ID: `f75593a2-e46a-416a-b292-b6bbb0156ef5`

## Deploy Result

- Previous production revision / rollback target: `alte-ai-crm-backend-00065-l8r`
- New deployed revision: `alte-ai-crm-backend-00071-fig`
- Staged revision tag: `phase10p`
- Tagged revision URL: `https://phase10p---alte-ai-crm-backend-oobzrmikna-ew.a.run.app`
- Tagged revision health before traffic shift: 200
- Container health: Ready / ContainerHealthy
- Final traffic: `alte-ai-crm-backend-00071-fig=100%`
- Production health after traffic shift: 200

## Pre-Deploy Validation

Run from `C:\tmp\alte-ai-crm\backend` with `.\.venv\Scripts\python.exe`.

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10m_website_sync_preview_mvp.py --basetemp .pytest_tmp_10p_10m`: 7 passed
- `pytest app/tests/test_phase_10n_website_sync_approval_publish.py --basetemp .pytest_tmp_10p_10n`: 9 passed
- `pytest app/tests/test_phase_10o_website_sync_admin_review.py --basetemp .pytest_tmp_10p_10o`: 4 passed
- `pytest --basetemp .pytest_tmp_10p_full`: 1173 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10p_9bf_9bg`: 12 passed
- `node --check frontend/app.js`: PASS

## Production QA Results

### Health

- `GET /health`: 200
- Active revision after traffic shift: `alte-ai-crm-backend-00071-fig`
- Traffic: 100%

### Existing Production Regressions

- Production 9AS full knowledge coverage: 53/53 PASS
- Production 9AT knowledge fixes: 7/7 PASS
- Production Operator alignment: 7/7 PASS
- Production Program Catalog source QA: 10/10 PASS
- 9BE local academic calendar QA: 30/30 PASS
- 9BF/9BG focused tests: 12/12 PASS

### Public Chatbot Probes

Safe production public chat probes passed without lead/task creation:

- `რეგისტრაცია როდისაა?`: clarification returned, no contact write
- `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: calendar answer returned
- `2028 წლის აკადემიური კალენდარი მითხარი`: unsupported calendar safe fallback returned, no reused 2025-2026 dates
- `მითხარი სტუდენტის პირადი მონაცემები`: privacy refusal returned
- `შემიქმენი ლიდი სატესტოდ`: no lead/task/customer creation; contact-write flags stayed false

For all public chat probes:

- `should_create_lead=false`
- `created_lead_id=null`
- `created_task_id=null`
- `contact_cta_allowed=false`
- `contact_write_allowed=false`

### Deterministic Knowledge Gateway

`POST /api/knowledge/ask` remained deterministic:

- Computer Science spring registration: `status=answered`, `source_group=academic_calendar_2025_2026`, `used_claude=false`
- 2028 academic calendar: `status=unsupported`, `source_group=academic_calendar_2025_2026`, `used_claude=false`

## Website Sync Endpoint Safety Results

Unauthenticated public requests to Website Sync admin endpoints are blocked:

- `GET /api/knowledge/sync/website/sources`: 401 `Missing bearer token`
- `GET /api/knowledge/sync/website/approved`: 401 `Missing bearer token`
- `POST /api/knowledge/sync/website/sources`: 401 `Missing bearer token`
- `POST /api/knowledge/sync/website/preview` with unapproved external domain payload: 401 before preview execution
- `POST /api/knowledge/sync/website/preview` with `/admin` path payload: 401 before preview execution

No real crawl was executed. No real URL preview was run. No source was added in production. No draft or approved website content was created during production QA.

Local pre-deploy tests continue to cover:

- approved domain acceptance
- unapproved domain rejection
- admin/login/private path rejection
- draft `public_usable=false`
- rejected content not searchable
- archived content not searchable
- approved content priority and clean source labels

## Safety Status

- Real crawl: NO
- Real site changed: NO
- `alte.edu.ge` changed: NO
- `join.alte.edu.ge` changed: NO
- Netlify/frontend production changed: NO
- Assets uploaded/embedded: NO
- Production KB changed/replaced: NO
- DB/schema/migration changed: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub changed: NO
- Contact-flow enabled: NO
- Contact creation flow run: NO
- Lead/customer/task created intentionally: NO
- Real personal data submitted: NO
- Secrets/tokens/passwords/`DATABASE_URL` printed: NO

## Current Readiness

- Chat-only embed readiness: `READY_FOR_APPROVAL`
- Contact-flow status: `BLOCKED`
- Public launch: `NO-GO`

## Rollback Instructions

Rollback target:

- `alte-ai-crm-backend-00065-l8r`

Command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend `
  --region europe-west1 `
  --to-revisions alte-ai-crm-backend-00065-l8r=100 `
  --quiet
```

Post-rollback checks:

- `GET /health` returns 200
- Cloud Run traffic shows `alte-ai-crm-backend-00065-l8r=100%`
- Public chat smoke confirms contact-flow remains blocked

## Decision

`PHASE_10P_WEBSITE_SYNC_BACKEND_DEPLOYED_PUBLIC_LAUNCH_NO_GO`
