# Production Knowledge Smoke After Study Docs Result

Date/time: `2026-05-24 19:35 Asia/Tbilisi`

Production backend URL:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Phase 8V Import Summary

- `sources_created=11`
- `snippets_created=11`
- `high_sensitivity_records=5`
- `review_required_records=8`

## Endpoint Health

- `/health`: `200`, status `ok`, version `0.8.0`
- `/version`: `200`, service `alte-ai-crm`, version `0.8.0`
- `/diagnostics/ai`: `200`, provider `claude`, Claude enabled, no secrets exposed

## Smoke Test Cases

KA / `alte.edu.ge`:

1. `რა პროგრამები აქვს ალტე უნივერსიტეტს?`
2. `როგორ ხდება ჩარიცხვა?`
3. `რა საბუთებია საჭირო ჩარიცხვისთვის?`
4. `რა ღირს სწავლა?`
5. `როდის არის მიღების ბოლო ვადა?`
6. `სად მდებარეობს ალტე უნივერსიტეტი?`
7. `მინდა ადამიანთან საუბარი`

EN / `join.alte.edu.ge`:

8. `I want to apply for medicine from India`
9. `What documents do international students need?`
10. `How much is tuition for medicine?`
11. `When is the admission deadline?`
12. `Can you help me with visa and relocation?`

## Summary

- Total assertions: `23`
- Passed: `22`
- Failed: `1`
- Original status: `PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_STATUS=FAILED_NEEDS_REVIEW`, resolved by Phase 8Y-Redeploy

Failure:

- Test: `no lead/task side effect: tuition`
- Response summary: `intent=finance_question`, `confidence=0.95`, `answer_source_status=answered_from_approved_source`, `should_handover=true`, `should_create_lead=true`, `created_lead_id=null`, `created_task_id=null`, `missing_fields=["first_name","phone","email","specific_program"]`
- Interpretation: the backend did not create lead/task IDs, but it still returned `should_create_lead=true` without contact details. This was fixed and verified in Phase 8Y-Redeploy.

## Behavior Notes

- Tuition/finance behavior: conservative on exact price; no invented exact tuition was detected.
- Deadline behavior: conservative on exact deadline; no invented exact deadline was detected.
- Documents behavior: routed carefully / requested official confirmation or handover.
- International admissions behavior: routed carefully and did not create a lead/task ID.
- Medicine/MD behavior: routed carefully and did not create a lead/task ID.
- Visa/relocation behavior: routed carefully and did not provide legal certainty.
- No-contact guard behavior: partially failed because one tuition response returned `should_create_lead=true` without contact details, although no lead/task ID was created.

## Safety Confirmation

- Contact-flow test run: `false`
- Contact details sent: `false`
- Intentional production leads/tasks/customers created: `false`
- Production seed run: `false`
- Migration run: `false`
- Direct DB admin changes: `false`
- Cloud Run deploy: `false`
- Docker image push: `false`
- `gcloud` commands: `false`
- Secrets printed: `false`
- Real Alte site modified: `false`

The smoke test used production chat endpoints, so normal conversation/message persistence may occur by backend design. No CRM lead/task/customer creation was intentional and no lead/task IDs were returned by the failed case.

## Remaining Blockers

- Official reviewer decisions pending
- Official content approval pending
- Privacy/data approval pending
- Final widget asset URL pending
- Actual site embed pending
- Real-domain browser smoke pending
- Tuition no-contact `should_create_lead=true` behavior resolved by Phase 8Y-Redeploy

Original decision state, now superseded:

```text
BACKEND_DEPLOYED_STUDY_DOCS_KB_SMOKE_FAILED_NEEDS_REVIEW
```

## Phase 8Y Follow-Up

The tuition/finance no-contact lead bug from this smoke result has been fixed in the service layer and deployed to Cloud Run.

- finance/tuition/scholarship/deadline questions without phone/email now force `should_create_lead=false`
- no customer/lead/task is created for no-contact finance information requests
- sensitive finance content remains review-required and conservative
- production redeploy completed with image tag `v0.8-finance-no-contact-guard`

Superseded decision state:

```text
BACKEND_CODE_FIXED_FINANCE_NO_CONTACT_GUARD_PENDING_REDEPLOY
```

## Phase 8Y-Redeploy Resolution

The finance no-contact guard fix has now been deployed to Cloud Run.

- Image tag: `v0.8-finance-no-contact-guard`
- New revision: `alte-ai-crm-backend-00004-gsn`
- Finance no-contact smoke after redeploy: `24 passed`, `0 failed`
- Broader production knowledge smoke after redeploy: `25 passed`, `0 failed`
- Contact-flow test: not run
- Contact details sent: no
- Intentional production lead/task/customer creation: no
- Finance/tuition/scholarship/deadline no-contact responses now return `should_create_lead=false` with no created IDs.

Updated decision state:

```text
BACKEND_DEPLOYED_FINANCE_NO_CONTACT_GUARD_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```
