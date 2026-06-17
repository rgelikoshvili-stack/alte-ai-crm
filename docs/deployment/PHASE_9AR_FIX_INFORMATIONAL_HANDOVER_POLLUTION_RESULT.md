# Phase 9AR Fix Informational Handover Pollution Result

PHASE_9AR_FIX_STATUS=PASSED_PENDING_APPROVALS

Decision state:
BACKEND_DEPLOYED_CHATBOT_OPERATOR_ALIGNMENT_FIX_VERIFIED_PENDING_APPROVALS

Public launch: NO-GO

## Scope

Phase 9AR fixed BUG-9AQ-ALIGN-01 from the chatbot to Operator CRM alignment QA.

The goal was to stop normal source-backed informational answers from entering the Operator CRM handover lane while preserving handover behavior for unsupported answers, explicit operator requests, contact handoff, and wait-for-operator.

## Bug Summary

Question:

```text
რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?
```

Before Phase 9AR:

- Answer was correct and source-backed.
- Answer included 240 ECTS.
- Chat response had `should_handover=true`.
- Operator CRM showed `human_handover=true`.
- Operator CRM selected department showed `Study Process`.
- No lead/customer/task was created.

After Phase 9AR:

- Answer is still source-backed.
- Answer still includes 240 ECTS.
- Chat response has `should_handover=false`.
- Operator CRM shows `human_handover=false`.
- Operator CRM selected department shows `Programs`.
- No lead/customer/task is created.

## Root Cause

Two backend policy issues caused the pollution:

1. Department routing treated sensitive/source-backed academic topics as `handover_required`, and `apply_department_routing()` converted that directly into `analysis.should_handover=True`.
2. ECTS degree-completion questions matched both `study_process` and `programs`; the department priority chose the internal `Study Process` label before the public `Programs` label.

## Fix

Backend behavior changed as follows:

- Source-backed informational answers now clear `should_handover` unless the visitor explicitly asks for operator/contact/human routing.
- No-approved-source answers that offer operator fallback still persist handover metadata.
- Explicit operator/contact requests still persist handover metadata.
- Wait-for-operator still sets `waiting_for_operator` and `human_handover=true`.
- Degree-credit completion questions now route to the public `Programs` department instead of internal `Study Process`.
- Response `handover_reason` is only returned when `should_handover=true`.

## Files Changed

- `backend/app/services/chat_service.py`
- `backend/app/services/department_routing_service.py`
- `backend/app/tests/test_phase_9ar_fix_informational_handover_pollution.py`
- `backend/app/scripts/production_phase_9ar_fix_informational_handover_qa.py`
- `backend/app/scripts/verify_phase_9ar_fix_informational_handover.py`
- `backend/app/tests/test_phase_9ar_fix_informational_handover_result.py`
- `docs/deployment/PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_RESULT.md`

## Tests Run

Local compile:

```text
python -m compileall app
PASSED
```

Focused Phase 9AR tests:

```text
pytest app/tests/test_phase_9ar_fix_informational_handover_pollution.py -q
8 passed
```

Full backend pytest:

```text
pytest --basetemp .pytest_tmp_9ar_handover_pollution
916 passed
```

Production-safe Phase 9AR QA:

```text
python -m app.scripts.production_phase_9ar_fix_informational_handover_qa
36/36 passed
```

Phase 9AQ alignment rerun:

```text
python -m app.scripts.production_phase_9aq_chat_operator_alignment_qa
116/116 passed
```

## Production Deployment

Backend deploy status:

```text
DEPLOYED
Revision: alte-ai-crm-backend-00037-7xh
Image: v0.9-phase-9ar-informational-handover-fix
```

No migrations or seed were run.

Cloud Run was updated only to deploy the tested backend image.

## Production QA Result

Phase 9AR production-safe QA:

```text
PHASE_9AR_PRODUCTION_QA_STATUS=PASSED
Checks: 36
Passed: 36
Failed: 0
Operator API auth/checks: AUTH_OK
```

Verified:

- Bachelor ECTS answer contains 240.
- Bachelor ECTS answer is source-backed.
- Bachelor ECTS `should_handover=false`.
- Operator CRM Bachelor ECTS `human_handover=false`.
- Operator CRM Bachelor ECTS selected department is `Programs`.
- Master ECTS answer contains 120 and `should_handover=false`.
- Clarification response has `should_handover=false`.
- Unsupported no-source answer still has operator fallback and `should_handover=true`.
- Explicit operator request still has `should_handover=true`.
- Wait-for-operator still sets `waiting_for_operator` and `human_handover=true`.
- No lead/customer/task was created by informational or wait flows.

## Operator CRM Verification

Operator CRM API verification passed.

For the Bachelor ECTS conversation:

```text
conversation_status=open
human_handover=false
selected_department=Programs
waiting_status=null
has_customer=false
has_lead=false
message_count=2
```

For wait-for-operator:

```text
conversation_status=waiting_for_operator
human_handover=true
waiting_status=waiting_for_operator
has_customer=false
has_lead=false
```

## Safety

- Real Alte site modified: NO
- REAL_ALTE_SITE_MODIFIED=NO
- Asset upload executed: NO
- Real-site embed executed: NO
- Production DB schema changed: NO
- Production DB migration run: NO
- Production seed run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- CONTACT_FLOW_EXECUTED=NO
- REAL_CONTACT_DATA_SENT=NO
- LEAD_TASK_CUSTOMER_CREATED=NO

## Known Limitation

VISITOR_SIDE_OPERATOR_REPLY_POLLING=NOT_ACTIVE

Operator CRM can send replies to the backend, but this phase does not prove replies appear back in the visitor widget. This limitation remains documented and was not changed in Phase 9AR.

## Final Recommendation

Phase 9AR fix status: PASSED_PENDING_APPROVALS

The original Phase 9AQ alignment bug is fixed and verified in production.

Ready for public launch: NO-GO

Remaining blockers:

- Official Privacy URL
- Contact-flow approval
- Asset upload approval
- Staged real-site embed approval
- Real-domain smoke
- Dirty tree reconciliation
- Final public launch approval
