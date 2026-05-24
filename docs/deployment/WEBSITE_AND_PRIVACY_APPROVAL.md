# Website And Privacy Approval

## A. Website Access

- [ ] `alte.edu.ge` developer/admin access confirmed.
- [ ] `join.alte.edu.ge` developer/admin access confirmed if needed.
- [ ] Script injection location identified.
- [ ] Staging page or test page identified.
- [x] Rollback/removal plan for widget snippet documented in `WEBSITE_WIDGET_PRODUCTION_EMBED.md`.

## B. Widget Production Config

- `apiBaseUrl = Cloud Run service URL`
- `sourceDomain = alte.edu.ge` or `join.alte.edu.ge`
- `defaultLanguage = ka` for `alte.edu.ge`
- `defaultLanguage = en` for `join.alte.edu.ge`
- `proactiveEnabled` approved: yes/no
- `proactiveDelayMs` approved: pending

## C. Privacy / Consent

- [ ] Consent text approved.
- [ ] Privacy policy link confirmed.
- [ ] Contact data usage approved.
- [ ] Retention policy owner identified.
- [ ] GDPR/privacy owner approval.
- [ ] Student data handling approved.

## D. Status

- Website access status: `PENDING`
- Privacy approval status: `PENDING`
- Actual embed status: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`
- Widget asset hosting choice: `Option A - Website/CMS static asset hosting`
- Final widget asset URL: `PENDING`
- Privacy policy URL: `PENDING`
- Consent text approval: `PENDING`
- Rollback/removal owner: `PENDING`

## Phase 8J Preparation Status

- Production embed guide: `WEBSITE_WIDGET_PRODUCTION_EMBED.md`
- Production smoke checklist: `PRODUCTION_WIDGET_SMOKE_CHECKLIST.md`
- Alte config example: `widget/production-config.alte.example.js`
- Join config example: `widget/production-config.join.example.js`
- Widget asset hosting decision: `WIDGET_ASSET_HOSTING_DECISION.md`
- Final snippets: `WIDGET_EMBED_SNIPPETS_FINAL.md`
- Website developer handoff: `WEBSITE_DEVELOPER_HANDOFF.md`
- Staging/test page: `widget/production-embed-test.html`
- Actual website widget embed pending.
- Production widget smoke pending.

## Phase 8N Approval Gate

- Website embed approval gate: `WEBSITE_EMBED_APPROVAL_GATE.md`
- Privacy consent approval: `PRIVACY_CONSENT_APPROVAL.md`
- Final widget embed go/no-go checklist: `FINAL_WIDGET_EMBED_GO_NO_GO.md`
- Final asset URL decision: `WIDGET_FINAL_ASSET_URL_DECISION.md`
- Current decision state: `BACKEND_DEPLOYED_WIDGET_READY_PENDING_WEBSITE_PRIVACY_APPROVAL`
- Actual site embed remains blocked.
- Real-domain smoke remains pending.
