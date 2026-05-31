# Phase 9AP Fix 9AO QA Bugs Result

PHASE_9AP_FIX_STATUS=CODE_READY_PENDING_NETLIFY_REDEPLOY

Decision state:
BACKEND_DEPLOYED_FULL_CHATBOT_FUNCTIONALITY_FIXES_VERIFIED_PENDING_NETLIFY_REDEPLOY

Public launch: NO-GO

## Scope

Phase 9AP fixes the three defects found during Phase 9AO full chatbot functionality QA.

Real Alte site modified: NO

REAL_ALTE_SITE_MODIFIED=NO

Asset upload executed: NO

Real-site embed executed: NO

Production DB modified: NO

Secret Manager modified: NO

CORS changed: NO

Bridge Hub touched: NO

CONTACT_FLOW_EXECUTED=NO

LEAD_TASK_CUSTOMER_CREATED=NO

REAL_CONTACT_DATA_SENT=NO

## Bugs Fixed

### BUG-9AO-KB-01 - Computer Science spring registration fallback

Root cause:

The live backend had approved calendar source evidence for the Computer Science spring semester registration question, but when the AI provider returned a generic service fallback, the source-backed path did not have a deterministic official-answer fallback for this exact academic calendar fact. Routing also scored generic admissions intent too strongly for the Georgian word "registration".

Fix:

- Added academic calendar routing boost for Computer Science + spring semester + registration/start questions.
- Added deterministic official calendar reply guarded by approved-source status.
- Kept the answer source-backed: the deterministic reply is only used after approved knowledge retrieval succeeds.

Expected facts:

- Computer Science spring semester academic/administrative registration: 9-14 March.
- Spring semester start: 30 March.
- Source group: `academic_calendar_2025_2026`.

### BUG-9AO-UI-01 - Medicine / MD label spacing

Root cause:

The frontend department strings did not use the exact expected public QA label.

Fix:

- Changed the KA label to `მედიცინა / MD`.
- Changed the EN label to `Medicine / MD`.
- Updated tests and the existing clarification QA expectation to match the corrected label.

### BUG-9AO-UI-02 - Contact textarea prefill

Root cause:

The handover card contact action preferred the assistant's generic operator text over the latest user question.

Fix:

- Contact form handoff now passes `latestUserText() || m.text`.
- The textarea still falls back to generic operator text when there is no latest user question.
- The textarea remains editable.

## Files Changed

- `backend/app/services/chat_service.py`
- `backend/app/services/knowledge_routing_service.py`
- `backend/app/tests/test_phase_9ai_chatgpt_style_kb_clarification_operator.py`
- `backend/app/tests/test_phase_9ai_knowledge_source_routing_clarification.py`
- `backend/app/tests/test_phase_9ap_fix_9ao_qa_bugs.py`
- `backend/app/scripts/production_phase_9ai_clarification_routing_qa.py`
- `backend/app/scripts/production_phase_9ap_fix_9ao_bugs_qa.py`
- `backend/app/scripts/verify_phase_9ap_fix_9ao_bugs.py`
- `test_site/variants/pro-v2-chat.jsx`
- `test_site/variants/pro-v2-strings.jsx`
- `widget/variants/pro-v2-chat.jsx`
- `widget/variants/pro-v2-strings.jsx`
- `docs/deployment/PHASE_9AP_FIX_9AO_QA_BUGS_RESULT.md`

## Tests Run

Local backend compile:

```text
python -m compileall app
PASSED
```

Focused Phase 9AP tests:

```text
pytest app/tests/test_phase_9ap_fix_9ao_qa_bugs.py -q
6 passed
```

Full backend pytest:

```text
pytest --basetemp .pytest_tmp_9ap_fix_9ao
894 passed
```

Verifier:

```text
python -m app.scripts.verify_phase_9ap_fix_9ao_bugs
PASSED
```

Production focused QA:

```text
python -m app.scripts.production_phase_9ap_fix_9ao_bugs_qa
PASSED
```

Production focused QA result:

```text
16/16 checks passed
Computer Science spring registration: answered_from_approved_source
Source group: academic_calendar_2025_2026
Expected facts present: 9-14 March, 30 March
No generic AI fallback
No CRM records created
No direct contact-data request
Broad clarification sanity check passed
Unsupported no-hallucination sanity check passed
```

Visual QA:

```text
python -m app.scripts.visual_qa_netlify_widget
PENDING_NETLIFY_REDEPLOY
```

## Deployment Status

Backend deploy status:

```text
DEPLOYED
Revision: alte-ai-crm-backend-00035-g2b
Image: v0.9-phase-9ap-fix-9ao-qa-bugs
```

Netlify deploy status:

```text
CODE_READY_PENDING_NETLIFY_REDEPLOY
```

Netlify CLI redeploy attempt:

```text
FAILED_UNAUTHORIZED
```

The test-site redeploy was attempted with Netlify CLI against the existing `nimble-croissant-2f66e8` site, but this machine does not have authorization for that Netlify project. The real Alte site was not touched.

Final upload bundle status:

```text
UNCHANGED_FROM_PHASE_9AM
```

The final upload ZIP was not rebuilt in this phase. The live test-site and widget source copies were fixed, while the owner-approved final upload bundle remains under the existing Phase 9AM approval gate unless a separate bundle rebuild is approved.

## Known Limitations

- `pollOperatorMessages()` currently returns `[]`, so visitor-side live operator replies may not stream back yet.
- Privacy URL remains pending.
- Contact-flow approval remains NOT_APPROVED.
- Dirty working tree reconciliation remains pending for older unrelated files.

## Final Recommendation

Ready for owner approval review: YES, after focused live verification.

Ready for public launch: NO-GO.
