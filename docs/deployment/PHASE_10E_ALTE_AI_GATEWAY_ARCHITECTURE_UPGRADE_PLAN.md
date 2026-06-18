# Phase 10E Alte AI Gateway Architecture Upgrade Plan

Date: 2026-06-18
Branch: `phase-9s-agent-preview-cors-note`

Status: `ALTE_GATEWAY_ARCHITECTURE_PLAN_READY_PUBLIC_LAUNCH_NO_GO`

This is a planning-only architecture note. No deploy, real-site change, DB/schema change, contact-flow enablement, lead/customer/task creation, or Secret/CORS/Bridge Hub change is authorized by this phase.

## A. Current Alte Architecture Summary

The current Alte chatbot architecture is a single public chat gateway backed by several shared services:

- Public chat routes are in `backend/app/api/routes_chat.py` under `/chat`.
- `/chat/session/start` creates a chat conversation/session.
- `/chat/message` calls `chat_service.handle_message()` and currently performs message persistence, deterministic knowledge routing, Claude intent routing, optional legacy AI analysis, approved-source retrieval, grounded deterministic replies, answer validation, source-label cleanup, handover decisions, and guarded CRM write decisions.
- `/chat/handover/{conversation_id}` can set `waiting_for_operator` without customer/lead/task creation when there is no customer or lead.
- `/chat/contact/{conversation_id}` is the explicit contact-flow write endpoint and can create/update customer, lead, and task after session match, consent, and phone/email checks.
- `/chat/messages/{conversation_id}` exposes the public transcript for a valid session.

The current knowledge/admin surface is separate but not gateway-shaped:

- `routes_knowledge.py` exposes `/knowledge/sources`, `/knowledge/snippets`, `/knowledge/review-queue`, `/knowledge/snippets/search`, and operator-reply knowledge-candidate creation.
- `knowledge_service.py` supports source/snippet CRUD, approval/archive, review queue, and snippet search.
- `knowledge_routing_service.py` performs deterministic department/source-group routing, clarification detection, source-group selection, and public clarification formatting.
- `claude_intent_router_service.py` classifies intent/source groups with Claude when enabled and falls back to deterministic routing.

The current CRM/operator surfaces are write-capable and should remain internal:

- `routes_leads.py` exposes lead create/list/detail/update/stage-change.
- `routes_tasks.py` exposes task create/list/update/complete.
- `routes_conversations.py` exposes conversation create/detail/messages.
- `operator_service.py` builds inbox, task, lead, dashboard, and pipeline views and infers conversation department.

Authentication and public exposure are controlled centrally:

- `main.py` mounts all routers.
- `auth_rbac_middleware()` applies auth unless `permission_service.is_public_path()` allows the path.
- Current public prefixes include `/chat/session/start`, `/chat/message`, `/chat/handover`, `/chat/contact`, and `/chat/messages`.
- CRM, dashboard, inbox, task, lead, and knowledge management routes are RBAC-protected.

## B. Bridge Hub Comparison

Bridge Hub separates chatbot capabilities into three gateway classes:

1. `/api/ai/chat`: main assistant, lazy DB context, Claude.
2. `/ask`: fast SQL/DB intent query without Claude.
3. `/api/claude/chat`: tool-using agent loop.

Alte already has the ingredients but they are concentrated in `/chat/message`:

- Main assistant behavior exists in `handle_message()`, `route_with_claude_intent()`, `retrieve_chat_knowledge()`, and `validate_public_chat_answer()`.
- Fast deterministic behavior exists as helper functions: `classify_knowledge_route()`, `grounded_source_backed_reply()`, `grounded_calendar_reply()`, `grounded_program_catalog_reply()`, and source-group lookup helpers.
- Internal tool-like behavior exists as normal protected services/routes: operator inbox, conversation detail, lead/task lists, knowledge review, and operator-reply knowledge candidates.

The upgrade should therefore split responsibilities without changing the database first.

## C. Proposed 3-Gateway Alte Architecture

### 1. `/api/chat/message`

Public student chatbot gateway.

Purpose:

- Read-only public assistant for student/applicant questions.
- Knowledge/routing/clarification only.
- Runs answer validator before any response.
- Safe public source labels only.
- No lead/customer/task creation.
- No contact-flow write.

Implementation direction:

- Add a new `/api/chat/message` alias or versioned route while preserving existing `/chat/message` until the widget migration is approved.
- Introduce a public-chat service wrapper, for example `public_chat_gateway_service.py`, that calls a write-blocked mode of the existing chat pipeline.
- In write-blocked mode, `ChatMessageResponse.created_lead_id` and `created_task_id` must always be `None`, and `should_create_lead` must always be `False`.
- Explicit public handover should only set safe chat state if still approved; no customer/lead/task write should occur from the public chatbot gateway.
- `/chat/contact/{conversation_id}` should remain blocked for public launch and must not be included in the chat-only embed.

