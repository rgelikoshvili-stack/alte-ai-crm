# Phase 10D Deadline and Tuition Routing Result

Date: 2026-06-18
Branch: `phase-9s-agent-preview-cors-note`

## Observed Issues

1. Admissions deadline prompts such as `რომლის არის ჩარიცხვის ბოლო ვადა?` returned generic admissions document text instead of asking which deadline was meant.
2. Medical tuition prompts such as `რა ღირს სამედიცინო სწავლა?` returned Medicine / MD program description and 360 ECTS instead of recognizing fee/tuition intent.

## Root Causes

- Admissions deadline wording was routed to `admissions_rules` but had no deadline-specific ambiguity clarification.
- Georgian tuition markers such as `რა ღირს` and `საფასური` were too weak when paired with Medicine/medical program markers.
- Medicine/MD program markers could override fee intent and route to program/academic-rule descriptions.

## Files Changed

- `backend/app/services/claude_intent_router_service.py`
- `backend/app/services/knowledge_routing_service.py`
- `backend/app/tests/test_phase_10d_deadline_tuition_routing.py`

Feature commit: `99f6d78`

## Tests Added

- Admissions deadline clarification route and chat response tests.
- English application/admission deadline clarification tests.
- Medical tuition Georgian and English clarification tests.
- Guards against generic admissions-doc-only answers, 360 ECTS/program-description-only answers, invented dates, and invented tuition amounts.
- Regression checks for Medicine program info, Bachelor admissions documents, Bachelor spring registration, academic-registration deadline routing, and clean source labels.

## Local Validation

- `python -m compileall app`: PASS
- `pytest --basetemp .pytest_tmp_10d_full`: PASS, `1134 passed`
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: PASS, `30/30`
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10d_9bf_9bg`: PASS, `12/12`
- `python -m app.scripts.local_phase_10a_production_safe_behavior_review`: PASS, `14/14`
- `pytest app/tests/test_phase_10a_clarifying_router_validator.py app/tests/test_phase_10b_topic_switch_source_display.py app/tests/test_phase_10d_deadline_tuition_routing.py --basetemp .pytest_tmp_10d_10a_10b`: PASS, `17/17`

## Deploy Result

- Backend-only deploy performed.
- No frontend, Netlify, real-site, DB/schema, Secret Manager, CORS, or Bridge Hub changes were made.
- Image tag: `v1.0-phase-10d-deadline-tuition-routing`
- Image digest: `sha256:3096bf2e3294a75b541525080f7f8c19cbf69ecd69589a14ccd4a64c179b07f6`
- Previous revision / rollback target: `alte-ai-crm-backend-00060-zm6`
- Current production revision: `alte-ai-crm-backend-00061-sgp`
- Traffic: `100%`
- Health: `/health` returned `200`

Note: local Google Cloud CLI token refresh required a temporary local SSL-validation workaround because the workstation certificate chain could not be verified by gcloud. The temporary gcloud settings were unset after deployment.

## Production QA

Deadline prompts:

- `რომლის არის ჩარიცხვის ბოლო ვადა?`: PASS, `clarification_needed`, no source label, no lead/task.
- `ჩარიცხვის ბოლო ვადა როდისაა?`: PASS, `clarification_needed`, no source label, no lead/task.
- `როდის მთავრდება მიღება?`: PASS, `clarification_needed`, no source label, no lead/task.
- `What is the application deadline?`: PASS, `clarification_needed`, no source label, no lead/task.

Medical tuition prompts:

- `რა ღირს სამედიცინო სწავლა?`: PASS, `clarification_needed`, no 360 ECTS answer, no invented amount, no source label, no lead/task.
- `მედიცინის სწავლა რა ღირს?`: PASS, `clarification_needed`, no 360 ECTS answer, no invented amount, no source label, no lead/task.
- `მედიცინის პროგრამის საფასური რამდენია?`: PASS, `clarification_needed`, no 360 ECTS answer, no invented amount, no source label, no lead/task.
- `What is the Medicine tuition fee?`: PASS, `clarification_needed`, no invented amount, no source label, no lead/task.

Regression results:

- 9AS full knowledge coverage: PASS, `53/53`
- 9AT knowledge fixes: PASS, `7/7`
- Operator alignment: PASS, `7/7`
- Program Catalog source QA: PASS, `10/10`
- 9BE academic calendar local QA: PASS, `30/30`
- 9BF/9BG source and Georgian controls: PASS, `12/12`
- 10A focused behavior: PASS
- 10B Computer Science topic switching/source display: PASS

## Safety Status

- Chat-only embed readiness: improved for deadline and tuition ambiguity; still requires final owner approval.
- Contact-flow status: blocked; no contact creation flow was run.
- Public launch: `NO-GO`

Confirmed:

- No real `alte.edu.ge` or `join.alte.edu.ge` changes.
- No frontend/Netlify changes.
- No DB/schema/migration/seed/import changes.
- No Secret Manager/CORS/Bridge Hub changes.
- No contact-flow, lead, customer, or task creation.
- No secrets, tokens, passwords, or `DATABASE_URL` values printed.
