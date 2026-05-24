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

- [x] Open `widget/standalone-production-demo.html` locally for standalone sandbox testing.
- [ ] Open `widget/production-embed-test.html` locally or on staging.
- [ ] Verify chat bubble appears.
- [ ] Verify widget opens and closes.
- [ ] Verify language toggle works.
- [x] Verify backend API session starts outside browser CORS.
- [x] Verify backend API reply from Cloud Run outside browser CORS.
- [x] Verify production endpoint `/health: 200`.
- [x] Verify production endpoint `/version: 200`.
- [x] Verify production endpoint `/diagnostics/ai: 200`; Claude enabled; no secrets exposed.
- [x] Verify `https://alte.edu.ge` CORS preflight PASS.
- [x] Verify `https://join.alte.edu.ge` CORS preflight PASS.
- [x] Verify localhost browser CORS is blocked as expected: `http://127.0.0.1:5500` preflight FAIL `400`.
- [ ] Verify no secrets appear in browser console.
- [x] Verify consent text is visible in KA and EN.
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
- Standalone production demo prepared: `widget/standalone-production-demo.html`
- Standalone smoke checklist prepared: `STANDALONE_WIDGET_SMOKE_CHECKLIST.md`
- Transfer package prepared: `WIDGET_TRANSFER_TO_ALTE_SITE.md`
- Website admin/developer access: `PENDING`
- Privacy/data approval: `PENDING`
- Actual website widget embed: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`
- Production widget smoke: `PENDING`
- Standalone backend/API smoke: `PASSED`
- Production domain CORS: `PASSED`
- Localhost browser CORS: `BLOCKED_AS_EXPECTED`
- Real-domain browser widget smoke: `PENDING`
- Decision state: `BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE`
