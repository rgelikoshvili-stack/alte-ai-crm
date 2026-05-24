# Safe Pro Sidebar UI Decision

## Decision

The preferred final widget UI is the Safe Pro Sidebar Layout, not the compact PIP layout.

Selected file:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

Archived alternate:

```text
widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html
```

## Reason

- Department navigation is central to the product goal.
- Selected department context helps backend AI routing and fallback/handover decisions.
- Unknown, low-confidence, source-missing, or sensitive answers can route to the correct operator.
- The sidebar layout better matches the uploaded Pro design concept.
- The layout supports KA/EN, active department highlighting, source display, contact request UI, and operator handover cards.

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
- own the production system prompt;
- create leads/tasks/customers;
- decide CRM actions.

## Status

Actual embed and public launch remain pending.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_SIDEBAR_WIDGET_READY_PENDING_REDEPLOY_AND_SITE_EMBED
```
