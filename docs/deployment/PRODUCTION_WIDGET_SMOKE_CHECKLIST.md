# Production Widget Smoke Checklist

Use this checklist after website admin/developer access and privacy approval are complete.

Do not create production test leads unless the owner approves test records.

## Before Embed

- [ ] Backend URL confirmed: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- [ ] `/health: 200`
- [ ] `/diagnostics/ai: 200`
- [ ] CORS includes `https://alte.edu.ge`
- [ ] CORS includes `https://join.alte.edu.ge`
- [ ] Widget asset URL finalized.
- [ ] Privacy policy URL finalized.
- [ ] Consent text approved.
- [ ] Rollback/removal owner assigned.

## A. Staging / Test Page Smoke

- [ ] Open `widget/production-embed-test.html` locally or on staging.
- [ ] Verify chat bubble appears.
- [ ] Verify widget opens and closes.
- [ ] Verify language toggle works.
- [ ] Verify session starts.
- [ ] Verify reply from Cloud Run.
- [ ] Verify no CORS error.
- [ ] Verify no secrets appear in browser console.
- [ ] Verify consent text is visible.
- [ ] Verify `alte.edu.ge` source domain mode.
- [ ] Verify `join.alte.edu.ge` source domain mode.

## B. Real Website Smoke

Only after website/privacy approval.

- [ ] Embed on a test page or hidden page first.
- [ ] Verify widget appears.
- [ ] Verify page layout is unaffected.
- [ ] Verify configured domain/sourceDomain.
- [ ] Verify one safe message.
- [ ] Verify operator inbox if allowed.
- [ ] Verify rollback procedure.

## C. alte.edu.ge Smoke

- [ ] Embed uses `sourceDomain: "alte.edu.ge"`.
- [ ] Embed uses `defaultLanguage: "ka"`.
- [ ] Widget button appears.
- [ ] Widget opens and closes.
- [ ] Georgian quick replies render.
- [ ] Consent line is visible.
- [ ] General contact question returns safe answer.
- [ ] Tuition/deadline question does not invent exact price/date.
- [ ] Human handover path is available.

## D. join.alte.edu.ge Smoke

- [ ] Embed uses `sourceDomain: "join.alte.edu.ge"`.
- [ ] Embed uses `defaultLanguage: "en"`.
- [ ] Widget button appears.
- [ ] Widget opens and closes.
- [ ] English quick replies render.
- [ ] International admissions question routes safely.
- [ ] Medicine/international question uses high-sensitivity handover behavior where needed.
- [ ] Human handover path is available.

## Rollback Check

- [ ] Removing both script tags removes the widget.
- [ ] Setting `proactiveEnabled: false` disables proactive prompt.
- [ ] No JavaScript console errors remain after removal.
- [ ] No layout shift remains after removal.

## Current Status

- Widget asset prepared: `alte-chat-widget.v0.8.js`
- Final snippets prepared: `WIDGET_EMBED_SNIPPETS_FINAL.md`
- Developer handoff prepared: `WEBSITE_DEVELOPER_HANDOFF.md`
- Staging/test page prepared: `widget/production-embed-test.html`
- Website admin/developer access: `PENDING`
- Privacy/data approval: `PENDING`
- Actual website widget embed: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`
- Production widget smoke: `PENDING`
