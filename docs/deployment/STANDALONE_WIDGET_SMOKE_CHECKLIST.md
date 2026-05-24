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

- [ ] Local static server starts.
- [ ] `standalone-production-demo.html` loads.
- [ ] Widget JS loads.
- [ ] Chat bubble appears.
- [ ] Domain selector works.
- [ ] KA behavior works for `alte.edu.ge`.
- [ ] EN behavior works for `join.alte.edu.ge`.
- [ ] `/health` link opens.
- [ ] `/version` link opens.
- [ ] `/diagnostics/ai` link opens.
- [ ] Message sends to production backend.
- [ ] Reply received.
- [ ] No CORS error.
- [ ] No secrets visible in browser console/network.
- [ ] Consent text visible.
- [ ] Contact-data test only if approved.
- [ ] CRM side effect verification only if approved.

## Current State

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED
```

Actual Alte website embed remains pending.
