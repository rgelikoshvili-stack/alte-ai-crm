# Phase 9AS Full Knowledge Coverage QA Result

PHASE_9AS_FULL_KNOWLEDGE_QA_STATUS=PASSED

Test time UTC: 2026-06-22T17:01:59.000105+00:00
Backend URL: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
Netlify Origin: https://nimble-croissant-2f66e8.netlify.app
Dataset: `backend\app\data\evaluation\phase_9as_full_knowledge_qa.json`
Operator API auth: AUTH_OK

## Summary

- Total questions: 53
- Passed: 53
- Failed: 0
- Skipped: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO
- Public launch: NO-GO

## Per-Category Results

| Category | Total | Passed | Failed |
| --- | ---: | ---: | ---: |
| academic_calendar | 9 | 9 | 0 |
| admissions | 6 | 6 | 0 |
| clarification | 6 | 6 | 0 |
| official_academic_facts | 17 | 17 | 0 |
| operator_handover | 5 | 5 | 0 |
| routing | 6 | 6 | 0 |
| unsupported | 4 | 4 | 0 |

## Failures

- None

## Checks Covered

- Source-backed correctness
- Expected source group
- Department/routing
- Clarification behavior
- Unsupported no-hallucination fallback
- Handover expectation
- Operator `human_handover` state when API auth is available
- No lead/task/customer creation
- No direct phone/email/name request in chat answer
- No Georgian mojibake

## Final Recommendation

No critical knowledge/routing failures were found in this run.
