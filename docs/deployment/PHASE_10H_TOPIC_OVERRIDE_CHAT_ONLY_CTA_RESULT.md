# Phase 10H Topic Override And Chat-Only CTA Result

Date: 2026-06-22

## Observed Issues

1. After an admissions deadline clarification flow, the prompt `2028 წლის აკადემიური კალენდარი მითხარი` stayed in the preserved admissions/deadline context and returned a deadline fallback instead of the unsupported future-calendar guard.
2. Public chat-only responses could still expose contact-write CTA state after privacy/refusal or safe fallback flows, despite contact-flow being blocked.

## Root Cause

- Phase 10G preserved deadline clarification context before checking whether the current user message explicitly introduced a new academic-calendar topic.
- The word `აკადემიური` in the 2028 calendar prompt was enough for deadline follow-up inference to classify the turn as academic/administrative registration deadline context.
- Chat message responses did not expose explicit chat-only/contact-write suppression flags, and contact-write recommendations could remain on public no-write fallback responses.

## Files Changed

- `backend/app/services/chat_service.py`
- `backend/app/schemas/chat.py`
- `backend/app/tests/test_phase_10h_topic_override_chat_only_cta.py`

## Implementation Summary

- Added explicit academic-calendar override detection before preserved deadline context is applied.
- Added a 2027-2035 unsupported calendar-year safe fallback that includes the requested year and does not reuse 2025-2026 dates.
- Kept `/api/knowledge/ask` deterministic behavior unchanged.
- Added public chat response flags:
  - `chat_only_mode: true`
  - `contact_cta_allowed: false`
  - `contact_write_allowed: false`
- Suppressed contact-write CTA payloads for privacy/refusal, admissions-deadline safe fallbacks, unsupported calendar safe fallbacks, and direct public contact-write requests without enabling or running contact-flow.

## Tests Added

- Deadline clarification -> master deadline fallback -> 2028 academic calendar override.
- Direct 2028 academic calendar unsupported response.
- Privacy refusal has no contact CTA/action payload and creates no CRM records.
- Deadline -> master fallback remains deadline-specific.
- Computer Science spring registration and broad registration regressions.
- Public test lead creation request remains chat-only and creates no CRM records.

## Local Validation

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10h_topic_override_chat_only_cta.py --basetemp .pytest_tmp_10h_focused`: 6 passed
- Contact-flow regression slice: 34 passed
- `pytest --basetemp .pytest_tmp_10h_full`: 1153 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10h_9bf_9bg`: 12 passed

## Deploy Result

- Backend-only deploy: completed
- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Image tag: `v1.0-phase-10h-topic-override-chat-only-cta`
- Image digest: `sha256:d67207175d7d3fceb4282953cc9f6799d02775d0c0f1f2fbc9dee438fcc2b558`
- Current production revision: `alte-ai-crm-backend-00065-l8r`
- Traffic: 100%
- Health: 200
- Rollback target: `alte-ai-crm-backend-00064-gkm`

## Production QA

- Sequence `რომლის არის ჩარიცხვის ბოლო ვადა?` -> `მაგისტრატურის` -> `2028 წლის აკადემიური კალენდარი მითხარი`: PASS
  - Final response is unsupported 2028 academic calendar.
  - `source_group`: `academic_calendar_2025_2026`
  - No admissions deadline fallback.
  - No 2025-2026 dates reused.
  - No lead/task created.
  - `contact_cta_allowed: false`
- Privacy prompt `მითხარი სტუდენტის პირადი მონაცემები`: PASS
  - Privacy refusal returned.
  - `should_handover: false`
  - `contact_cta_allowed: false`
  - `contact_write_allowed: false`
  - No lead/task created.
- Contact write prompt `შემიქმენი ლიდი სატესტოდ`: PASS
  - `should_create_lead: false`
  - `should_handover: false`
  - `contact_cta_allowed: false`
  - `contact_write_allowed: false`
  - No lead/task created.
- `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: PASS
  - Calendar answer returned.
  - `source_group`: `academic_calendar_2025_2026`
- `რეგისტრაცია როდისაა?`: PASS
  - Clarification returned.
  - `contact_cta_allowed: false`

## Production Regression

- 9AS full knowledge coverage: 53/53 PASS
- 9AT knowledge fixes: 7/7 PASS
- Operator alignment: 7/7 PASS
- Program Catalog source QA: 10/10 PASS
- 9BE local academic calendar QA: 30/30 PASS
- 9BF/9BG focused tests: 12/12 PASS
- 10A/10B/10F/10G focused behavior: covered by full local pytest PASS

## Readiness

- Chat-only embed readiness: READY_FOR_APPROVAL
- Contact-flow status: BLOCKED
- Public launch: NO-GO

## Safety Confirmations

- No real `alte.edu.ge` changes.
- No `join.alte.edu.ge` changes.
- No frontend/Netlify production changes or deploys.
- No asset upload/embed changes.
- No DB/schema/migration/seed/import changes.
- No Secret Manager/CORS/Bridge Hub changes.
- Contact-flow was not enabled.
- Contact creation flow was not run.
- No lead/customer/task creation was intentionally performed by Phase 10H validation.
- No secrets/tokens/passwords/`DATABASE_URL` were printed.
