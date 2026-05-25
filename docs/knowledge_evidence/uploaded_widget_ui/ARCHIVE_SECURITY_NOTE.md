# Uploaded Widget UI Archive Security Note

Files in this folder are historical evidence/reference only. They are not production assets and must not be copied into the live Alte website.

Some archived prototype files may contain unsafe prototype patterns, including direct browser calls to `api.anthropic.com`. That pattern is intentionally not allowed in production.

Production widget assets are:

- `widget/alte-university-ai-chatbot-safe-pro.html`
- `dist/widget/alte-ai-chat-widget.html`
- `dist/widget/alte-ai-chat-widget.js`

Production assets must not contain `api.anthropic.com`, `ANTHROPIC_API_KEY`, API keys, or secret values.
