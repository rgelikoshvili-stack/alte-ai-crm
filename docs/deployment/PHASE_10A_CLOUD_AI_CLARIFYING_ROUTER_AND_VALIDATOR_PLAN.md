# Phase 10A Cloud AI Clarifying Router and Answer Validator Plan

Date: 2026-06-16

Branch: `phase-9s-agent-preview-cors-note`

Public launch: `NO-GO`

## Current Routing Architecture Summary

The backend currently combines deterministic routing and cloud-AI-style routing metadata:

- `knowledge_routing_service.py` scores departments and source groups from approved routing maps.
- `claude_intent_router_service.py` validates or replaces routing decisions and can request clarification.
- `chat_service.py` retrieves approved knowledge, applies deterministic source-backed answer helpers, and persists the public chat response.
- Existing safety guards handle academic-calendar exact dates, unsupported official questions, private-data refusal, no-contact lead protection, and public source-label cleanup.

Phase 10A extends the current architecture rather than replacing it. The new layer should bias toward clarification when confidence, source group, or answer path is ambiguous.

## Proposed Components

1. Routing confidence score
   - Continue using `KnowledgeRouteDecision.confidence`.
   - Treat low/medium confidence or close competing department scores as clarification candidates.

2. Candidate source groups
   - Preserve ranked/allowed source groups from the department map.
   - Add broad-question source-group disambiguation for finance, grants, programs, calendar, registration, library, ombudsman, academic integrity, and operator handoff.

3. Clarification decision layer
   - Add deterministic Phase 10A broad/ambiguous prompt detection before retrieval.
   - Prefer `clarification_required=True` over guessing when a user asks broad questions such as "registration", "tuition", "grant", "programs", or "calendar".

4. Clarifying question generator
   - Reuse `format_clarification_reply()`.
   - Add specific options for admissions, academic calendar, program catalog, finance/grants, student services, library, ombudsman, and academic integrity.

5. Answer validator
   - Validate the answer before persistence.
   - Do not allow empty/whitespace answers.
   - Do not allow private-data requests to be answered from admissions documents.
   - Do not allow unsupported future calendar years to reuse approved-year dates.
   - Do not allow finance answers to invent exact current amounts.
   - Do not expose internal source IDs in the public reply.

6. Empty-answer fallback
   - If a source-backed path produces an empty answer, return a clarification or safe no-source fallback.
   - Never send an empty public chatbot answer.

7. Privacy/refusal classifier
   - Keep the Phase 9CK private student-data refusal before retrieval.
   - Mark privacy requests as `privacy_safety`, with no lead/task side effects.

8. Unsupported-year/calendar guard
   - Keep unsupported future-year calendar handling before grounded calendar rendering.
   - For 2027+ calendar requests, do not reuse 2025-2026 dates.

## Source Groups And Departments

Phase 10A treats these as explicit clarification/validation targets:

- admissions
- academic_calendar_2025_2026
- program_catalog
- finance/tuition/grants
- student_services
- academic_integrity
- library
- ombudsman
- operator_handoff
- unsupported/private_data

## Implementation Approach

- Add Phase 10A broad clarification helpers in `knowledge_routing_service.py`.
- Add an answer validator in `chat_service.py` after answer construction and before persistence.
- Keep existing deterministic safety rules and 9BE/9BF/9BG/9CK behavior.
- Add focused regression tests for clarification, Phase 9CF blocker fixes, no-empty answers, no private disclosure, no unsupported-year date reuse, and no CRM side effects.
- Add a local production-safe behavior review script if no Phase 9CF script exists.

## Decision

`PHASE_10A_PLAN_READY_PUBLIC_LAUNCH_NO_GO`

Public launch remains `NO-GO`.
