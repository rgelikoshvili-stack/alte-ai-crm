# Phase 9AS Full Knowledge And Operator Verification Result

PHASE_9AS_FULL_VERIFICATION_STATUS=FAILED_PENDING_FIXES

Decision state:
BACKEND_DEPLOYED_FULL_KNOWLEDGE_OPERATOR_QA_FAILED_PENDING_FIXES

Public launch: NO-GO

## Scope

Phase 9AS verifies that the production chatbot uses the loaded approved knowledge base, asks clarifying questions for broad prompts, avoids unsupported hallucination, routes department/operator cases correctly, and reflects conversation/routing/handover state in Operator CRM.

## Tested Targets

- Backend revision: alte-ai-crm-backend-00037-7xh
- Production backend: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
- Netlify chatbot: https://nimble-croissant-2f66e8.netlify.app/join.html
- Operator CRM URL: http://127.0.0.1:5173

## Evidence Paths

- Active knowledge inventory: `docs/evaluation/PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md`
- QA dataset: `backend/app/data/evaluation/phase_9as_full_knowledge_qa.json`
- Full knowledge QA report: `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md`
- Operator alignment QA report: `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md`
- Visual QA script: `backend/app/scripts/visual_qa_netlify_widget.py`

## Initial Expected Coverage

- Official academic rules
- Academic calendar 2025-2026
- Admissions rules
- Student status and mobility
- Exams and assessment
- Finance operator fallback where approved source is missing
- Library operator fallback where approved source is missing
- IT operator fallback where approved source is missing
- Career operator fallback where approved source is missing
- International admissions routing/source availability

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
- Public launch: NO-GO

## Current Run Summary

Phase 9AS production QA was executed against the live Cloud Run backend using the Netlify Origin.

Full knowledge coverage QA:

```text
Status: FAILED
Total questions: 53
Passed: 11
Failed: 42
Skipped: 0
Operator API auth/checks: AUTH_OK
```

Per-category result:

| Category | Total | Passed | Failed |
| --- | ---: | ---: | ---: |
| official_academic_facts | 17 | 6 | 11 |
| academic_calendar | 9 | 0 | 9 |
| admissions | 6 | 0 | 6 |
| clarification | 6 | 4 | 2 |
| routing | 6 | 0 | 6 |
| unsupported | 4 | 1 | 3 |
| operator_handover | 5 | 0 | 5 |

Operator CRM alignment QA:

```text
Status: FAILED
Scenarios: 7
Passed: 6
Failed: 1
Operator API auth/checks: AUTH_OK
```

Visual QA:

```text
Status: PASSED
Desktop: PASS
Mobile: PASS
Georgian rendering: PASS
No horizontal scroll: PASS
Clarification UI: PASS
Contact textarea visible: PASS
Wait-for-operator visible: PASS
```

Backend tests:

```text
compileall app: PASS
pytest --basetemp .pytest_tmp_9as_full_knowledge: 932 passed
```

## Answerable Knowledge Areas Verified

Verified as working in this run:

- Bachelor ECTS: 240 ECTS, source-backed, no handover pollution.
- Master ECTS: 120 ECTS, source-backed, no handover pollution.
- Student status suspension: maximum 5 years, source-backed.
- Several broad clarification prompts still ask clarification.
- The unsupported space-campus scholarship prompt did not invent the requested scholarship.

## Gaps And Bugs Found

### BUG-9AS-KB-01: Many approved-source questions return AI-service fallback text

Several source-backed questions returned generic AI-service fallback text such as temporary AI unavailability while still attaching approved source titles. This means retrieval may find an approved source, but the user-facing answer is not reliably synthesized into a useful official answer for many topics.

Affected categories include:

- Medicine/Dentistry program facts
- Mobility/internal mobility
- Credit recognition
- GPA
- FX/F
- Final exam admission
- Retake/make-up exams
- Academic calendar questions
- Admissions document questions

Recommendation: add deterministic/source-grounded answer builders or improve source-backed answer synthesis for these official areas before launch.

