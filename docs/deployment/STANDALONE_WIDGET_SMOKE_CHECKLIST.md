# Standalone Widget Smoke Checklist

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
