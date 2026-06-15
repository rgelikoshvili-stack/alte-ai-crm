# Phase 9CC Real Site Embed Plan No Execution

Date: 2026-06-15

Branch: `phase-9s-agent-preview-cors-note`

Decision: `REAL_SITE_EMBED_PLAN_READY_NO_EXECUTION_PUBLIC_LAUNCH_NO_GO`

Public launch: `NO-GO`

## Source Documents And Local Artifacts

- `docs/deployment/PHASE_9CA_LAUNCH_APPROVAL_GATES_REFRESH.md`: FOUND
- `docs/deployment/PHASE_9CB_PRIVACY_LEGAL_CONTACT_FLOW_APPROVAL_PACKAGE.md`: FOUND
- `docs/deployment/PHASE_9BZ_POST_DEPLOY_FINAL_AUDIT_AND_APPROVAL_GATES.md`: FOUND
- `docs/deployment/PHASE_9AZ_FINAL_APPROVAL_PACKAGE.md`: NOT_FOUND
- `docs/deployment/WIDGET_EMBED_SNIPPETS_FINAL.md`: FOUND
- `docs/deployment/WIDGET_FINAL_ASSET_URL_DECISION.md`: FOUND
- `docs/deployment/WIDGET_ASSET_HOSTING_DECISION.md`: FOUND
- `docs/deployment/CORS_AND_WIDGET_ORIGINS.md`: FOUND
- `docs/deployment/REAL_DOMAIN_WIDGET_SMOKE_PLAN.md`: FOUND
- `docs/deployment/WIDGET_EMBED_ROLLBACK_PLAN.md`: FOUND
- `widget/alte-chat-widget.v0.8.js`: FOUND
- `widget/production-config.alte.example.js`: FOUND
- `widget/production-config.join.example.js`: FOUND

No site embed, asset upload, Netlify change, CORS change, deploy, rollback, or contact-flow execution was performed in this phase.

## A. Current Backend Endpoint

Backend API base URL:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

Production backend:

- Revision: `alte-ai-crm-backend-00054-m6r`
- Traffic: `100%`
- Health: PASS, HTTP 200
- Image tag: `v0.9-phase-9by-calendar-hotfix`
- Image digest: `sha256:b456378796a91c2ca2140935affbcdc0bd7edabc18b3a694e8a25761e9234fb3`
- Rollback target: `alte-ai-crm-backend-00053-pbz`

Public launch:

- `NO-GO`

## B. Candidate Embed Approach

Recommended approach:

- Host the reviewed widget JavaScript asset as a versioned static asset controlled by the Alte web team.
- Embed a small configuration block before the widget script tag on approved pages.
- Use only the public backend API base URL in browser config.
- Do not expose API keys, tokens, database URLs, Secret Manager values, service-account data, or private operator credentials in frontend code.

Candidate widget asset:

```text
widget/alte-chat-widget.v0.8.js
```

Candidate production asset URL placeholder:

```text
https://APPROVED_ASSET_HOST/alte-chat-widget.v0.8.js
```

Candidate pages:

- `https://alte.edu.ge` homepage or approved Georgian admissions/program page.
- `https://join.alte.edu.ge` homepage or approved English/international admissions landing page.
- Any final page must be approved by the owner and web team before embed.

Candidate `alte.edu.ge` snippet:

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
<script src="https://APPROVED_ASSET_HOST/alte-chat-widget.v0.8.js"></script>
```

Candidate `join.alte.edu.ge` snippet:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    proactiveEnabled: true,
    proactiveDelayMs: 30000
  };
</script>
<script src="https://APPROVED_ASSET_HOST/alte-chat-widget.v0.8.js"></script>
```

Optional admissions landing-page change:

- `proactiveDelayMs: 5000` may be used only after owner/web/privacy approval.

Required frontend config:

- `apiBaseUrl`
- `sourceDomain`
- `defaultLanguage`
- `proactiveEnabled`
- `proactiveDelayMs`
- final approved script asset URL

Do not expose in frontend:

- Anthropic/OpenAI/API keys.
- `DATABASE_URL`.
- JWT secrets.
- Secret Manager resource values.
- Service-account keys.
- Operator/admin credentials.
- Private CRM/customer/lead/task data.

## C. Asset Hosting Plan

Preferred host:

- Alte website/CMS/static asset hosting controlled by the web team.

Acceptable later alternative:

- Approved static asset host such as Cloud Storage/CDN only after a separate owner-approved hosting decision.

Versioning strategy:

