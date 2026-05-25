# Final Pre-Embed Approval Gate

## A. Current Technical Status

- Production backend is deployed and healthy.
- Cloud Run service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Cloud Run service: `alte-ai-crm-backend`
- Claude is enabled through the backend.
- Cloud SQL is ready.
- Secret Manager is ready.
- Full local Alte Knowledge Base has been imported into production Knowledge Base.
- Sensitive KB content remains `review_required`.
- Finance/tuition/scholarship/deadline no-contact guard is deployed and verified in production.
- Safe Pro widget candidate is ready.

## B. Selected Widget

Selected candidate:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

Design style:

```text
compact PIP-style widget with selected Pro polish
```

Reason:

- Least intrusive for public `alte.edu.ge` pages.
- Safe backend-connected architecture.
- KA/EN support.
- No direct Anthropic browser call.
- No frontend API key or secret.
- Frontend renders backend state only; backend remains responsible for AI, Knowledge Base, and CRM business rules.

Baseline widget remains available:

```text
widget/alte-university-ai-chatbot-safe.html
```

## C. Blockers

These items are not approved and remain pending:

- Human reviewer decisions: `PENDING`
- Official content approval: `PENDING`
- Privacy/data approval: `PENDING`
- Final widget asset URL: `PENDING`
- Website admin/developer deployment confirmation: `PENDING`
- Actual site embed: `PENDING`
- Real-domain browser smoke: `PENDING`

## D. Approval Requirements

Required before actual embed:

1. Human reviewer decisions completed, or explicit approval to keep sensitive content handover/review-required.
2. Official content approval.
3. Privacy/data approval.
4. Final widget asset hosting URL selected.
5. Alte website admin/developer confirms where the snippet will be inserted.
6. Real-domain smoke plan approved.

## E. Go/No-Go

```text
FINAL_PRE_EMBED_STATUS=NO_GO_PENDING_APPROVALS
```

Do not mark GO. Do not embed on the real Alte website until all required approvals and the final asset URL are confirmed.

## Phase 9L-M-N Final Handoff Update

- Final approval intake prepared: `docs/deployment/PHASE_9L_FINAL_APPROVAL_INTAKE.md`
- Final website handoff package prepared: `docs/final_handoff/FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md`
- Asset manifest prepared: `docs/final_handoff/WIDGET_ASSET_MANIFEST.md`
- Actual site embed execution status: `NOT_EXECUTED_MISSING_APPROVALS`
- Real-domain smoke status: `NOT_EXECUTED_SITE_NOT_EMBEDDED`
- Public launch decision: `NO_GO_PENDING_APPROVALS_OR_SITE_EMBED`

Decision state:

```text
BACKEND_DEPLOYED_FINAL_HANDOFF_READY_NO_GO_PENDING_APPROVALS_AND_SITE_EMBED
```

## Phase 9L-P Final Handoff Update

- Final approval/access record: `docs/deployment/PHASE_9L_FINAL_APPROVAL_AND_ACCESS_RECORD.md`
- Conservative content policy: ready, final human review pending for sensitive exact facts.
- Privacy/data: approved in principle, official privacy URL pending.
- Website access: approved for preparation, actual upload/embed pending.
- Actual site embed status: `NOT_EXECUTED_PENDING_FINAL_CONFIRMATION`
- Real-domain smoke status: `NOT_EXECUTED_SITE_NOT_EMBEDDED`
- Public launch decision: `NO_GO_PENDING_SITE_EMBED_AND_REAL_DOMAIN_SMOKE`

Decision state:

```text
BACKEND_DEPLOYED_FINAL_HANDOFF_READY_NO_GO_PENDING_SITE_EMBED_AND_SMOKE
```

## Phase 9D Routing Requirement

Department-aware handover routing is implemented in code and must be redeployed before actual website embed.

The widget sends sidebar context only. The backend decides:

- route department;
- handover;
- task/lead/customer creation;
- no-contact lead guard.

Decision state:

```text
BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY
```

## Phase 9D-UI Sidebar Layout

The selected UI is now the Safe Pro Sidebar Layout.

