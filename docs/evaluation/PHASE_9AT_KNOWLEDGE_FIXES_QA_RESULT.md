# Phase 9AT Knowledge Fixes Production QA Result

PHASE_9AT_PRODUCTION_QA_STATUS=FAILED

Test time UTC: 2026-05-31T15:09:28.475963+00:00
Backend URL: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
Operator API auth: AUTH_OK

## Summary

- Total: 7
- Passed: 2
- Failed: 5
- CONTACT_FLOW_EXECUTED=NO
- REAL_CONTACT_DATA_SENT=NO
- LEAD_TASK_CUSTOMER_CREATED=NO
- Public launch: NO-GO

## Failures

- `cs_calendar`: department
- `master_documents`: department
- `fake_tuition`: source_status, handover, must_include
- `it_emis`: source_status, operator_handover
- `career_empty_source`: source_status, department
