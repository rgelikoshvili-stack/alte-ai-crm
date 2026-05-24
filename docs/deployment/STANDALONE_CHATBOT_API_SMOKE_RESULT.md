# Standalone Chatbot API Smoke Result

## Run Metadata

- Date/time: `2026-05-24 13:20:53 +04:00`
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Command: `python -m app.scripts.standalone_chatbot_api_smoke`
- Contact-flow flag used: NO
- Phone/email/contact details sent: NO

## Endpoint Results

- `/health`: PASS, HTTP 200
- `/version`: PASS, HTTP 200
- `/diagnostics/ai`: PASS, HTTP 200
- Diagnostics summary: Claude enabled; no secrets exposed.

## KA / alte.edu.ge Smoke

- Session start for `sourceDomain=alte.edu.ge`, `language=ka`: PASS, HTTP 200
- Message: `გამარჯობა`
  - result: PASS
  - intent: `general_info`
  - confidence: `0.95`
  - handover: `false`
  - created lead/task: none
- Message: `რა ღირს სწავლა?`
  - result: PASS
  - intent: `finance_question`
  - confidence: `0.95`
  - handover: `true`
  - behavior: did not provide an exact invented price; routed to handover behavior
  - created lead/task: none

## EN / join.alte.edu.ge Smoke

- Session start for `sourceDomain=join.alte.edu.ge`, `language=en`: PASS, HTTP 200
- Message: `I want to apply for medicine from India`
  - result: PASS
  - intent: `international_admission`
  - confidence: `0.95`
  - handover: `true`
  - behavior: routed as international/medicine admission interest
  - observed backend side effect: lead/task created by existing business rules

## Lead/Task Creation Policy

- Any leads/tasks intentionally created: NO
- Contact-flow test run: NO
- Contact details submitted: NO
- Observed side effect: the safe medicine/international admissions message triggered existing production business rules and created a lead/task without contact details.
- Phase 8P-Fix status: no-contact lead/task guard applied locally.
- Expected behavior after fix: admission, international, and medicine interest without phone or email asks for contact details and does not create a lead/task.
- Expected behavior with contact after fix: admission, international, and medicine interest with phone or email creates/updates customer, lead, and follow-up task.
- Redeploy required: completed in Phase 8P-Redeploy.
- Next recommendation: continue using the safe standalone smoke without contact-flow before any public website embed.

## Phase 8P-Redeploy Verification

- Image tag deployed: `v0.8-no-contact-guard`
- Cloud Run service: `alte-ai-crm-backend`
- Cloud Run revision: `alte-ai-crm-backend-00003-x84`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- `/health`: PASS, HTTP 200
- `/version`: PASS, HTTP 200
- `/diagnostics/ai`: PASS, HTTP 200; Claude enabled; no secrets exposed.
- Safe standalone API smoke rerun: PASS
- Contact-flow flag used: NO
- Phone/email/contact details sent: NO
- Any leads/tasks intentionally created: NO
- Medicine/international no-contact behavior after redeploy:
  - intent: `international_admission`
  - `should_create_lead=false`
  - `created_lead_id=null`
  - `created_task_id=null`
  - missing fields include `phone_or_email`
- Lead/task side effect fixed: YES

## Known Limitations

- Browser local CORS remains blocked by production CORS for `http://127.0.0.1:5500`.
- Real-domain browser smoke from `https://alte.edu.ge` or `https://join.alte.edu.ge` remains pending.
- Official content review remains pending before public launch.
- Historical Phase 8P note: Production test knowledge seed remains pending approval and was not run during Phase 8P.
- Production test knowledge seed was executed in Phase 8Q after explicit approval.
- Official review of seeded test knowledge remains required before public launch.
