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
