# Netlify Test Site Package Manifest

Package path:

```text
dist/netlify_test_site_deploy.zip
```

## Included Files

ZIP root contains files directly, not under `test_site/`:

```text
index.html
join.html
alte-ai-chat-widget.js
alte-ai-chat-widget.html
_redirects
README_GEO.md
NETLIFY_DEPLOY_README_GEO.md
```

## SHA256

| File | SHA256 |
| --- | --- |
| `index.html` | `73CDE2CC2D9A9542D2DFFB97D573E9FBD372F598802E14A0F0E0A87E0F77E963` |
| `join.html` | `A9DD4B365D4F19EDDBAB47292F712F41B171A8AF40781E4B1ED37626663A1F08` |
| `alte-ai-chat-widget.js` | `0FBFA48F0F7424BFA5CDB7D3F8126475694AC48976F62A0278F5E4B8700314F2` |
| `alte-ai-chat-widget.html` | `3D4C33CBC6D6615DCECDE0823BE52860CAFDFD4C8232D5E02C3E9F888ADA1465` |
| `_redirects` | `47B45ECD4353A1E0921A7AD8E8B9B4A7CC8F77D5760B0B61EC6DB0703AE1F465` |

## Safety Scan

- `api.anthropic.com` absent from deploy assets.
- `ANTHROPIC_API_KEY` absent from deploy assets.
- `sk-ant-` absent from deploy assets.
- Production backend URL present:
  `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- `/chat/session/start` present.
- `/chat/message` present.
- `/chat/session/start` 422 payload fix included:
  session start now sends `channel: "website_chat"` to match backend schema.
- Pro v2 safe widget adaptation included:
  `widget_variant` defaults to `pro_v2_safe` and the test package includes the updated Pro v2 safe HTML.

## Deployment Status

- Netlify CLI deploy executed: NO
- Manual/Git redeploy required: YES
- Browser smoke passed: NO
