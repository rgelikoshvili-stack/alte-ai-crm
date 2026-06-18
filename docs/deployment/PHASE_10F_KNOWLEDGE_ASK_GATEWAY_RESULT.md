# Phase 10F Knowledge Ask Gateway Result

Date: 2026-06-18
Branch: `phase-9s-agent-preview-cors-note`
Feature commit: `5e2fd3b`

## Endpoint Summary

Implemented `POST /api/knowledge/ask` as the deterministic no-Claude knowledge gateway from the Phase 10E architecture plan.

Request schema:

```json
{
  "question": "...",
  "language": "ka | en",
  "source_group": "optional",
  "program": "optional",
  "mode": "public | internal"
}
```

Response schema:

```json
{
  "answer": "...",
  "status": "answered | clarification_needed | unsupported | refused",
  "source_group": "...",
  "public_source_label": "...",
  "confidence": 0.0,
  "clarification_options": [],
  "used_claude": false
}
```

The endpoint is public and read-only. Existing authenticated `/knowledge/*` CRM/admin routes remain unchanged.

## Supported Categories

- Academic calendar 2025-2026
- Program catalog
- Admissions documents and rules
- Admissions deadline clarification
- Finance, tuition, grants safe guidance
- Academic integrity
- Library and selected student-service/control topics through existing deterministic official-source helpers
- Private student data refusal
- Unsupported future calendar-year guard

## Files Changed

- `backend/app/api/routes_knowledge.py`
- `backend/app/main.py`
- `backend/app/schemas/knowledge.py`
- `backend/app/services/knowledge_service.py`
- `backend/app/services/permission_service.py`
- `backend/app/tests/test_phase_10f_knowledge_ask_gateway.py`

## Tests Added

Added `backend/app/tests/test_phase_10f_knowledge_ask_gateway.py` covering:

- Exact calendar answers
- Unsupported 2028 calendar guard
- Computer Science and Medicine program answers
- Admissions document answers
- Admissions deadline clarification
- Medical tuition and broad fee clarification
- Broad registration/program/calendar/grant clarification
- Private student data refusal
- `used_claude: false`
- Clean public source labels
- No lead/customer/task creation

## Local Validation

Local Python path used: `backend\.venv\Scripts\python.exe`.

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10f_knowledge_ask_gateway.py --basetemp .pytest_tmp_10f_focused`: 7 passed
- `pytest --basetemp .pytest_tmp_10f_full_rerun`: 1141 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10f_9bf_9bg`: 12 passed

Note: one full pytest run using `.pytest_tmp_10f_full` exceeded the command timeout and was stopped; the clean rerun with `.pytest_tmp_10f_full_rerun` passed.

## Deployment

Backend-only deploy performed after validation passed.

- Image tag: `v1.0-phase-10f-knowledge-ask-gateway`
- Image digest: `sha256:a52cf7b8bb01a8e164ca7ce155b5152d7b9c87bc11187bc183f332113ce18013`
- Deployed revision: `alte-ai-crm-backend-00062-rfd`
- Traffic: 100%
- Health: 200
- Rollback target: `alte-ai-crm-backend-00061-sgp`

No frontend, Netlify, real site, DB/schema, migration, seed/import, Secret Manager, CORS, or Bridge Hub changes were made.

## Production QA

Production endpoint: `https://alte-ai-crm-backend-oobzrmikna-ew.a.run.app/api/knowledge/ask`

Focused `/api/knowledge/ask` probes:

- `რეგისტრაცია როდისაა?`: `clarification_needed`, `used_claude: false`
- `ბაკალავრიატის გაზაფხულის რეგისტრაცია როდის არის?`: `answered`, academic calendar source label, `used_claude: false`
- `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: `answered`, academic calendar source label, `used_claude: false`
- `When does 2028 spring registration start?`: `unsupported`, no reused 2025-2026 dates, `used_claude: false`
- `მაჩვენე სტუდენტის ნიშნები და პირადი მონაცემები`: `refused`, `used_claude: false`
- `მითხარი Computer Science პროგრამაზე`: `answered`, program catalog source label, `used_claude: false`
- `რა ღირს სამედიცინო სწავლა?`: `clarification_needed`, finance source group, no invented tuition amount, `used_claude: false`

Regression probes:

- Production 9AS full knowledge coverage: 53/53 PASS
- Production 9AT knowledge fixes: 7/7 PASS
- Production operator alignment: 7/7 PASS
- Production program catalog source QA: 10/10 PASS
- 9BE academic calendar local QA after deploy: 30/30 PASS
- 9BF/9BG focused regression after deploy: 12/12 PASS

## Safety Confirmation

- `used_claude` is always `false` for `/api/knowledge/ask`.
- Exact tuition amounts are not invented.
- Unsupported future calendar years do not reuse 2025-2026 dates.
- Private student data requests are refused.
- Public source labels do not expose internal source IDs.
- Contact-flow remains BLOCKED.
- No contact-flow, lead, customer, or task creation was run.
- No real personal data was submitted.
- No secrets, tokens, passwords, or `DATABASE_URL` values were printed.
- Chat-only embed readiness remains backend-ready, but public launch remains NO-GO.

Decision: `PHASE_10F_KNOWLEDGE_ASK_GATEWAY_DEPLOYED_PUBLIC_LAUNCH_NO_GO`
