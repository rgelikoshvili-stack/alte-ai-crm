# Phase 9BY Production 9AS Calendar Hotfix Result

Date: 2026-06-15

Branch: `phase-9s-agent-preview-cors-note`

Public launch: `NO-GO`

## Original Production Failure

- Production revision with failure: `alte-ai-crm-backend-00053-pbz`
- Full 9AS result before hotfix: 52/53
- Failed case: `calendar_bachelor_spring_registration_ka`
- Category: `academic_calendar`
- Issue: Georgian Bachelor spring registration prompt returned the spring semester start date instead of registration dates.

Failure reproduced locally before the hotfix: YES

Local reproduced answer before fix:

- Returned only spring semester start: `9 March 2026`

## Root Cause

`deterministic_academic_calendar_reply()` handled Bachelor spring registration only when the prompt explicitly specified academic or administrative registration. The failed Georgian prompt included both registration wording and the start marker `იწყება`, so the later Bachelor spring semester-start branch won and returned `9 March 2026`.

## Hotfix

Files changed:

- `backend/app/services/chat_service.py`
- `backend/app/tests/test_phase_9be_academic_calendar_fixes.py`

Code change:

- Added a narrow Bachelor spring registration branch before the Bachelor spring semester-start branch.
- Generic Bachelor spring registration now returns both approved registration rows:
  - Spring administrative registration: `23 - 28 February 2026`
  - Spring academic registration: `2 - 7 March 2026`
- Bachelor spring semester-start prompts still return `9 March 2026`.
- Georgian registration requirements/documents prompts remain admissions-safe and do not return calendar dates.

Hotfix commit SHA:

- `b9716e78d8c7bffb199da89b301f2ce38fe7eb27`

## Local Validation

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_9be_academic_calendar_fixes.py --basetemp .pytest_tmp_9by_9be`: PASS, 21/21
- `pytest app/tests/test_phase_9as_full_knowledge_operator_verification.py --basetemp .pytest_tmp_9by_9as_focused`: PASS, 7/7
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: PASS, 30/30
- `pytest --basetemp .pytest_tmp_9by_full`: PASS, 1112/1112

## Backend Deploy

Deploy attempted: YES

Deploy scope: backend only

Build method:

- Cloud Build from `.\backend`

Build ID:

- `13f245a8-2a20-4abe-9ea3-8a14f5805030`

Image tag:

- `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9by-calendar-hotfix`

Image digest:

- `sha256:b456378796a91c2ca2140935affbcdc0bd7edabc18b3a694e8a25761e9234fb3`

Previous revision:

- `alte-ai-crm-backend-00053-pbz`

New Cloud Run revision:

- `alte-ai-crm-backend-00054-m6r`

Traffic allocation:

- `alte-ai-crm-backend-00054-m6r=100%`

Health check:

- `/health`: PASS, HTTP 200

Deploy commands summary:

```powershell
gcloud builds submit .\backend --tag europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9by-calendar-hotfix
gcloud run deploy alte-ai-crm-backend --image europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9by-calendar-hotfix --region europe-west1 --platform managed --quiet
```

## Production QA After Hotfix

Failed single case:

- `calendar_bachelor_spring_registration_ka`: PASS
- Reply included `23 - 28 February 2026` and `2 - 7 March 2026`
- Reply did not answer only `9 March 2026`

Full 9AS:

- PASS, 53/53
- Academic calendar category: 9/9
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

Focused 9AT:

- PASS, 7/7
- Contact flow executed: NO
- Lead/task/customer created: NO

Operator alignment:

- PASS, 7/7
- Contact flow executed: NO
- Lead/task/customer created: NO

Program Catalog:

- PASS, 10/10 using available production script `production_phase_9ay_program_catalog_source_qa`
- A 20-question production Program Catalog script was not present in this checkout.

9BE Academic Calendar:

- Closest production coverage: full 9AS academic-calendar category PASS, 9/9
- Local 9BE verifier: PASS
- Local 9BE QA: PASS, 30/30
- Dedicated production 9BE 30-question script was not present in this checkout.

9BF / 9BG:

- Local focused 9BF/9BG suite after deploy: PASS, 12/12
- Dedicated production 9BF/9BG scripts were not present in this checkout.

## Rollback

Rollback readiness: READY

Rollback target:

- `alte-ai-crm-backend-00053-pbz`

Prior rollback target retained:

- `alte-ai-crm-backend-00052-mjq`

Rollback command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions alte-ai-crm-backend-00053-pbz=100 --quiet
```

Rollback executed: NO

Reason: hotfix deploy and production QA passed; no owner approval was given to rollback.

## Current Production State

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Current production revision: `alte-ai-crm-backend-00054-m6r`
- Current traffic: `alte-ai-crm-backend-00054-m6r=100%`

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

Deploy status: `BACKEND_DEPLOYED_9BY_CALENDAR_HOTFIX_VERIFIED_PUBLIC_LAUNCH_NO_GO`

Full 9AS status: PASS, 53/53

Public launch: `NO-GO`
