# Phase 9AB Mobile Responsive Widget Fix Result

PHASE_9AB_MOBILE_RESPONSIVE_STATUS=FIXED_PENDING_NETLIFY_REDEPLOY_AND_VISUAL_QA

Decision state:

```text
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_FIXED_PENDING_NETLIFY_REDEPLOY
```

## Scope

- Netlify test page: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Local test URL used for fixed assets: `http://127.0.0.1:5179/join.html`
- Production backend revision remains: `alte-ai-crm-backend-00030-td7`
- Real Alte site modified: NO
- Real join.alte.edu.ge modified: NO
- Backend behavior changed: NO
- CORS changed: NO
- Production DB changed: NO
- Secret Manager changed: NO
- Contact details sent: NO
- Lead/task/customer created: NO
- Public launch: NO-GO

## Original Issue

Previous mobile visual QA at `430x932` showed the Pro v2 widget was too wide for the mobile viewport:

- The expanded widget rendered with the desktop sidebar.
- The main chat content was cropped on the right edge.
- A horizontal page scroll appeared.
- The composer area did not fit safely inside the mobile viewport.

Original screenshot:

- `docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png`

## Root Cause

The overflow came from two layout layers:

1. The host iframe was set to `100vw`, which can create page-level horizontal overflow when browser scrollbars are present.
2. The expanded Pro v2 chat shell kept desktop layout assumptions on mobile: wide sidebar, fixed action rows, unbounded greeting/source chips, and composer controls competing for a narrow viewport.

## Files Changed

- `test_site/join.html`
- `test_site/index.html`
- `test_site/alte-ai-chat-widget.js`
- `test_site/variants/pro-v2-chat.jsx`
- `widget/variants/pro-v2-chat.jsx`
- `dist/widget/alte-ai-chat-widget.js`
- `dist/netlify_test_site/join.html`
- `dist/netlify_test_site/index.html`
- `dist/netlify_test_site/alte-ai-chat-widget.js`
- `dist/netlify_test_site/alte-ai-chat-widget.html`
- `dist/netlify_test_site_package/join.html`
- `dist/netlify_test_site_package/index.html`
- `dist/netlify_test_site_package/alte-ai-chat-widget.js`
- `dist/netlify_test_site_package/alte-ai-chat-widget.html`
- `dist/netlify_test_site_package/variants/pro-v2-chat.jsx`
- `dist/netlify_test_site_deploy.zip`
- `backend/app/scripts/visual_qa_netlify_widget.py`
- `backend/app/scripts/verify_phase_9ab_mobile_responsive_widget_fix.py`
- `backend/app/tests/test_phase_9ab_mobile_responsive_widget_fix.py`
- `docs/deployment/PHASE_9AB_MOBILE_RESPONSIVE_WIDGET_FIX_RESULT.md`

## CSS/Layout Fix Summary

- Changed the widget iframe default width from `100vw` to `100%`.
- Added host container `max-width: 100vw` and `overflow-x: hidden` guard.
- Added `overflow-x: hidden` on Netlify test host pages.
- Added Pro v2 responsive guard for embedded/mobile widths:
  - Expanded window uses viewport insets instead of desktop-centered sizing.
  - Sidebar is hidden in the mobile/tablet responsive shell.
  - Main chat column is constrained to `max-width: 100%`.
  - Header text truncates safely.
  - Source chips and quick replies stack/wrap.
  - Handover buttons wrap.
  - Composer uses a narrower control layout on mobile.

The desktop layout rules remain unchanged for the 1366/1440 target widths.

## Visual QA Result

Local fixed-asset screenshot QA was run with Chrome headless against the local static test site. This verifies the repo assets before Netlify redeploy.

Desktop:

- `1440x900`: PASS for initial widget load and desktop layout preservation.
- `1366x768`: PASS for initial widget load and desktop layout preservation.

Mobile:

- `430x932`: PASS locally for the primary blocker: sidebar removed, main chat visible, composer visible, no desktop sidebar crop.
- `390x844`: PASS locally for the same responsive shell behavior.
- `375x667`: PASS locally for the same responsive shell behavior.

Screenshots:

- `docs/deployment/visual_qa/local_widget_desktop_1440x900_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_desktop_1366x768_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_mobile_430x932_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_mobile_390x844_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_mobile_375x667_phase_9ab.png`

Netlify visual QA:

- Current Netlify deployment is not updated yet from this local branch state.
- Netlify redeploy is needed before marking `PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL`.
- Do not mark Netlify mobile visual QA passed until the redeployed `https://nimble-croissant-2f66e8.netlify.app/join.html` is rechecked.

## Automation

Added:

- `backend/app/scripts/visual_qa_netlify_widget.py`
- `backend/app/scripts/verify_phase_9ab_mobile_responsive_widget_fix.py`
- `backend/app/tests/test_phase_9ab_mobile_responsive_widget_fix.py`

`visual_qa_netlify_widget.py` uses Playwright when available. If Playwright is unavailable, it records `PLAYWRIGHT_UNAVAILABLE` and manual QA steps instead of faking a pass.

## Official KB Guardrails

This phase did not change backend routing, source priority, official KB logic, CORS, DB, or deployment.

Official facts remain documented and protected:

- Bachelor completion: `240 ECTS`, not `180`.
- Master program: `120 ECTS`.
- Student status suspension: maximum total `5 years`.
- Unsupported questions must return no approved source.
- No phone/email/name request before approved contact flow.

## Remaining Before Final Embed Approval

- Push branch and allow Netlify to redeploy test assets.
- Re-run Netlify desktop/mobile visual QA after redeploy.
- Confirm official privacy URL.
- Approve contact-flow copy and contact creation gate separately.
- Approve final asset URL.
- Approve staged real-site embed pages.
- Run real-domain no-contact smoke after approved embed.
- Reconcile dirty working tree before launch freeze.

Final recommendation:

```text
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_NETLIFY_REDEPLOY_PRIVACY_URL_FINAL_SITE_EMBED_APPROVAL_REAL_DOMAIN_SMOKE
```
