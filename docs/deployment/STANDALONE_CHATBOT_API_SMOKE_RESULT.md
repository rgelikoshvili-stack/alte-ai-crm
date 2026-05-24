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
- Next recommendation: treat future medicine/admission smoke as potentially mutating unless a read-only smoke mode is added or an isolated staging backend is used.

## Known Limitations

- Browser local CORS remains blocked by production CORS for `http://127.0.0.1:5500`.
- Real-domain browser smoke from `https://alte.edu.ge` or `https://join.alte.edu.ge` remains pending.
- Official content review remains pending before public launch.
- Production test knowledge seed remains pending approval and was not run.
