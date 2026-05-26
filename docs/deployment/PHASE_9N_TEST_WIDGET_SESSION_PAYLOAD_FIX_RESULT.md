# Phase 9N Test Widget Session Payload Fix Result

PHASE_9N_TEST_WIDGET_SESSION_PAYLOAD_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY

## Issue

The hosted Netlify widget page loaded and the Safe Pro Sidebar widget was visible, but the browser console showed:

```text
POST /chat/session/start failed with status 422
```

## Root Cause

The backend schema for `POST /chat/session/start` expects:

```json
{
  "channel": "website_chat",
  "source_domain": "alte.edu.ge",
  "language": "ka"
}
```

The widget HTML was sending:

```json
{
  "channel": "website"
}
```

`channel` is validated as a literal value, so `"website"` caused a `422` validation error.

## Fixed Payload Fields

- `channel`: changed to `website_chat`
- `source_domain`: preserved from widget config
- `language`: preserved from active widget language
- `selected_department` / `selected_topic`: preserved for `/chat/message`
- frontend lead/task/customer creation: not added
- direct AI provider browser calls: not added

## Files Changed

- `test_site/alte-ai-chat-widget.html`
- `dist/widget/alte-ai-chat-widget.html`
- `widget/alte-university-ai-chatbot-safe-pro.html`
- `test_site/alte-ai-chat-widget.js`
- `dist/netlify_test_site_deploy.zip`
- `docs/test_origin_handoff/NETLIFY_TEST_SITE_PACKAGE_MANIFEST.md`
- `backend/app/scripts/test_site_session_payload_smoke.py`

## Session Payload Smoke Result

Command:

```powershell
python -m app.scripts.test_site_session_payload_smoke
```

Result:

- total tests: 2
- passed: 2
- failed: 0
- no contact details sent: true
- contact-flow test run: false
- intentional lead/task/customer creation: false

## Deployment Status

- Netlify redeploy required: YES
- Deploy package: `dist/netlify_test_site_deploy.zip`
- Browser smoke status: `PENDING_REDEPLOY_AND_MANUAL_RETEST`

Do not mark hosted browser smoke passed until Netlify is redeployed and manual browser retest confirms the session starts successfully.
