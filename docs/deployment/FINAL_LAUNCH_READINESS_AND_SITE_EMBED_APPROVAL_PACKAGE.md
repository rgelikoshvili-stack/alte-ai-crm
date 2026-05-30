# Final Launch Readiness And Site Embed Approval Package

FINAL_LAUNCH_READINESS_STATUS=NO_GO_PENDING_FINAL_SITE_EMBED_APPROVAL_AND_MANUAL_VISUAL_QA

Decision state:

```text
BACKEND_ROUTING_SOURCE_PRIORITY_PRODUCTION_VERIFIED_PENDING_SITE_EMBED_APPROVAL
```

## Scope

- Netlify test site: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Current verified Cloud Run revision: `alte-ai-crm-backend-00030-td7`
- Current verified backend image: `v0.9-routing-spec-source-priority3`
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Real contact creation flow executed: NO
- Public launch: NO-GO

## Verification Already Completed

Backend routing/source smoke, Netlify-origin mode:

- Command: `.\.venv\Scripts\python.exe -m app.scripts.production_phase_9u_official_kb_browser_origin_smoke`
- Result: `17 passed`, `0 failed`
- CORS exact Netlify origin: PASS
- No contact details sent: YES
- `/chat/handover` called: NO
- Intentional lead/task/customer creation: NO

Mandatory answer checks passed:

- Bachelor ECTS: `240`, not `180`
- Master ECTS: `120`
- Status suspension: `5` years
- Master's admission documents: official checklist
- Unsupported `2031` scholarship: `no_approved_source_found`
- AI policy: source-backed and conservative
- Current tuition / consultant phone / today's promotion: `no_approved_source_found`
- Operator request: no direct request to type name, phone, or email

Package verification scripts:

- `python -m app.scripts.verify_phase_9q_pro_v2_safe_widget`: PASS
- `python -m app.scripts.verify_phase_9l_m_n_final_launch_package`: PASS
- Netlify `join.html` HTTP check: `200 OK`

## 1. Netlify Widget Visual QA

Automated in-browser screenshot QA was not completed in this environment because Playwright/browser automation is unavailable here. Do not mark visual launch approval complete until a human or browser-capable environment verifies the items below.

Desktop QA checklist:

- [ ] `1366x768`: launcher visible, expanded modal fits viewport.
- [ ] `1440x900`: sidebar, messages, source chips, and composer do not overlap.
- [ ] Wide desktop: widget does not cover primary nav, CTA, forms, footer, cookie banner, or site modals.
- [ ] Close/minimize/reset/language controls work.
- [ ] Georgian and English labels fit in buttons/chips/cards.
- [ ] Page scroll remains usable with widget open and closed.
- [ ] Browser console has no widget-blocking errors.

Mobile QA checklist:

- [ ] `375x667`: launcher reachable, no horizontal scroll.
- [ ] `390x844`: expanded widget fits viewport and composer remains reachable.
- [ ] `430x932`: source cards and handover card are readable.
- [ ] Mobile nav/forms are not blocked by the launcher.
- [ ] Keyboard opening does not permanently hide the composer.
- [ ] Tap targets are usable and not stacked on each other.

Visual QA status:

```text
NETLIFY_WIDGET_VISUAL_QA_STATUS=PENDING_MANUAL_DESKTOP_MOBILE_BROWSER_REVIEW
```

## 2. Source-Backed Answer UI Display

Expected UI behavior:

- Source-backed answers should render assistant text plus source chips/cards when `used_sources` is present.
- Source display can be toggled by the widget source setting.
- The backend response must contain `answer_source_status=answered_from_approved_source` for verified academic/official questions.
- The UI must not show raw system prompts, API details, database data, or internal stack traces.

Smoke-confirmed source-backed cases:

- Bachelor ECTS `240`
- Master ECTS `120`
- Status suspension `5 years`
- Master's admission documents
- Computer Science spring registration
- Financial support official-source answer
- AI policy answer

## 3. Unsupported Answer UI Display

Expected UI behavior:

- Unsupported answers should render a conservative message:

```text
დამტკიცებულ წყაროებში ეს ინფორმაცია არ ჩანს. ზუსტ ინფორმაციას ოპერატორი ან ოფიციალური არხი დაგიდასტურებთ.
```

- The backend response should contain `answer_source_status=no_approved_source_found`.
- The UI should not display fabricated amounts, percentages, deadlines, phone numbers, scholarships, or consultant details.
- The UI may offer operator routing, but must not directly ask the user to type name, phone, or email before approved contact flow.

Smoke-confirmed unsupported cases:

- `2031` space-campus scholarship
- Current tuition price
- Specific consultant phone
- Today's promotion

## 4. Loading And Error States

Required loading behavior:

- User message remains visible after submit.
- Assistant loading/typing state is visible.
- Composer is disabled or guarded against duplicate sends while request is pending.
- Long backend latency does not break layout.

Required error behavior:

- Error card/message is user-facing and short.
- Internal error details, stack traces, provider names, credentials, DB URLs, and raw exception payloads are not shown.
- User can retry or request operator without sending personal contact details.

Current implementation evidence:

- Widget code contains backend error handling for failed `/chat/message`.
- Production smoke observed no CORS error and no secret exposure.
- One transient AI-provider fallback was observed during a previous smoke run, but the final smoke passed `17/17`.

## 5. Privacy Notice And Data Handling Copy

Privacy/data launch state:

```text
PRIVACY_NOTICE_STATUS=NO_GO_PENDING_APPROVED_OFFICIAL_PRIVACY_URL
CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED
```

Required production copy before real-site embed:

