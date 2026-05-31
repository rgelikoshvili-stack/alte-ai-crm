# Phase 9AV Claude Intent Router Design

## Current Status

Decision state before this phase:

`BACKEND_DEPLOYED_FULL_KNOWLEDGE_OPERATOR_QA_FAILED_PENDING_FIXES`

Public launch:

`NO-GO`

Production deployment status for this design:

`NOT_DEPLOYED_PENDING_APPROVAL`

## Old Flow

The previous chatbot flow relied heavily on deterministic keyword routing before retrieval:

1. Backend received the visitor message.
2. Manual keyword routing selected a department and source group.
3. The backend retrieved snippets from the selected scope, or sometimes fell back to broader search.
4. The AI analyzer produced a reply and metadata.
5. Backend guards tried to replace generic fallback answers with source-backed deterministic answers.
6. Operator CRM metadata was saved from the final backend state.

This protected the system from many unsafe answers, but Phase 9AS showed recurring failure modes:

- manual keywords sometimes selected the wrong source group;
- source-backed topics sometimes fell into generic AI-service fallback;
- unsupported prompts sometimes matched unrelated approved snippets;
- broad questions needed clarification before retrieval;
- Operator CRM metadata had to remain separate from answer generation.

## New Flow

Phase 9AV introduces Claude as an intent and source router, not as an unrestricted answerer.

Expected request flow:

1. Visitor sends a message.
2. Backend stores the user message.
3. Claude Intent Router receives the message, recent context, public departments, and approved source group descriptions.
4. Claude returns strict JSON only.
5. Backend validates every field.
6. If clarification is needed, backend returns a clarification message and performs no broad retrieval.
7. If an operator is explicitly requested, backend returns safe handover metadata.
8. If source groups are selected, backend searches only those approved source groups.
9. If strong approved excerpts are found, Claude writes the answer using only those excerpts.
10. If no approved excerpt supports the exact answer, backend returns `no_approved_source_found` and offers the correct operator route.
11. Backend saves conversation, answer status, department, source group, and handover metadata for Operator CRM.

## Why Claude Is Used

Claude is used for natural-language intent understanding:

- identifying what the user actually means;
- recognizing broad or ambiguous questions;
- selecting the most relevant approved source group;
- detecting explicit operator intent;
- identifying likely unsupported or fake questions.

Claude is not allowed to answer from general knowledge.

## Backend Control

The backend remains the controller for:

- approved source group validation;
- scoped retrieval;
- no-hallucination fallback;
- answer status;
- handover metadata;
- Operator CRM persistence;
- lead/customer/task creation rules;
- contact-flow approval gates.

Claude cannot create new source groups, approve sources, create contacts, create CRM entities, or override backend safety policy.

## Review Fixes

Phase 9AV review found three issues that must be controlled before deployment:

- source group validation alone was not enough because retrieval could still fall through to broad approved search;
- parseable Claude JSON with invalid or empty source groups could be converted into deterministic broad retrieval;
- the production path could call Claude three times for a normal source-backed answer.

The review-fix design enforces source-group membership after retrieval, blocks broad fallback after validated Claude routes with invalid or empty groups, and skips the legacy full AI analysis call for clear source-backed and clarification paths.

The second review-fix adds two stricter controls:

- deterministic backend safety overrides always beat valid Claude JSON for explicit operator/contact/human requests, known broad prompts, and high-risk unsupported prompts;
- source membership is source-file/source-key/document identity first, while category fallback is disabled by default and allowed only with `allow_category_fallback=true` plus explicit `allowed_categories`.

The final polish keeps explicit operator department metadata aligned across both Claude-validation and deterministic fallback paths:

- operator department inference uses `department_for_operator_request` for finance, admissions, library, IT/EMIS, Medicine / MD, and generic live-operator requests;
- Georgian encoding cleanup removed mojibake from router clarification text and source group descriptions.

## Strict Router JSON

The router returns:

```json
{
  "intent": "string",
  "language": "ka|en",
  "department": "string",
  "public_department_label": "string",
  "topic": "string",
  "needs_clarification": true,
  "clarification_question": "string",
  "clarification_options": ["string"],
  "source_groups_to_search": ["string"],
  "search_terms": ["string"],
  "operator_needed": false,
  "operator_reason": "string",
  "unsupported_likely": false,
  "confidence": 0.0
}
```

Backend validation rules:

