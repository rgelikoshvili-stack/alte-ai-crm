# Pro v2 ZIP Source Audit

PRO_V2_ZIP_SOURCE_AUDIT_STATUS=COMPLETED_SOURCE_OF_TRUTH

## Source

Uploaded ZIP: `C:\Users\Acer\Downloads\სრული ვერსია.zip`

Evidence path:

`docs/knowledge_evidence/uploaded_pro_v2_zip_source/`

The ZIP contains actual source JSX/CSS, not only a bundled standalone HTML.

## Main Source Files

- `deploy/variants/pro-v2-chat.jsx` - exact chat widget layout, CSS, state, interactions, floating/expanded window behavior, sidebar, composer, message renderers.
- `deploy/variants/pro-v2-page.jsx` - demo/test page background and launcher context.
- `deploy/variants/pro-v2-strings.jsx` - departments, labels, quick replies, copy, placeholders.
- `deploy/variants/pro-v2-icons.jsx` - icon system.
- `deploy/variants/pro-v2-modals.jsx` - settings and contact/lead modals.
- `deploy/variants/tweaks-panel.jsx` - demo tweaking panel, not needed for production widget.

## Unsafe Source Logic

- `deploy/api/chat.js` proxies to Anthropic using `ANTHROPIC_API_KEY`.
- `deploy/index.html` defines `window.claude.complete` and calls `/api/chat`.
- `pro-v2-chat.jsx` uses `window.claude.complete` for direct model completion behavior.
- `pro-v2-strings.jsx` contains demo/system prompt text and hardcoded factual examples.

These parts are reference-only and must not be copied into the safe production/test widget.

## Safe Port Rule

The final widget must keep the Pro v2 visual and interaction structure, while replacing all Vercel/Claude/browser AI logic with the existing Alte FastAPI backend:

- `POST /chat/session/start`
- `POST /chat/message`

No frontend API keys, direct provider calls, or frontend CRM creation are allowed.
