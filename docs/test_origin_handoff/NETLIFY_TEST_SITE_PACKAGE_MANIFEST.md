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
| `index.html` | `63680918ECA04C138B83F9B555FA150A6D8376D9DCD6198084D757A57E91E4E0` |
| `join.html` | `E2B3BAB38E99CDB8C5FC90FD01FBC870D5A70B57B0F8996EFCA9AF42C8879538` |
| `alte-ai-chat-widget.js` | `A5083446ADE39513D77969115FE0CEF21A4BF8EF3F588551BC87EFDD4E2C2B73` |
| `alte-ai-chat-widget.html` | `5BE7677CB000B3EA5F0427B77FD270C788302DF26C75EE0229B509B280696977` |
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
- Phase 9Q-9R rebuild included:
  modal layout, reset/expand/close, sidebar collapse, settings panel, disabled attachment/voice controls, keyboard Enter handling, source card renderer, and handover/contact renderers.
- Phase 9S exact ZIP source port included:
  `.cw-win`, `.cw-win.expanded`, `.cw-backdrop`, `.cw-side`, `.cw-side.collapsed`, `.cw-comp`, quick replies/chips, settings, expand, and close markers are present in the deployed HTML.
- Phase 9S event binding fix included:
  `cw-attach` and `cw-voice` are mapped, and widget controls use guarded `on(...)` event binding so missing optional controls do not crash initialization.

## Phase 9S SHA256

| File | SHA256 |
| --- | --- |
| `widget/alte-ai-chatbot-pro-v2-safe.html` | `5BE7677CB000B3EA5F0427B77FD270C788302DF26C75EE0229B509B280696977` |
| `test_site/alte-ai-chat-widget.js` | `A5083446ADE39513D77969115FE0CEF21A4BF8EF3F588551BC87EFDD4E2C2B73` |
| `dist/widget/alte-ai-chat-widget.js` | `A5083446ADE39513D77969115FE0CEF21A4BF8EF3F588551BC87EFDD4E2C2B73` |
| `dist/netlify_test_site_deploy.zip` | `38116E30930EF79D6B3EAB55DAB3FCD8DF27085E656EA6F5498DA5EE7750ADCD` |

## Deployment Status

- Netlify CLI deploy executed: NO
- Manual/Git redeploy required: YES
- Browser smoke passed: NO
