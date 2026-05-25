# Phase 9N Final Real-Domain Smoke Plan

## Prerequisites

- Actual site embed completed.
- Final asset URL is live.
- Official privacy URL is live.
- Approved domains:
  - `https://alte.edu.ge`
  - `https://join.alte.edu.ge`
- Content and privacy approvals are recorded.
- Rollback owner and smoke test owner are recorded.

## Browser Checks

- Widget visible.
- Sidebar visible.
- KA/EN language switch works.
- No console errors.
- No CORS errors.
- No direct `api.anthropic.com` browser call.
- Browser calls only the Cloud Run backend.
- No frontend API key or secret is exposed.

## Safe Test Cases

KA:

- `რა პროგრამები აქვს ალტე უნივერსიტეტს?`
- `რა ღირს სწავლა?`
- `როდის არის მიღების ბოლო ვადა?`
- `მინდა ოპერატორთან საუბარი`

EN:

- `I want to apply for medicine from India`
- `How much is medicine tuition?`
- `What documents do international students need?`
- `Can you help with visa and relocation?`

## Expected Results

- no contact details sent.
- no intentional lead/task/customer creation.
- finance/deadline answers remain conservative.
- handover routes to the correct department where possible.
- source links/cards are shown when available.
- no contact-flow test is run unless separately approved.
