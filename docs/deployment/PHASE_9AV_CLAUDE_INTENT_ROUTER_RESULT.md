# Phase 9AV Claude Intent Router Result

`PHASE_9AV_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY`

Decision state:

`BACKEND_CODE_CLAUDE_INTENT_ROUTER_READY_PENDING_DEPLOY`

Public launch:

`NO-GO`

Production status:

`NOT_DEPLOYED_PENDING_APPROVAL`

## Summary

Phase 9AV makes Claude the chatbot's intent and source-selection brain while keeping the backend as the controller for approved-source access, scoped retrieval, hallucination prevention, handover metadata, Operator CRM state, and CRM entity creation rules.

Claude does not answer from general knowledge. It classifies the user question and returns strict JSON. The backend validates that JSON and searches only approved source groups.

## Architecture

Design document:

`docs/architecture/PHASE_9AV_CLAUDE_INTENT_ROUTER_DESIGN.md`

Old behavior relied heavily on manual keyword routing. This phase adds a validated Claude Intent Router so natural-language intent, broad-question detection, source-group selection, and operator-intent detection are handled more intelligently.

## Source Group Descriptions

Source descriptions path:

`backend/app/data/knowledge/source_group_descriptions.json`

The file documents approved source groups for:

- official academic rules
- academic calendar 2025-2026
- admissions rules
- student status and mobility
- exams and assessment
- finance sources
- library sources
- IT support sources
- international admissions sources
- career sources

Each entry includes Georgian and English descriptions, good-for topics, not-good-for topics, fallback department, exact-answer policy, and operator fallback policy.

## Router Service

Router service path:

`backend/app/services/claude_intent_router_service.py`

The router returns and validates strict JSON with:

- intent
- language
- department
- public department label
- topic
- clarification flag/question/options
- source groups to search
- search terms
- operator flag/reason
- unsupported-likely flag
- confidence

Validation rules:

- unknown source groups are removed;
- source groups are limited to 3;
- broad clarification performs no broad retrieval;
- invalid JSON falls back to deterministic safe routing;
- Claude cannot create source group names or CRM entities.

## Scoped Retrieval

`backend/app/services/chat_service.py` now uses the validated intent route to build the knowledge route decision before retrieval.

If clarification is needed:

- backend returns clarification;
- no source retrieval is performed;
- `should_handover=false`.

If source groups are selected:

- backend searches only the selected approved source group scope;
- retrieved excerpts are kept in metadata for source-grounded answering;
- source-backed informational answers keep `should_handover=false`.

If no approved source supports the exact answer:

- backend returns `no_approved_source_found`;
- backend may offer the correct operator fallback;
- unsupported/future/fake prompts do not use broad unrelated snippets.

Review-fix enforcement:

- selected source groups are now hard retrieval boundaries;
- every retrieved candidate is filtered against selected source group metadata;
- groups with `source_domain=null` are still restricted by source file/source key/title/document identity metadata;
- no broad approved-source fallback runs after a validated Claude route selected source groups;
- invalid or empty Claude source groups do not trigger deterministic broad retrieval.

Second review-fix enforcement:

- deterministic backend overrides beat valid Claude JSON for explicit operator/contact/human requests;
- deterministic fallback checks operator/contact intent before forced source-group routing;
- deterministic backend overrides force clarification for known broad prompts even if Claude selected source groups;
- deterministic unsupported/fake markers clear source groups before retrieval;
- same-category source matches are rejected by default;
- category fallback requires explicit `allow_category_fallback=true` and `allowed_categories`.

Fallback operator priority was verified for mixed operator/source-group requests such as finance operator handover. The duplicate operator detector was removed; the router has one expanded `has_operator_request()` implementation.

Final polish fixes:

- operator department inference uses department_for_operator_request, so explicit finance/library/IT/Medicine operator requests keep the best public department instead of falling back to generic human operator metadata;
- Georgian encoding cleanup removed mojibake from router clarification text and source group descriptions.

## Router Validation Status

The router now records:

- `valid`
- `invalid_source_groups`
- `empty_source_groups`
- `fallback_used`

Only complete Claude routing failure or disabled Claude routing may use deterministic fallback source groups. A parseable Claude response with fake or empty source groups is treated conservatively and returns clarification/no-approved-source behavior instead of broad retrieval.

Deterministic override metadata:

- `deterministic_override_applied`
- `deterministic_override_reason`

## Claude Call Count / Cost Control

For clear source-backed informational paths, the backend now uses:

Claude Intent Router -> scoped retrieval -> source-grounded answer generator.

The old full `analyze_with_ai` path is bypassed for source-backed and clarification paths. Internal metadata documents:

- `used_claude_intent_router`
- `used_legacy_ai_analysis`
- `used_grounded_answer_generator`
- `router_validation_status`

## Source-Grounded Answering

`backend/app/services/ai_service.py` now includes a source-grounded answer generator.

Claude answer prompt requires:

- use only approved excerpts;
- do not use general knowledge;
- do not invent dates, prices, deadlines, documents, or policies;
- say the approved source lacks exact information when excerpts do not contain the answer;
- keep Georgian UTF-8 clean.

In test/mock mode the function uses deterministic excerpt-based fallback.

## Operator Metadata

Metadata rules remain:

- source-backed informational answer: `should_handover=false`, `human_handover=false`;
- clarification: `should_handover=false`, `human_handover=false`;
- unsupported/no-approved-source: operator fallback allowed by backend policy;
- explicit operator request: `should_handover=true`, `human_handover=true`;
- wait-for-operator remains handled by the existing handover endpoint;
- contact form does not create lead/customer/task unless contact flow is approved and submitted.

## Local QA

Local QA script:

`backend/app/scripts/local_phase_9av_claude_intent_router_qa.py`

Local QA status:

`PASS: 27/27`

Pytest status:

`PASS: 988 passed`

Verifier status:

`PASS`

## Safety Confirmations

- Real Alte site modified: NO
- Assets uploaded or embedded: NO
- Backend deployed: NO
- DB schema changed: NO
- Migration run: NO
- Seed/import run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Contact creation executed: NO
- Lead/customer/task created: NO
- Frontend calls Anthropic directly: NO
- Public launch: NO-GO

## Expected 9AS Impact

Expected improvement is strongest in cases where manual keyword routing selected the wrong source group or failed to distinguish broad, unsupported, calendar, admissions, library, IT, finance, international, and policy questions.

Production verification is still pending because this phase is not deployed.

## Production Deployment Follow-up

The production deployment and post-deploy QA record is maintained separately:

`docs/deployment/PHASE_9AV_PRODUCTION_DEPLOY_AND_QA_RESULT.md`

This implementation document intentionally retains the original code-ready status marker (`NOT_DEPLOYED_PENDING_APPROVAL`) for the Phase 9AV implementation verifier. The deploy record contains the current Cloud Run revision, production QA status, and final deployment decision state.