- Main widget: `widget/alte-university-ai-chatbot-safe-pro.html`
- Archived compact PIP alternate: `widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html`
- Sidebar department selection drives backend context through `selected_department` and `selected_topic`.
- Actual embed remains pending.
- Public launch is not complete.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_SIDEBAR_WIDGET_READY_PENDING_REDEPLOY_AND_SITE_EMBED
```

## Phase 9D-UI-Final Exact Pro Sidebar Update

Selected widget:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

The final preferred UI is now the exact functional Pro Sidebar layout from the uploaded design ZIP/screenshots.

- Left sidebar department navigation is required.
- Right chat area includes header, KA/EN switch, reset control, trust/source bar, messages, quick chips, source cards, handover/operator card, contact request UI, and composer.
- The widget sends `selected_department`, `selected_topic`, `source_domain`, `language`, `page_url`, and `widget_variant=safe_pro_sidebar` to the backend.
- The frontend does not call Anthropic directly, expose keys, own the system prompt, create CRM records, or hardcode official sensitive facts.
- Actual embed remains blocked until approvals, final asset URL, backend redeploy for department routing, and real-domain smoke are complete.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_PRO_SIDEBAR_WIDGET_FUNCTIONAL_READY_PENDING_REDEPLOY_AND_SITE_EMBED

## Phase 9D-Redeploy Gate Update

Status: NO-GO remains in effect.

Phase 9D was redeployed with image `v0.9-department-routing-sidebar`, and endpoint health checks passed. However, department routing smoke failed two sidebar ambiguity cases:

- Finance sidebar + ambiguous details message routed to Admissions.
- Medicine sidebar + ambiguous details message routed to Admissions.

Finance no-contact and broader knowledge smoke tests still passed, and no production contact details or intentional CRM records were created.

Actual embed remains blocked until the ambiguous sidebar routing bug is fixed, redeployed, and smoke verified.

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```

## Phase 9E-Redeploy Routing Gate Update

The backend department routing blocker from Phase 9D has been resolved in production.

- Image tag: `v0.9-sidebar-ambiguous-routing-fix`
- New revision: `alte-ai-crm-backend-00006-vs5`
- Department routing sidebar smoke: 28/28 passed
- Finance ambiguous sidebar case: PASS
- Medicine ambiguous sidebar case: PASS
- Finance no-contact smoke: 24/24 passed
- Broader knowledge smoke final run: 25/25 passed

Pre-embed status remains NO-GO because these items are still pending:

- Human reviewer decisions
- Official content approval
- Privacy/data approval
- Final widget asset URL
- Actual site embed
- Real-domain browser smoke

Decision state:

```text
BACKEND_DEPLOYED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```

## Phase 9F Content Approval Gate Update

Conservative content decisions have been prepared, but official human approval remains pending.

- Conservative CSV: `docs/reviewer_package/alte_kb_conservative_decisions_for_approval.csv`
- `APPROVE`: 67
- `HANDOVER_ONLY`: 10
- `NEEDS_OFFICIAL_SOURCE`: 570
- High sensitivity rows: 379
- Production DB modified: NO
- `apply --apply` run: NO
- Public launch approved: NO

Pre-embed status remains NO-GO until human/official approval, privacy approval, final asset URL, actual site embed, and real-domain browser smoke are complete.

Decision state:

```text
BACKEND_DEPLOYED_CONTENT_DECISIONS_PREPARED_PENDING_HUMAN_APPROVAL
```

## Phase 9G-H Pre-Embed Package Update

The final pre-embed package now includes privacy/data approval material, consent wording, asset URL decision, embed snippets, rollback/runbook material, and real-domain smoke guidance.

- Privacy/data approval: PENDING
- Final asset URL: PENDING_FINAL_URL
- Actual site embed: NOT_EXECUTED
- Real-domain smoke: NOT_EXECUTED

The selected widget remains the Safe Pro Sidebar. Do not embed until privacy/content approval and final asset URL are complete.

Decision state:

```text
BACKEND_DEPLOYED_PRIVACY_AND_EMBED_PACKAGE_READY_PENDING_FINAL_APPROVALS
```

## Phase 9I Asset Hosting Update

Alte-controlled hosting was selected for the widget asset.

- Placeholder URL: `https://alte.edu.ge/assets/alte-ai-chat-widget.js`
- Asset package: `dist/widget/`
- Website developer handoff: `docs/embed_package/WEBSITE_DEVELOPER_HANDOFF_GEO.md`

Actual upload and site embed are still pending. Real-domain smoke is still pending.

Decision state:

```text
BACKEND_DEPLOYED_ASSET_HOSTING_SELECTED_ALTE_CONTROLLED_PENDING_UPLOAD_AND_SITE_EMBED
```

## Phase 9J Final Approval Gate

The final GO/NO-GO approval gate has been created and remains NO-GO.

- Final pre-site-embed status: `NO_GO_PENDING_FINAL_APPROVALS`
- Site embed approval record: pending
- Site embed GO/NO-GO checklist: pending approvals

Actual site embed and public launch are still blocked.

Decision state:

```text
BACKEND_DEPLOYED_FINAL_PRE_EMBED_GATE_READY_NO_GO_PENDING_APPROVALS
```
```