- Keep the current launch candidate as `alte-chat-widget.v0.8.js`.
- If a launch-window change is needed, publish a new versioned filename instead of overwriting the current asset.
- Embed the exact versioned URL in the real site snippet.
- Record the deployed asset URL in the final launch execution record.

Rollback asset version:

- Remove the script snippet, or replace the script URL with the previous approved version if one exists.
- Keep the previous real-site page/CMS revision available through the web team's rollback workflow.

No asset upload was performed in Phase 9CC.

## D. CORS And Domain Checklist

Candidate production origins:

```text
https://alte.edu.ge
https://join.alte.edu.ge
```

Current docs indicate these are the intended production widget origins. Any final smoke must verify that browser requests from the actual embedded page receive the expected CORS response.

Checklist before real embed:

- Confirm exact final page origins, including `www` or non-`www` variants if used by the real site.
- Confirm the widget asset host does not require backend CORS changes.
- Confirm backend API calls originate only from approved production origins.
- Confirm no wildcard `*` is used for production CORS.
- Confirm no frontend code calls third-party AI providers directly.

Warning:

- Do not change CORS in Phase 9CC.
- Any CORS allowlist update requires separate explicit approval and backend deployment/change control if needed.

## E. Privacy And Consent Dependency

Real-site embed must wait for Phase 9CB privacy/contact-flow approvals.

Requirements before public launch:

- Approved public privacy notice and URL/location.
- Approved consent wording before phone/email submission.
- Approved data retention and deletion/correction process.
- Approved operator/admin access scope.
- Approved contact-flow behavior if contact form is enabled.
- Approved no-spam/no-unwanted-contact wording.

Contact-flow rule:

- The widget may not write real contacts, customers, leads, or tasks until owner/legal approval is recorded.
- Safe no-write chat smoke can be approved separately, but must not include real contact data or contact creation.

## F. Real-Domain Smoke Test Plan

Run these tests only after owner/web-team approval and after the widget is embedded on an approved real-domain page.

| Test | Expected result | Contact-write behavior |
| --- | --- | --- |
| Page loads with widget | No layout break, no console error, widget button visible | No write |
| Open/close widget | Widget opens and closes on desktop/mobile | No write |
| Backend health/API reachability | Widget can call backend through approved origin | No write |
| Safe Georgian question | `alte.edu.ge` returns a grounded Georgian answer | No contact data |
| Safe English question | `join.alte.edu.ge` returns a grounded English answer | No contact data |
| Source display | Public source labels render safely without internal source noise | No write |
| Academic Calendar question | 9BE calendar behavior remains correct | No write |
| 9BF Georgian control topic | No unwanted Georgian contact prompt or routing regression | No write |
| 9BG source display safety | No private source labels or backend internals displayed | No write |
| Contact form visibility | Consent and privacy wording visible before phone/email collection | No write unless separately approved |
| Rollback test | Removing script restores page without widget artifacts | No write |

Do not run real contact creation in real-domain smoke unless contact-flow and real-write approval are explicitly recorded.

## G. Rollback Plan

Website rollback:

- Remove the widget config script tag.
- Remove the widget asset script tag.
- Revert the CMS/page revision if the web team uses versioned page history.
- Clear website/CDN cache if required.
- Verify the page loads without the widget and without console errors.

Asset rollback:

- Revert to the prior approved asset URL if one exists.
- Or remove the script tag completely.

Backend rollback readiness:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions alte-ai-crm-backend-00053-pbz=100 --quiet
```

DB rollback:

- No DB rollback is expected for embed-only launch if contact-flow writes remain disabled/not approved.
- If real contact-flow writes are later approved, the launch plan must include explicit data-handling and rollback guidance for any test/customer/lead/task records.

## H. Approval Checklist

Required before any real-site embed:

- Final owner approval.
- Web-team approval for exact pages and CMS/deployment method.
- Asset-hosting approval and final asset URL.
- Privacy/legal approval.
- Consent wording approval.
- Contact-flow approval if contact form is enabled.
- Real contact write approval before any production contact/customer/lead/task write.
- CORS approval if any domain allowlist change is needed.
- Real-domain smoke approval.
- Rollback owner and rollback command sign-off.
- Support/operator handoff approval.
- Final public launch approval.

## I. Decision

`REAL_SITE_EMBED_PLAN_READY_NO_EXECUTION_PUBLIC_LAUNCH_NO_GO`

This phase prepared the owner/web-team embed plan only. Real-site embed, asset upload, CORS changes, frontend/Netlify changes, contact-flow execution, and public launch remain blocked pending explicit approval.

## Safety Confirmations

- Backend deploy performed in this phase: NO
- Rollback performed in this phase: NO
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS changed: NO
- Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Public launch marked GO: NO