### 2. `/api/knowledge/ask`

Fast deterministic knowledge gateway.

Purpose:

- No Claude by default.
- Exact answers from structured KB and approved deterministic mappings.
- Academic calendar, program catalog, admissions docs, student rules, finance/grants safe answers, and source-group lookup.
- Return structured result metadata: `answer_source_status`, `source_group`, `public_source_label`, `confidence`, `clarification_needed`, and `clarification_options`.

Implementation direction:

- Add a read-only POST endpoint such as `/api/knowledge/ask`.
- Reuse `classify_knowledge_route()` to select source groups.
- Reuse deterministic answer helpers from `chat_service.py`, but move or wrap them into a knowledge-answer module to avoid pulling in CRM write behavior.
- Call approved-source search only when deterministic exact helpers do not answer and source-group config allows exact answers.
- Never create conversations, messages, customers, leads, or tasks.
- Never call Claude unless a future explicitly approved option sets `allow_ai_fallback=true`; default must be deterministic.

### 3. `/api/operator/agent-chat`

Internal operator/admin assistant gateway.

Purpose:

- Authenticated only; never exposed to the public widget.
- Uses Claude/tool loop only for operators/admins.
- Can summarize conversations, suggest replies, list pending conversations/tasks, inspect approved knowledge, and draft follow-up actions.
- Write actions require explicit approval and must be separate from the assistant's draft response.

Implementation direction:

- Add a new protected route prefix such as `/api/operator/agent-chat`.
- Require existing RBAC permission such as `conversation:read` plus role-specific gates; admin/manager/operator should be allowed read-only tools, write tools should require roles that already have write permissions.
- The first implementation should be read-only plus suggested actions.
- Later write-capable tools must use a two-step protocol: the model proposes an action, the UI shows exact action details, the operator approves, and only then a normal service method executes.

## D. Public vs Internal Boundary

Public:

- `/api/chat/message`
- `/api/knowledge/ask`, only if it is strictly read-only and returns public-safe source labels.
- Health/version/diagnostic endpoints already approved for public use.

Internal:

- `/api/operator/agent-chat`
- Leads, tasks, customers, conversations detail, inbox, dashboard, analytics, knowledge review/write endpoints.
- Any route that reads private contact details, lead status, operator notes, tasks, customer records, or full conversation detail.

Required policy:

- Public widget must never call operator agent routes.
- Public widget must never call lead/task/customer routes.
- Public widget must not receive internal source keys, chunks, DB IDs, private notes, contact data, or raw prompt/router internals.

## E. Read-Only vs Write-Capable Boundary

Read-only public gateways:

- `/api/chat/message`: stores only minimal chat transcript/session state if needed for conversation continuity; must not create CRM entities.
- `/api/knowledge/ask`: no writes at all, except optional non-sensitive rate/cost logs in a later approved phase.

Write-capable internal gateways:

- Existing lead/task/customer/conversation/knowledge mutation routes.
- Future `/api/operator/agent-chat` write tools only after explicit operator approval.

Contact-flow boundary:

- Contact-flow remains blocked.
- `/chat/contact/{conversation_id}` and any successor must not be included in the chat-only embed package until separate privacy/contact approval.
- The public chatbot may suggest waiting for an operator or contacting official admissions/finance, but must not create follow-up records without explicit approval.

## F. Lazy Context Loading Proposal

Current `/chat/message` builds conversation history and may retrieve initial knowledge before final routing/answer decisions. The upgraded gateways should load context lazily by intent:

- Start with deterministic normalization and route classification.
- If the prompt is an answerable deterministic fact, answer without Claude and without broad DB search.
- If clarification is required, return clarification immediately.
- If approved-source retrieval is required, load only the selected source group.
- If Claude is required for the public assistant, pass only compact conversation history and source excerpts, never broad DB context.
- For operator agent chat, load only the context required by selected tools: conversation summary first, then full transcript only if the operator asks, then related lead/task/customer only when needed and permitted.

Recommended context tiers:

- Tier 0: message text, language, source domain, selected department/topic.
- Tier 1: deterministic route/source group and clarification state.
- Tier 2: structured KB record or approved source snippets for one source group.
- Tier 3: compact conversation history.
- Tier 4 internal only: conversation detail, lead/task/customer records, operator inbox.

## G. Tool List Proposal for Internal Operator Only

Read-only tools:

- `get_conversation_summary(conversation_id)`
- `get_conversation_messages(conversation_id)`
- `list_waiting_conversations(filters)`
- `list_pending_tasks(filters)`
- `list_leads(filters)`
- `get_lead_detail(lead_id)`
- `search_approved_knowledge(query, source_group, language)`
- `get_source_group_policy(source_group_id)`
- `suggest_operator_reply(conversation_id, tone, language)`

Write tools, future phase only and explicit approval required:

- `create_operator_message(conversation_id, text)`
- `create_task_for_conversation(conversation_id, payload)`
- `update_task_status(task_id, status)`
- `update_lead_stage(lead_id, stage_id)`
- `create_knowledge_candidate_from_operator_reply(message_id)`

Write tool constraints:

- No tool should execute directly from model text.
- Each write must return a preview first.
- The UI must require a separate human approval event.
- Every write must use existing service methods and audit logging.

## H. Fast Deterministic `/knowledge/ask` Proposal

Request shape:

```json
{
  "question": "When is Computer Science spring registration?",
  "language": "en",
  "source_domain": "alte.edu.ge",
  "source_group": null,
  "allow_ai_fallback": false
}
```

Response shape:

```json
{
  "answer": "Computer Science spring registration is 9 - 14 March 2026.",
  "answer_source_status": "answered_from_approved_source",
  "source_group": "academic_calendar_2025_2026",
  "public_source_label": "აკადემიური კალენდარი 2025–2026",
  "confidence": 0.95,
  "clarification_needed": false,
  "clarification_options": [],
  "unsupported_likely": false
}
```

Initial supported topics:

- Academic calendar dates.
- Program catalog counts, levels, program lists, program language/credits/qualification when directly grounded.
- Admissions documents and admission-without-exams rules.
- Student status, mobility, exams, GPA, FX/F, and official academic rules.
- Finance/grants safe answers and tuition no-invention fallbacks.
- Source-group lookup and clarification prompts.

Default non-goals:

- No Claude.
- No CRM writes.
- No contact collection.
- No private student data lookup.
- No invented dates, deadlines, tuition amounts, grant eligibility, or legal/policy facts.

## I. Security, Privacy, and Contact-Flow Constraints

- Public launch remains `NO-GO`.
- Contact-flow remains `BLOCKED`.
- No endpoint in this plan should change DB schema or require migrations.
- No public endpoint should expose lead/customer/task data.
- No public endpoint should create lead/customer/task records.
- No public endpoint should print or return secrets, tokens, passwords, API keys, or `DATABASE_URL`.
- Public source labels must remain whitelisted and clean.
- Internal operator agent routes must require bearer auth and RBAC.
- Tool execution must be audited and separated into read-only and write-approved modes.
- Rate limiting and abuse controls should be considered before exposing `/api/knowledge/ask` publicly.

## J. Migration Phases

### 10F: Implement `/api/knowledge/ask` Deterministic Gateway

- Add schemas and route for deterministic knowledge ask.
- Extract/wrap deterministic answer helpers from `chat_service.py`.
- Add tests for calendar, catalog, admissions, student rules, finance/grants, unsupported facts, source labels, and no writes.
- Keep Claude disabled by default.
- No DB/schema changes.

### 10G: Implement Internal Operator Agent Gateway

- Add protected `/api/operator/agent-chat` route.
- Start read-only: conversation summaries, pending conversations/tasks, lead detail, approved KB search, suggested replies.
- Add strict RBAC tests.
- Add write-action preview protocol, but do not enable writes until separately approved.

### 10H: Add Cost/Session Logging If Needed

- Add non-sensitive per-gateway metrics if approved.
- Track gateway, source group, response type, latency, model usage if Claude is used, and answer-source status.
- Do not log secrets, contact values, or raw private records.
- Avoid schema changes unless a separate migration phase is approved.

### 10I: Final Chat-Only Embed Package

- Point public widget to the read-only public student chatbot gateway.
- Do not include contact form or lead/task/customer creation.
- Verify source labels, clarification rendering, no-contact behavior, CORS, and browser safety.
- Keep public launch `NO-GO` until owner approval and real-site QA are complete.

## K. Decision

Decision: `ALTE_GATEWAY_ARCHITECTURE_PLAN_READY_PUBLIC_LAUNCH_NO_GO`

Recommended architecture:

- Use `/api/chat/message` as the public read-only student assistant gateway.
- Use `/api/knowledge/ask` as the fast deterministic no-Claude knowledge gateway.
- Use `/api/operator/agent-chat` as the authenticated internal operator/admin agent gateway.

The upgrade should proceed in phases 10F through 10I. No production launch, contact-flow activation, DB/schema change, or public operator-agent exposure is approved by this plan.
