# Phase 10G Cloud AI Reasoning Fallback Result

Date: 2026-06-21
Branch: `phase-9s-agent-preview-cors-note`

## Root Cause

The public chat clarification flow handled the initial ambiguous admissions deadline question correctly, but the next user turn was interpreted in isolation. When the user replied `მაგისტრატურის`, the router treated it as a generic master admissions request and returned master admission document requirements instead of preserving the previous deadline intent.

Secondary risk areas were also covered:

- Deadline prompts could receive generic document lists.
- Tuition/cost prompts could receive program descriptions or ECTS-only answers.
- Short clarification follow-ups could lose the original intent.

## Architecture Change

`/api/chat/message` now keeps deterministic routing first, then applies a constrained Cloud AI Orchestrator-style reasoning fallback before the final public answer validator.

`/api/knowledge/ask` remains deterministic and no-Claude.

The fallback reads:

- Latest user message
- Recent conversation messages and AI clarification metadata
- Previous clarification question/options
- Deterministic source group
- Deterministic answer and answer status
- Safety constraints for deadlines, tuition, and private data

The structured internal decision shape is:

```json
{
  "decision": "answer | clarify | safe_fallback | refuse",
  "intent": "...",
  "source_group": "...",
  "confidence": 0.0,
  "reason": "...",
  "clarification_question": "...",
  "clarification_options": [],
  "answer_strategy": "...",
  "must_not_invent": true
}
```

## Cloud AI Orchestrator Behavior

Implemented behavior in `backend/app/services/chat_service.py`:

- Preserves admissions deadline context across clarification turns.
- Maps `მაგისტრატურის` after a deadline clarification to master admissions deadline context.
- Returns a deadline-specific safe fallback when exact/current deadline is not grounded.
- Keeps tuition/cost intent ahead of program description when the answer is weak.
- Leaves `/api/knowledge/ask` unchanged with `used_claude: false`.
- Runs the existing final answer validator after the fallback decision.

## Weak Answer Detector

The weak detector flags:

- Deadline prompt plus generic document answer.
- Tuition/cost prompt plus program/ECTS-only answer.
- Clarification follow-up that loses previous deadline intent.
- Source group mismatch where a deadline/cost answer would otherwise land in the wrong context.

The detector was tightened after production Program Catalog QA showed one catalog-specific tuition question should remain catalog-scoped rather than finance-scoped.

## Files Changed

- `backend/app/services/chat_service.py`
- `backend/app/tests/test_phase_10g_cloud_ai_reasoning_fallback.py`

## Tests Added

Added `backend/app/tests/test_phase_10g_cloud_ai_reasoning_fallback.py` covering:

- Georgian master admissions deadline clarification sequence.
- Georgian bachelor admissions deadline clarification sequence.
- English application deadline clarification sequence.
- Medical tuition/cost safe clarification.
- Clear Medicine program info still returns program information and can mention 360 ECTS.
- `/api/knowledge/ask` remains deterministic with `used_claude: false`.

## Local Validation

Local Python path used: `backend\.venv\Scripts\python.exe`.

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10g_cloud_ai_reasoning_fallback.py --basetemp .pytest_tmp_10g_focus_after_order`: 6 passed
- `pytest --basetemp .pytest_tmp_10g_full_rerun2`: 1147 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10g_9bf_9bg_final`: 12 passed
- `pytest app/tests/test_phase_10a_clarifying_router_validator.py app/tests/test_phase_10b_topic_switch_source_display.py app/tests/test_phase_10f_knowledge_ask_gateway.py app/tests/test_phase_10g_cloud_ai_reasoning_fallback.py --basetemp .pytest_tmp_10g_focused_bundle_final`: 25 passed

## Deploy Result

Backend-only deploy performed after local validation.

- Image tag: `v1.0-phase-10g-cloud-ai-reasoning-fallback`
- Final image digest: `sha256:d45237d140bea7bbadd31872b4d4f1ca5ec92d053868e7e1c0eaf107dabe36d2`
- Deployed revision: `alte-ai-crm-backend-00064-gkm`
- Traffic: 100%
- Health: 200
- Rollback target: `alte-ai-crm-backend-00062-rfd`

Note: revision `alte-ai-crm-backend-00063-cq4` was deployed first, then superseded by `00064-gkm` after tightening the catalog-specific tuition fallback.

## Production QA

Focused production probes on `00064-gkm`:

- Deadline clarification sequence:
  - User: `რომლის არის ჩარიცხვის ბოლო ვადა?`
  - Bot: `clarification_needed`
  - User: `მაგისტრატურის`
  - Result: `safe_fallback`, `source_group=admissions_rules`, no invented deadline, no generic document-only answer, no lead/task created.
- Medical tuition:
  - User: `რა ღირს სამედიცინო სწავლა?`
  - Result: `clarification_needed`, safe tuition wording, no 360 ECTS/program-description-only answer, no invented amount, no lead/task created.
- `/api/knowledge/ask`:
  - `used_claude: false`
  - `status=clarification_needed`
  - `source_group=finance_sources`

Regression probes:

- Production 9AS full knowledge coverage: 53/53 PASS
- Production 9AT knowledge fixes: 7/7 PASS
- Production operator alignment: 7/7 PASS
- Production Program Catalog source QA: 10/10 PASS
- 9BE local QA after deploy: 30/30 PASS
- 9BF/9BG focused after deploy: 12/12 PASS

## Readiness And Safety

- Chat-only embed readiness remains `READY_FOR_APPROVAL`.
- Contact-flow remains `BLOCKED`.
- Public launch remains `NO-GO`.
- No real site changes.
- No frontend/Netlify changes.
- No DB/schema/migration/seed/import changes.
- No Secret Manager/CORS/Bridge Hub changes.
- No contact-flow run.
- No lead/customer/task creation.
- No real personal data submitted.
- No secrets, tokens, passwords, or `DATABASE_URL` values printed.

Decision: `PHASE_10G_CLOUD_AI_REASONING_FALLBACK_DEPLOYED_PUBLIC_LAUNCH_NO_GO`
