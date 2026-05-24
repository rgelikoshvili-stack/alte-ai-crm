# Widget Design Concepts Review

## Source

- Source ZIP: `დიზაინი.zip`
- Imported to: `docs/knowledge_evidence/uploaded_widget_design_concepts/`

## Extracted Files

- `Alte AI Chat - Concepts.html`
- `design-canvas.jsx`
- `variants/pip.jsx`
- `variants/bento.jsx`
- `variants/bigtalk.jsx`
- `variants/pro.jsx`
- `previews/*.png`
- `uploads/alte_university_ai_chatbot.html`
- uploaded preview images

## Variants Found

- `pip`: compact floating helper widget
- `bento`: modern topic-card layout
- `bigtalk`: larger playful assistant view
- `pro`: professional sidebar and department layout

## Security Assessment

The design files are UI references only.

Findings:

- `uploads/alte_university_ai_chatbot.html` contains a direct browser request to `https://api.anthropic.com/v1/messages`.
- `uploads/alte_university_ai_chatbot.html` contains an embedded `SYS` prompt and passes it as the browser-side message API system field.
- Variant JSX files include hardcoded demo facts such as an exact annual tuition example. Those values are visual mock content only and are not a production source of truth.
- No production widget may expose an Anthropic key, call Anthropic directly from the browser, or use a frontend prompt as the source of truth.

Safe production architecture remains:

```text
browser widget -> FastAPI backend -> Claude -> Knowledge Base -> CRM business rules
```

The backend remains the only AI/CRM integration point.

## Recommendation

For real `alte.edu.ge` embed, prefer a compact/lightweight widget. The PIP direction is the least intrusive and best suited to a public website because it uses a small launcher, narrow chat panel, and familiar chat behavior.

The Pro direction has useful visual ideas, especially department navigation and structured handover/source cards, but the full sidebar view is better for admin or standalone demos than a public website.

Recommendation:

- Primary production candidate: compact PIP-style widget with selected Pro polish.
- Stable baseline remains: `widget/alte-university-ai-chatbot-safe.html`
- New candidate: `widget/alte-university-ai-chatbot-safe-pro.html`

Public launch remains blocked until official content review, privacy/data approval, final widget asset URL, actual site embed, and real-domain browser smoke are complete.

## Phase 9B Status

The uploaded design concepts have been imported as evidence, and a safe production candidate has been created at `widget/alte-university-ai-chatbot-safe-pro.html`.

The candidate keeps the compact PIP-style embed direction and selected Pro-style polish, but it removes direct browser AI calls and uses only the FastAPI backend as the AI/CRM integration point.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_CANDIDATE_READY_PENDING_REVIEW_AND_SITE_EMBED
```