- The widget must link to Alte's approved official privacy policy URL.
- Do not publish `#privacy-policy-pending` or any placeholder privacy URL on the real site.
- The widget/contact UI must state that contact details are shared only after explicit consent.
- Chat users must not be asked to type name/phone/email directly in normal assistant text before approved contact flow.
- No contact details should be sent during no-contact smoke.

Approved-safe operator wording pattern:

```text
თუ გსურთ ოპერატორთან დაკავშირება, დააჭირეთ „დიახ, კონტაქტი“-ს. საკონტაქტო ინფორმაციის გაზიარება მხოლოდ თქვენი მკაფიო თანხმობის შემდეგ უნდა მოხდეს.
```

Data handling constraints:

- Browser calls only the Cloud Run backend.
- Browser must not call Anthropic directly.
- Browser must not contain API keys, Secret Manager values, `DATABASE_URL`, tokens, password hashes, or system prompts.
- Contact record creation remains blocked until separate approval.

## 6. Contact Creation Flow Approval Gate

Normal embed smoke may test chat and operator intent without contact details.

Not approved until separate explicit approval:

- Sending real name, phone, email, or personal data.
- Creating real CRM customer/lead/task records.
- Testing production contact submission with real applicant data.
- Marking lead/task/customer creation launch-ready.

Separate approval phrase required:

```text
Approve production contact creation flow test with synthetic contact data only.
```

After that approval, use synthetic contact data only and record created CRM record IDs without printing secrets or private data.

## 7. Rollback Plan

Immediate rollback triggers:

- Widget breaks layout, navigation, forms, or CTAs.
- Real-domain CORS failure.
- Browser calls Anthropic directly or exposes secrets.
- Unsupported or conflicting answer for academic rules, tuition, scholarships, admissions, visa/legal, ECTS, Medicine/Dentistry, deadlines, or recognition.
- Direct request for name/phone/email before approved contact flow.
- Unexpected lead/task/customer creation.
- Mobile widget blocks navigation or form submission.

Frontend rollback steps:

1. Remove the `window.AlteChatWidgetConfig` block from the affected template/CMS page.
2. Remove the widget `<script src="...alte-ai-chat-widget.js">` tag.
3. Restore the previous CMS/template/deploy version.
4. Clear site/CDN cache if applicable.
5. Verify affected pages no longer load the widget.
6. Verify no browser requests go to the Cloud Run backend from rolled-back pages.
7. Record rollback owner, time, reason, and affected URLs.

Backend rollback option if the issue is backend-specific:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions PREVIOUS_REVISION=100
```

Do not change DB schema, Secret Manager, CORS, or production seed during rollback unless separately approved.

## 8. Exact Embed Snippet

Final asset URL is still pending website-owner approval. Recommended Alte-controlled asset path:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

Use only after the website team confirms the file is uploaded and reachable.

For `alte.edu.ge`:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    widgetVariant: "safe_pro_sidebar",
    assetBaseUrl: "https://alte.edu.ge/assets"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

For `join.alte.edu.ge`:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    widgetVariant: "safe_pro_sidebar",
    assetBaseUrl: "https://alte.edu.ge/assets"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Do not paste this snippet into the real site until final explicit approval is given.

## 9. First Alte Pages For Staged Embed

Recommended staged rollout order:

1. Hidden/staging page controlled by Alte website team, if available.
2. `join.alte.edu.ge` admissions landing page, because this is closest to the verified Netlify `join.html` test flow.
3. `alte.edu.ge` admissions or applicant information page.
4. Program listing page.
5. Bachelor program detail page.
6. Master program detail page.
7. Contact/help page.
8. Main `alte.edu.ge` homepage only after the pages above pass smoke.

Do not start with all pages at once. Expand only after desktop/mobile visual QA and no-contact smoke pass on the first page.

## 10. Final GO/NO-GO Launch Checklist

GO requires all of these:

- [ ] Final written site embed approval from project owner.
- [ ] Website owner/developer assigned.
- [ ] Rollback owner assigned.
- [ ] Smoke test owner assigned.
- [ ] Final asset URL approved and reachable.
- [ ] Official privacy policy URL approved and visible from widget/site.
- [ ] Netlify desktop visual QA passed.
- [ ] Netlify mobile visual QA passed.
- [ ] Real first-page desktop visual QA passed after embed.
- [ ] Real first-page mobile visual QA passed after embed.
- [ ] Real-domain CORS passes for exact embedded origin.
- [ ] Real-domain no-contact smoke passes.
- [ ] Source-backed answers display sources correctly.
- [ ] Unsupported answers show no approved source and do not hallucinate.
- [ ] Loading/error states are user-safe.
- [ ] No direct browser Anthropic calls.
- [ ] No keys/secrets in browser.
- [ ] No contact details sent during no-contact smoke.
- [ ] No lead/task/customer created during informational/no-contact smoke.
- [ ] Contact creation flow remains disabled unless separately approved.
- [ ] Public launch approval recorded separately after embed smoke.

NO-GO if any are true:

- Privacy URL is missing or placeholder.
- Visual QA is not done.
- Website owner or rollback owner is missing.
- Real-domain smoke has not passed.
- Widget asks for name/phone/email directly in chat text.
- Any unsupported answer invents tuition, scholarship, deadline, phone, consultant, or recognition details.
- Any informational question creates lead/task/customer.
- Browser exposes secrets or calls Anthropic directly.
- Real Alte site modification is attempted without explicit approval.

Current launch recommendation:

```text
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_FINAL_SITE_EMBED_APPROVAL_PRIVACY_URL_VISUAL_QA_REAL_DOMAIN_SMOKE
```

