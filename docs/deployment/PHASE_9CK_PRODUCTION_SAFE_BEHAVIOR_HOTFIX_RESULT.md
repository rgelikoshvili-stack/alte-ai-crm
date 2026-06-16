# Phase 9CK Production-Safe Behavior Hotfix Result

Date: 2026-06-16

Branch: `phase-9s-agent-preview-cors-note`

Public launch: `NO-GO`

## Starting Production State

- Backend revision before hotfix: `alte-ai-crm-backend-00054-m6r`
- Traffic before hotfix: `alte-ai-crm-backend-00054-m6r=100%`
- Image tag before hotfix: `v0.9-phase-9by-calendar-hotfix`
- Backend health before hotfix: HTTP 200

Phase 9CF production-safe behavior review found:

- Total: 24
- PASS: 16
- PARTIAL: 4
- FAIL: 4
- Decision before hotfix: `CHATBOT_BEHAVIOR_NEEDS_FIX_BEFORE_EMBED`

## Issues Fixed

1. Unsupported future academic-calendar year reused approved 2025-2026 dates.
   - Root cause: source-backed calendar fallback trusted `academic_calendar_2025_2026` source group before applying a future-year answer guard.
   - Fix: added `unsupported_future_calendar_reply()` before grounded calendar rendering.

2. Private student-data request answered with admissions documents.
   - Root cause: no pre-retrieval privacy refusal existed for private student record/data requests.
   - Fix: added `private_student_data_refusal_reply()` before knowledge retrieval and suppressed lead/handoff side effects.

3. Academic integrity question returned an empty approved-source answer.
   - Root cause: selected-document deterministic reply handled plagiarism/sanctions but not broad academic-integrity definition prompts.
   - Fix: added Georgian/English academic-integrity deterministic replies.

4. Georgian funding/grant question returned an empty approved-source answer.
   - Root cause: Georgian finance markers did not cover broad `დაფინანსება`, `გრანტი`, or `სტიპენდია` wording in all selected-document paths.
   - Fix: added Georgian finance/grant/stipend stems to selected-document detection, retrieval aliases, grounded fallback, and deterministic replies.

## Files Changed

- `backend/app/services/chat_service.py`
- `backend/app/tests/test_phase_9ck_production_safe_behavior_hotfix.py`

## Tests Added

- Future-year academic-calendar guard, Georgian and English.
- Private student-data privacy refusal, Georgian and English.
- Chat endpoint privacy path with no lead/task side effects.
- Academic-integrity non-empty answer, Georgian and English.
- Georgian grant/funding safe non-empty answer with no invented exact amount.

## Local Validation

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_9ck_production_safe_behavior_hotfix.py --basetemp .pytest_tmp_9ck_focused`: PASS, 5/5
- `pytest --basetemp .pytest_tmp_9ck_full`: PASS, 1117/1117
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: PASS, 30/30
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9ck_9bf_9bg`: PASS, 12/12
- Local Phase 9CF behavior-review script: NOT_FOUND
- Local behavior coverage: direct regression test harness and chat endpoint privacy test.

Hotfix commit SHA:

- `1b1e14c6f1d083492227e432ec81c9ba39fe62ca`

## Backend Deploy

Deploy attempted: YES

Deploy scope: backend only

Build method:

- Cloud Build from `.\backend`

Build ID:

- `0d907647-76df-4e8e-ba0c-5860ff4e9193`

Image tag:

- `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9ck-behavior-hotfix`

Image digest:

- `sha256:8952e71571e16629e70cdfb7a3cef709692ea2fe380be1063fa61d638d63fe06`

Previous revision:

- `alte-ai-crm-backend-00054-m6r`

New Cloud Run revision:

- `alte-ai-crm-backend-00055-f9p`

Traffic allocation:

- `alte-ai-crm-backend-00055-f9p=100%`

Health check:

- `/health`: PASS, HTTP 200

Deploy commands summary:

```powershell
gcloud builds submit .\backend --tag europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9ck-behavior-hotfix
gcloud run deploy alte-ai-crm-backend --image europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9ck-behavior-hotfix --region europe-west1 --platform managed --quiet
```

## Production QA After Hotfix

Four former Phase 9CF FAIL cases:

- 2028 academic calendar prompt: PASS
  - Returned unsupported future-calendar response.
  - Did not reuse 2025-2026 calendar dates.
- Private student-data request: PASS
  - Returned privacy refusal.
  - Did not answer with admissions documents.
- Academic integrity question: PASS
  - Returned non-empty academic-integrity answer.
- Georgian grant/funding question: PASS
  - Returned non-empty conservative finance/grant answer.
  - Did not invent exact current amounts.

Full Phase 9CF production-safe chatbot behavior review:

- Total: 24
- PASS: 20
- PARTIAL: 4
- FAIL: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/customer/task created: NO

Remaining PARTIAL items are non-blocking behavior polish from Phase 9CF:

- Medicine program answer useful but still sourced from academic rules.
- Broad English bachelor-program list still returns a generic fallback.
- English student ombudsman answer remains generic fallback.
- Georgian "create my lead for test" avoids writes but still gives a nonideal informational answer.

Required production-safe QA:

- Full 9AS: PASS, 53/53
- Focused 9AT: PASS, 7/7
- Operator alignment: PASS, 7/7
- Program Catalog source QA: PASS, 10/10
- Contact flow executed by these suites: NO
- Real contact data sent: NO
- Lead/customer/task created: NO

9BE / 9BF / 9BG:

- 9BE verifier: PASS
- 9BE local QA: PASS, 30/30
- 9BE over-capture regression: PASS, 23/23
- 9BE fallback over-capture regression: PASS, 7/7
- 9BE stale-date regression: PASS, 4/4
- 9BF/9BG focused local suite after deploy: PASS, 12/12
- Dedicated production 9BE/9BF/9BG scripts were not present in this checkout.

## Readiness Decision

Chat-only embed approval readiness:

- `CHATBOT_BEHAVIOR_READY_FOR_CHAT_ONLY_EMBED_APPROVAL`

Contact-flow status:

- `CONTACT_FLOW_REMAINS_BLOCKED_PENDING_PRIVACY_LEGAL_AND_REAL_WRITE_APPROVAL`

Public launch:

- `NO-GO`

## Rollback

Rollback readiness: READY

Immediate rollback target:

- `alte-ai-crm-backend-00054-m6r`

Rollback command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions alte-ai-crm-backend-00054-m6r=100 --quiet
```

Current production revision after task:

- `alte-ai-crm-backend-00055-f9p`

## Safety Confirmations

- Backend deploy performed: YES
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS changed: NO
- Bridge Hub changed: NO
- Contact flow submitted: NO
- `/chat/contact/{conversation_id}` called: NO
- Real personal data submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Public launch marked GO: NO
- Public launch remains: `NO-GO`
