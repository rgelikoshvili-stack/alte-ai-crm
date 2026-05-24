# Widget Transfer To Alte Site

## Phase 9B Safe Pro Candidate

Uploaded widget design concepts were imported and reviewed. The safe production candidate is:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

Use it only after final asset hosting, privacy/data approval, official content approval, actual site embed approval, and real-domain browser smoke.

The candidate uses only the production FastAPI backend:

- `POST /chat/session/start`
- `POST /chat/message`

Direct browser Anthropic calls are forbidden. The frontend must not create leads or own chatbot business rules.

Decision state:

```text
BACKEND_DEPLOYED_SAFE_PRO_WIDGET_CANDIDATE_READY_PENDING_REVIEW_AND_SITE_EMBED
```
Current state:

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED
```

Actual embed remains blocked until website admin/developer access and privacy/data approval are confirmed.

## Backend URL

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Widget Asset

```text
alte-chat-widget.v0.8.js
```

Recommended upload location:

```text
Website/CMS static asset hosting
```

The website developer should upload the JS file to an approved static asset location and provide the final URL.

## alte.edu.ge Snippet

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    proactiveEnabled: true,
    proactiveDelayMs: 30000
  };
</script>
<script src="https://YOUR_FINAL_WIDGET_ASSET_URL/alte-chat-widget.v0.8.js"></script>
```

## join.alte.edu.ge Snippet

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    proactiveEnabled: true,
    proactiveDelayMs: 5000
  };
</script>
<script src="https://YOUR_FINAL_WIDGET_ASSET_URL/alte-chat-widget.v0.8.js"></script>
```

## Hidden/Staging Page First

- Add the snippet to a hidden/staging page first.
- Verify the widget loads.
- Verify no JavaScript console errors.
- Verify no CORS errors.
- Verify source domain and default language.
- Verify one safe non-contact message.
- Do not enter contact data unless production test records are approved.

## Browser Console Checks

- No API key values.
- No database connection strings.
- No DB password.
- No failed widget asset request.
- No CORS error for Cloud Run backend.

## Privacy / Consent

Consent text:

```text
საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის.
We use your contact details only to provide consultation.
```

The final website should include the approved Alte privacy policy link when available.

## Rollback

- Remove both script tags.
- Remove or replace the widget asset.
- Set `proactiveEnabled: false` if only proactive prompt needs to be disabled.
- Clear CMS/CDN cache.
- Confirm no layout issue remains.

## Blockers

- Website admin/developer access pending.
- Privacy/data approval pending.
- Final widget asset URL pending.
- Actual website embed pending.
- Production website smoke pending.

## Phase 8N Approval Gate

The transfer package is ready, but the real embed remains blocked until these documents are approved:

- `WEBSITE_EMBED_APPROVAL_GATE.md`
- `PRIVACY_CONSENT_APPROVAL.md`
- `FINAL_WIDGET_EMBED_GO_NO_GO.md`
- `WIDGET_FINAL_ASSET_URL_DECISION.md`

Current decision:

```text
BACKEND_DEPLOYED_WIDGET_READY_PENDING_WEBSITE_PRIVACY_APPROVAL
```

## Phase 8Z Safe Uploaded UI

The uploaded `alte_university_ai_chatbot.html` demo was converted into a safe backend-connected standalone UI:

```text
widget/alte-university-ai-chatbot-safe.html
```

The converted UI keeps the useful visual pattern, including department navigation, KA/EN switch, message bubbles, handover display, and backend source display. It removes the unsafe browser Anthropic call and uses the production FastAPI backend as the source of truth.

Do not transfer the original uploaded file to the real website. Transfer only the safe backend-connected widget/page or the existing production widget asset after final review.
