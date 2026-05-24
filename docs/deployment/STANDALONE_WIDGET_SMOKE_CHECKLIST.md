# Standalone Widget Smoke Checklist

## Phase 9B Safe Pro Preview

Safe Pro standalone preview:

```text
widget/standalone-safe-pro-demo.html
```

Notes:

- Localhost browser requests may be blocked by production CORS.
- API smoke should continue to use backend scripts.
- Real-domain browser smoke remains pending.
- The safe Pro widget must not call Anthropic directly from the browser.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_CANDIDATE_READY_PENDING_REVIEW_AND_SITE_EMBED
```
Use this checklist with:

```text
widget/standalone-production-demo.html
```

The page uses the production backend:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Checklist

- [x] Local static server starts.
- [x] `standalone-production-demo.html` loads.
- [x] Widget JS loads.
- [ ] Chat bubble appears.
- [ ] Domain selector works.
- [ ] KA behavior works for `alte.edu.ge`.
- [ ] EN behavior works for `join.alte.edu.ge`.
- [x] `/health` link opens: production endpoint returned `200`.
- [x] `/version` link opens: production endpoint returned `200`.
- [x] `/diagnostics/ai` link opens: production endpoint returned `200`; Claude enabled; no secrets exposed.
- [x] Backend API smoke sends safe messages outside browser CORS:
  - `alte.edu.ge` / `ka`: PASS
  - `join.alte.edu.ge` / `en`: PASS
- [x] Reply received through backend API smoke.
- [x] `https://alte.edu.ge` CORS preflight PASS.
- [x] `https://join.alte.edu.ge` CORS preflight PASS.
- [x] `http://127.0.0.1:5500` browser CORS preflight FAIL `400` as expected because localhost is not in production CORS.
- [ ] No secrets visible in browser console/network.
- [x] Consent text visible in KA and EN.
- [ ] Contact-data test only if approved.
- [ ] CRM side effect verification only if approved.
- [ ] Real browser smoke from allowed Alte domains.

## Current State

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE
```

Actual Alte website embed remains pending.

## Safe Uploaded UI Smoke

Additional standalone page:

```text
widget/alte-university-ai-chatbot-safe.html
```

- [x] Original uploaded UI copied as evidence.
- [x] Direct browser Anthropic call removed in safe version.
- [x] Safe version uses `/chat/session/start`.
- [x] Safe version uses `/chat/message`.
- [x] Safe version uses production FastAPI backend URL.
- [ ] Browser chat from localhost may be blocked by production CORS, as expected.
- [ ] Real-domain browser smoke remains pending.
