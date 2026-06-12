# Phase 9BE Academic Calendar Fixes Result

PHASE_9BE_STATUS=CODE_READY_PENDING_REVIEW

Decision state: `BACKEND_CODE_ACADEMIC_CALENDAR_QA_FIXES_READY_PENDING_REVIEW`

Public launch: `NO-GO`

## Baseline

- Phase 9BD Academic Calendar GEO/ENG: 30 total
- 9BD PASS: 4
- 9BD PARTIAL: 3
- 9BD FAIL: 23

## Root Cause Summary

- `wrong_source_program_catalog`: calendar/date questions were sometimes routed to Program Catalog because program-level terms won before date/calendar intent.
- `missing_calendar_priority`: date/time wording needed stronger calendar priority.
- `generic_answer_generation`: fallback calendar answers omitted exact source dates.
- `clarification_missing`: broad calendar questions defaulted to a program group instead of asking a clarification.
- `future_year_unsupported_failure`: 2027 calendar questions reused 2025-2026 dates.
- `program_group_confusion`: "except Computer Science", one-cycle, master, and first-year one-cycle English cases needed explicit group detection.
- `stale_expectation`: one-cycle spring final end date needed the full source row ending 1 August.

## Fixes Made

- Added calendar/date priority in `claude_intent_router_service.py` before Program Catalog routing.
- Added matching calendar priority in `knowledge_routing_service.py`.
- Fixed the medium review over-capture finding: bare `registration` is no longer treated as a calendar/date marker by itself.
- Added admissions, requirements, documents, procedure, rules, and policy exclusions so non-date registration policy questions stay out of Academic Calendar routing.
- Fixed the final review substring over-capture finding: English date/time markers now use word-boundary matching, so `updated`, `candidate`, `outdated`, `mandate`, `update`, and `validate` do not match `date`.
- Preserved Georgian substring/stem matching for Georgian calendar markers.
- Fixed the remaining Computer Science spring shortcut over-capture: CS spring registration/semester shortcuts now require the stricter calendar date/time predicate and no longer route requirements/documents questions to Academic Calendar.
- Fixed the final chat-service helper substring finding: the deterministic CS spring helper now uses word-boundary matching for English date/time markers, so `updated`, `candidate`, and `outdated` do not trigger direct deterministic calendar replies.
- Fixed the grounded source-backed fallback over-capture: `grounded_source_backed_reply()` no longer uses broad `is_calendar_text()` as standalone permission to return calendar dates, and `admissions_rules` is protected from calendar fallback for non-date registration requirements/documents questions.
- Fixed the stale Bachelor registration fallback: broad Bachelor registration prompts now return the approved 2025-2026 fall and spring registration rows instead of the old 8-13 September / 15-20 September fallback dates.
- Added deterministic Academic Calendar 2025-2026 exact-date answer mapping in `chat_service.py`.
- Added broad calendar clarification handling for exam, registration, and semester-start questions.
- Added a future year guard for calendar questions outside 2025-2026.
- Preserved Program Catalog routing for non-calendar program list/language/credit questions.

## Review Finding Follow-up

- Review finding: `registration` plus a program level could over-capture admissions/requirements questions into `academic_calendar_2025_2026`.
- Fix: Academic Calendar priority now requires explicit calendar context or real date/time wording plus a calendar-like event.
- Final review finding: bare English `date` matched inside non-date words such as `updated` and `candidate`.
- Final fix: English calendar/date markers are matched with regex word boundaries; Georgian markers continue using stem matching.
- Remaining review finding: a Computer Science spring registration shortcut bypassed the stricter predicate for requirements/documents questions.
- Remaining fix: the forced-source shortcut was removed, the knowledge-routing CS spring scorer is gated by `is_academic_calendar_priority_question()`, and the deterministic CS spring registration helper now requires date/time wording.
- Final helper finding: direct `chat_service.py` helper matching still treated `date` inside `updated`, `candidate`, and `outdated` as a date/time signal for CS spring semester registration requirements.
- Final helper fix: `chat_service.py` now uses local word-boundary matching for English date/time markers; direct deterministic helper probes are covered in focused tests and local QA.
- Final grounded fallback finding: `grounded_source_backed_reply()` could return Academic Calendar dates for admissions requirements/documents prompts when called with `source_group=admissions_rules`.
- Final grounded fallback fix: calendar fallback is now allowed only for `academic_calendar_2025_2026` or the strict academic-calendar priority predicate; `admissions_rules` is handled before text-only calendar fallback.
- Final stale Bachelor registration finding: broad Bachelor registration date prompts fell through to an older fallback and returned stale dates.
- Final stale Bachelor registration fix: broad Bachelor registration prompts return fall administrative registration 15-20 September 2025, fall academic registration 22-27 September 2025, spring administrative registration 23-28 February 2026, and spring academic registration 2-7 March 2026, plus a Computer Science separate-date note.
- Rule preserved: `When is bachelor registration?` and `ბაკალავრზე რეგისტრაცია როდის არის?` route to the calendar.
- Rule preserved: `What date does bachelor registration start?` and `What are the registration dates for Computer Science?` route to the calendar.
- Rule preserved: `When is Computer Science spring registration?`, `What date is Computer Science spring registration?`, and Georgian CS spring registration/start questions route to the calendar.
- Rule added: `What are updated registration requirements for bachelor admission?`, `What are candidate registration requirements for bachelor admission?`, `What are outdated registration requirements for bachelor admission?`, `What are the registration requirements for bachelor admission?`, `What documents are required for bachelor registration?`, CS spring requirements/documents questions, direct CS spring semester helper substring probes, and Georgian equivalents do not route to the calendar or trigger deterministic calendar replies.
- Over-capture regression: 23 PASS / 0 FAIL.
- Fallback over-capture regression: 7 PASS / 0 FAIL.
- Stale-date regression: 4 PASS / 0 FAIL.

## Local QA

- Local QA result: 30 PASS / 0 PARTIAL / 0 FAIL
- Over-capture regression result: 23 PASS / 0 FAIL
- Fallback over-capture regression result: 7 PASS / 0 FAIL
- Stale-date regression result: 4 PASS / 0 FAIL
- Root cause groups after local QA: none
- Safety checks: no lead/customer/task; no contact flow; public launch NO-GO

## Verification

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_9be_academic_calendar_fixes.py --basetemp .pytest_tmp_9be_chat_helper_fix_focused`: PASS, 12 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30 PASS / 0 PARTIAL / 0 FAIL; over-capture 23 PASS / 0 FAIL; fallback over-capture 7 PASS / 0 FAIL; stale-date 4 PASS / 0 FAIL
- Full backend pytest after chat helper fix: PASS, 1111 passed

## Expected Production Result

After review and an explicitly approved future backend deploy, Academic Calendar GEO/ENG file QA is expected to improve from 4 PASS / 3 PARTIAL / 23 FAIL to 30 PASS / 0 PARTIAL / 0 FAIL.

## Deploy Status

- Deploy status: NOT_DEPLOYED
- Commit made: NO
- Public launch remains: NO-GO

## Safety Checks

- Real site modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB schema/migration/seed/import changed or run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Contact flow submitted: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- Public launch remains: NO-GO