- department must normalize to a known department;
- source groups must exist in `source_group_descriptions.json` and `source_groups.json`;
- max source groups per query is 3;
- clarification blocks broad retrieval;
- unsupported/low confidence cannot become broad retrieval;
- invalid JSON falls back to deterministic safe routing.
- invalid source group names produce `router_validation_status=invalid_source_groups` and do not trigger broad retrieval;
- empty source groups without clarification/operator produce `router_validation_status=empty_source_groups` and do not trigger broad retrieval;
- only complete router failure or disabled Claude routing may use deterministic fallback source groups.

## Scoped Retrieval Enforcement

Backend retrieval now treats selected source groups as a hard boundary.

For every selected source group, the backend:

- reads `source_groups.json`;
- uses `source_files`, `source_keys`, `document_ids`, source key/title/path, and snippet/source identity metadata to test group membership;
- searches approved snippets only;
- filters every retrieved candidate to the selected source group before it can be used;
- searches all selected groups in order and merges only group-matching approved results.

If a selected source group returns no matching approved snippets, the backend returns `no_approved_source_found` instead of searching all approved snippets broadly.

This is especially important for groups whose `source_domain` is `null` or broad, including `admissions_rules`, `finance_sources`, and selected `alte.edu.ge` policy groups.

Category fallback policy:

- same-category matches are rejected by default;
- `source_domain=null` groups still require source identity membership;
- category-only acceptance requires `allow_category_fallback=true` and an explicit `allowed_categories` list in source group config;
- source groups without usable identity metadata do not broaden silently.

## Deterministic Safety Overrides

Claude assists routing, but backend safety rules are authoritative.

Backend overrides valid Claude JSON before retrieval when the visitor message deterministically matches:

- explicit operator/contact/human intent: force `operator_needed=true`, clear source groups/search terms, and route to handover instead of retrieval;
- known broad prompt: force clarification, clear source groups, and keep `should_handover=false`;
- high-risk unsupported/fake prompt: force unsupported handling and prevent broad retrieval.

The same operator/contact priority applies when Claude routing is disabled or fails and the deterministic fallback router is used. Fallback checks explicit operator/contact intent before any forced source-group routing, so mixed messages such as "I want finance operator" or "მინდა ფინანსურ დეპარტამენტთან დაკავშირება" become handover routes, not source-backed finance retrieval.

Metadata records:

- `deterministic_override_applied`;
- `deterministic_override_reason` with `explicit_operator_request`, `known_broad_question`, `unsupported_high_risk`, or `none`.

The operator detector has a single implementation to avoid stale duplicate safety logic.

## Claude Call Count Control

The production source-backed path is:

Claude Intent Router -> scoped retrieval -> source-grounded answer generator.

For clear source-backed paths and clarification paths, the backend bypasses the old full `analyze_with_ai` call. Metadata records:

- `used_claude_intent_router`;
- `used_legacy_ai_analysis`;
- `used_grounded_answer_generator`;
- `router_validation_status`.

The legacy analyzer remains available for deterministic fallback or non-source-backed legacy paths.

## Source-Grounded Answering

When approved excerpts are retrieved, the final answer prompt says:

“You are answering as Alte University’s assistant. Use only the approved source excerpts provided below. Do not use your general knowledge. If the exact answer is not present in the excerpts, say that the approved source does not contain exact information and offer to connect the user with the relevant operator. Do not invent dates, prices, deadlines, documents, or policies.”

The answer must:

- match the user language;
- use only retrieved excerpts;
- avoid phone/email/name requests for informational answers;
- return no approved source when exact support is missing;
- keep Georgian UTF-8 clean.

## Hallucination Guard

The backend blocks unsafe behavior by:

- searching only validated selected source groups;
- treating fake/future prompts as unsupported unless strong approved evidence exists;
- preserving known mandatory facts: bachelor 240 ECTS, master 120 ECTS, status suspension max 5 years, CS spring registration 9-14 March and semester start 30 March;
- returning `no_approved_source_found` for unsupported exact tuition, fake scholarships, fake campus questions, unapproved IT procedures, and unapproved library rules.

## Operator CRM Metadata Rules

Source-backed informational answer:

- `should_handover=false`
- `human_handover=false`

Clarification:

- `should_handover=false`
- `human_handover=false`

No approved source:

- operator fallback is allowed;
- `should_handover=true` only when the backend policy marks fallback as handover.

Explicit operator request:

- `should_handover=true`
- `human_handover=true`

Wait for operator:

- `waiting_for_operator=true`
- `human_handover=true`

Contact form:

- no lead/customer/task unless contact-flow approval is explicitly complete.

## Safety Status

This phase is code-ready only. It does not deploy, upload assets, modify the real Alte site, change DB schema, run migrations, seed/import data, change Secret Manager, change CORS, touch Bridge Hub, or execute contact creation.

Public launch remains:

`NO-GO`