### BUG-9AS-KB-02: Academic calendar routing/source mapping is incomplete

All 9 academic calendar tests failed. Some calendar prompts routed to Programs, Admissions, General / Operator, or `admissions_rules` instead of consistently using `academic_calendar_2025_2026`.

Recommendation: strengthen calendar keyword routing and source-group selection for registration, semester start, finals, midterms, retakes, and holidays.

### BUG-9AS-KB-03: Admissions routing/source mapping is incomplete

All 6 admissions tests failed under the full coverage expectations. Several admissions/document questions routed to Programs or General / Operator, or returned fallback text instead of clear admissions-source answers.

Recommendation: improve admissions source-group selection and deterministic answer extraction for bachelor/master documents, admission without exams, foreign applicants, and recognition of foreign education.

### BUG-9AS-ROUTE-01: IT/EMIS fallback does not persist Operator CRM human handover

Operator CRM alignment passed 6 of 7 scenarios. The remaining failure:

```text
it_operator_fallback: human_handover_expected
```

The IT/EMIS conversation is visible, but the Operator CRM `human_handover` state was not set as expected for that fallback route.

Recommendation: fix IT no-approved-source fallback so it persists the same handover metadata as other unsupported/operator fallback flows.

### BUG-9AS-UNSUPPORTED-01: Some unsupported prompts matched unrelated approved sources

Some unsupported/empty-source prompts, especially unsupported tuition-like prompts, matched unrelated approved academic/admissions snippets instead of returning no approved source and finance/operator fallback.

Recommendation: tighten source relevance checks for unsupported finance/library/IT prompts and prevent unrelated approved-source snippets from satisfying unsupported questions.

## Routing Results

- Bachelor and Master ECTS routing remained aligned with Programs and did not pollute handover.
- Calendar routing is not consistently aligned to `academic_calendar_2025_2026`.
- Admissions routing is not consistently aligned to `admissions_rules`.
- Finance/Library/IT/Career empty-source routes need stricter operator fallback behavior.
- Operator CRM alignment is mostly correct, but IT fallback handover metadata is incomplete.

## Handover Results

- Informational Bachelor/Master answers are excluded from the handover queue.
- Explicit operator requests work in the focused Operator CRM alignment QA.
- Wait-for-operator works in the focused Operator CRM alignment QA.
- Unsupported/no-source fallback works for the space-campus scholarship test.
- IT/EMIS fallback handover metadata is incomplete in Operator CRM.

## Contact Textarea Result

Visual QA confirms the contact form and question/message textarea are visible. Contact flow was not submitted because contact-flow approval remains NOT_APPROVED.

## Hallucination Result

The main unsupported space-campus scholarship test did not hallucinate. However, some unsupported prompts matched unrelated approved source snippets, so unsupported relevance filtering still needs work before public launch.

## Lead/Task/Customer Creation Result

No lead, task, or customer was intentionally created by the Phase 9AS QA scripts.

## Bugs Found

- BUG-9AS-KB-01: source-backed fallback text instead of useful official answers in multiple official topics.
- BUG-9AS-KB-02: academic calendar routing/source-group failures.
- BUG-9AS-KB-03: admissions routing/source-group failures.
- BUG-9AS-ROUTE-01: IT/EMIS fallback does not persist Operator CRM `human_handover=true`.
- BUG-9AS-UNSUPPORTED-01: unsupported prompts can match unrelated approved source snippets.

## Known Limitation

VISITOR_SIDE_OPERATOR_REPLY_POLLING=NOT_ACTIVE

Operator CRM can receive and store conversation state, but visitor-side polling for live operator replies remains documented as not active unless a later phase verifies otherwise.

## Final Recommendation

Phase 9AS status: FAILED_PENDING_FIXES

Public launch remains: NO-GO

Recommended next phase:

Phase 9AT - Fix knowledge coverage routing, source relevance, and IT fallback handover metadata, then rerun Phase 9AS focused QA.
