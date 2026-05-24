# Production Test Knowledge Seed Result

## Run Metadata

- Date/time: `2026-05-24 14:12:01 +04:00`
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Seed file: `backend/app/knowledge_seed/alte_required_test_knowledge_v1.json`
- Seed command used: `python -m app.scripts.seed_required_test_knowledge --allow-production`
- Verification command: `python -m app.scripts.verify_required_test_knowledge_seed`
- Safe smoke command: `python -m app.scripts.standalone_chatbot_api_smoke`

## First Seed Run Summary

- `sources_created`: 12
- `snippets_created`: 13
- `skipped_existing`: 0
- `review_required_count`: 11
- `warnings`: none

## Second Seed Run / Idempotency Summary

- `sources_created`: 0
- `snippets_created`: 0
- `skipped_existing`: 13
- `review_required_count`: 11
- `warnings`: none
- Idempotency result: PASS. Re-running the seed did not duplicate snippets.

## Verification Script Result

- Required test knowledge verification: PASS
- `general_contact`: PASS
- `admissions_general`: PASS
- `finance`: PASS
- `international_admissions`: PASS
- `medicine_md`: PASS
- `deadlines`: PASS
- Uncertain content remains review-required or approved: PASS

## Safe API Smoke After Seed

- `/health`: PASS
- `/version`: PASS
- `/diagnostics/ai`: PASS
- KA greeting: PASS
- KA finance exact price question: PASS; did not create lead/task and did not intentionally submit contact details.
- KA deadline question: PASS; did not create lead/task and requested contact details before any admissions lead action.
- EN medicine/international no-contact question: PASS; `should_create_lead=false`, `created_lead_id=null`, `created_task_id=null`, missing fields include `phone_or_email`.
- Contact-flow test run: NO
- Phone/email/contact details sent: NO
- Any leads/tasks intentionally created: NO

## Safety Confirmation

- Production test knowledge seed run only after explicit approval.
- No contact-flow test was run.
- No intentional production lead/task creation was performed.
- No secrets were printed.
- Exact tuition/deadline behavior remains conservative and does not invent final official facts.

## Known Limitations

- Official content review is still required before public launch.
- Real Alte site embed remains pending.
- Real-domain browser smoke remains pending.
- The seeded content is suitable for controlled testing, not final public official answers until reviewed.
