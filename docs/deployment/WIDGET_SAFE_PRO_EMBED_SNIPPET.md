# Safe Pro Widget Embed Snippet

Status: prepared for later site integration only.

Do not embed this widget on `alte.edu.ge` or `join.alte.edu.ge` until official content review, privacy/data approval, final asset hosting URL, actual site embed approval, and real-domain browser smoke are complete.

## Backend

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

The widget must call only the FastAPI backend:

- `POST /chat/session/start`
- `POST /chat/message`

Direct browser calls to Anthropic are forbidden.

## Candidate Asset

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

The current candidate is a standalone HTML widget. For production, host it as a reviewed static asset on an approved Alte-controlled domain or approved static asset location.

## Example Iframe Embed

Replace `https://assets.example.alte.edu.ge/widget/alte-university-ai-chatbot-safe-pro.html` with the final approved asset URL.

```html
<iframe
  src="https://assets.example.alte.edu.ge/widget/alte-university-ai-chatbot-safe-pro.html"
  title="Alte AI Chatbot"
  style="position:fixed;right:0;bottom:0;width:430px;height:720px;border:0;z-index:9999;background:transparent;"
  loading="lazy"
></iframe>
```

## Source Domain Examples

For the main Alte site:

```js
window.AlteChatWidgetConfig = {
  apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
  sourceDomain: "alte.edu.ge",
  defaultLanguage: "ka"
};
```

For the admissions site:

```js
window.AlteChatWidgetConfig = {
  apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
  sourceDomain: "join.alte.edu.ge",
  defaultLanguage: "en"
};
```

## Pending Before Embed

- Human reviewer decisions.
- Official content approval.
- Privacy/data approval.
- Final widget asset URL.
- Actual website embed approval.
- Real-domain browser smoke from `alte.edu.ge` and `join.alte.edu.ge`.

## Phase 9D-UI Sidebar Decision

The preferred widget UI is now the Safe Pro Sidebar Layout:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

The compact PIP version is archived as an alternate:

```text
widget/archive/alte-university-ai-chatbot-safe-pro-pip-archive.html
```

The sidebar widget sends `selected_department`, `selected_topic`, and `widget_variant=safe_pro_sidebar` to the backend.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_SIDEBAR_WIDGET_READY_PENDING_REDEPLOY_AND_SITE_EMBED
```

## Phase 9C Gate

This snippet remains a draft until:

- `FINAL_PRE_EMBED_STATUS=NO_GO_PENDING_APPROVALS` is replaced by an explicit GO approval in a later phase.
- `WIDGET_ASSET_HOSTING_STATUS=PENDING_FINAL_URL` is replaced by a final URL.
- `PRIVACY_DATA_APPROVAL_STATUS=PENDING` is approved.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_PRE_EMBED_GATE_READY_PENDING_APPROVALS
```
