# Real-Domain Widget Smoke Plan

## Target Domains

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

Run this only after the widget is embedded on an approved real-domain page.

## KA / alte.edu.ge

1. Open the homepage or approved page with the widget.
2. Confirm the widget loads without layout break.
3. Confirm KA greeting is visible.
4. Send: `რა პროგრამები აქვს ალტე უნივერსიტეტს?`
5. Send: `რა ღირს სწავლა?`
6. Send: `როდის არის მიღების ბოლო ვადა?`
7. Send: `მინდა ადამიანთან საუბარი`

## EN / join.alte.edu.ge

1. Open the approved page with the widget.
2. Confirm the widget loads.
3. Confirm EN greeting is visible.
4. Send: `I want to apply for medicine from India`
5. Send: `How much is medicine tuition?`
6. Send: `What documents do international students need?`
7. Send: `Can you help with visa and relocation?`

## Expected Results

- No browser console errors.
- No CORS errors.
- No direct call to `api.anthropic.com`.
- Browser calls go only to the production FastAPI backend.
- No contact details are sent in safe smoke.
- No intentional lead/task/customer creation.
- Tuition/deadline answers remain conservative.
- No-contact guard works.
- Handover card appears when needed.
- Widget does not harm page layout or performance.
- Department-aware routing is visible when handover occurs:
  - tuition -> Finance
  - international documents -> International Admissions
  - medicine/MD -> Medicine / MD
  - portal/login -> IT Support
  - student services -> Student Services
- Sidebar layout is visible:
  - left department menu is present
  - active department is highlighted
  - selected department context is sent to backend

## Status

```text
REAL_DOMAIN_WIDGET_SMOKE_STATUS=PENDING_ACTUAL_EMBED
```

Phase 9D routing code requires redeploy before this plan can verify production behavior.

## Phase 9D-UI-Final Exact Pro Sidebar Addendum

Real-domain smoke must verify the exact functional Pro Sidebar layout:

- Left sidebar remains visible on desktop and does not break page layout.
- Active department highlighting works.
- Department clicks update the selected department label.
- Quick chips send messages to the backend with `selected_department` and `selected_topic`.
- Human Operator sends a human request with the active department context.
- Handover/operator card shows the correct department when backend returns handover/routing fields.
- Source cards render only backend-returned sources.
- Contact request UI appears only when backend asks for phone/email.
- Browser network calls go only to the production FastAPI backend, not Anthropic.
- No contact details are sent during safe smoke.
- No intentional production lead/task/customer is created during safe smoke.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_PRO_SIDEBAR_WIDGET_FUNCTIONAL_READY_PENDING_REDEPLOY_AND_SITE_EMBED

## Phase 9D-Redeploy Addendum

The backend was redeployed with image `v0.9-department-routing-sidebar`, but production department routing smoke did not fully pass.

Real-domain browser smoke must not proceed until:

- Ambiguous sidebar Finance context routes to Finance.
- Ambiguous sidebar Medicine context routes to Medicine / MD.
- `python -m app.scripts.production_department_routing_sidebar_smoke` passes.

Current production verification:

- Department routing smoke: `26/28` passed, `2` failed
- Finance no-contact smoke: `24/24` passed
- Broader knowledge smoke: `25/25` passed

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```

## Phase 9E-Redeploy Update

Production backend routing has been redeployed with the sidebar ambiguous routing fix.

- Image tag: `v0.9-sidebar-ambiguous-routing-fix`
- New revision: `alte-ai-crm-backend-00006-vs5`
- Department routing sidebar smoke: 28/28 passed
- Previously failing Finance and Medicine ambiguous sidebar cases now pass

Real-domain browser smoke remains pending because the actual site embed has not been completed.

Decision state:

```text
BACKEND_DEPLOYED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED
```
```
