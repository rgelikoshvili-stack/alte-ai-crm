# Exact Safe Pro Sidebar UI Decision

## Decision

The user explicitly selected the exact Pro Sidebar layout from the uploaded design ZIP/screenshots as the final preferred chatbot UI.

The compact/PIP layout is archived and is not the primary widget.

Selected file:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

Archived alternate:

```text
widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html
```

## Reason

- Sidebar department navigation is required functionality, not decoration.
- Department navigation is central to the product goal.
- Selected department context helps backend AI routing and fallback/handover decisions.
- Unknown, low-confidence, source-missing, or sensitive answers can route to the correct operator.
- The sidebar layout better matches the uploaded Pro design concept.
- The layout supports KA/EN, active department highlighting, department badges, quick chips, source display, contact request UI, and operator handover cards.

## Architecture

Safe architecture is preserved:

```text
browser widget -> FastAPI backend -> Claude -> Knowledge Base -> CRM business rules
```

The frontend sends context only:

- `selected_department`
- `selected_topic`
- `source_domain`
- `language`
- `page_url`
- `widget_variant=safe_pro_sidebar`

The frontend does not:

- call Anthropic directly;
- expose API keys;
- hardcode tuition, deadlines, or official facts as final truth;
- own the production system prompt;
- create leads/tasks/customers;
- decide CRM actions.

## Functional Requirements Implemented

- Left sidebar with department list.
- Right-side chat area with header, trust/source bar, message bubbles, quick chips, composer, source cards, contact request card, and handover/operator card.
- Sidebar clicks set `selected_department` and `selected_topic`.
- Quick chips send selected department/topic context to the backend.
- Human Operator sends a human request to backend with the active department context.
- Fallback/handover UI uses backend department fields first, then selected sidebar department.

## Visual Parity Refinement

The widget was refined again to match the uploaded Pro screenshot more closely:

- compact app-shell proportions similar to the Pro preview;
- cream left sidebar with approximately 200px department navigation;
- white chat area with compact header, KA/EN controls, trust bar, message bubbles, and composer;
- smaller Pro-style typography, spacing, icon cells, borders, and operator/source cards;
- the compact/PIP visual direction remains archived as alternate, not primary.

## Status

Actual embed and public launch remain pending.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_PRO_SIDEBAR_WIDGET_FUNCTIONAL_READY_PENDING_REDEPLOY_AND_SITE_EMBED
```
