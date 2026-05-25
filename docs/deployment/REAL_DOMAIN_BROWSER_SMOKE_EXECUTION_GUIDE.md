# Real-Domain Browser Smoke Execution Guide

Do not execute before actual site embed.

Phase 9I selected Alte-controlled hosting. The planned placeholder asset URL is:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

Run this guide only after the website team uploads the asset and inserts the approved snippet.

Phase 9L-P status: real-domain smoke is NOT executed because actual site embed is not executed. Do not mark smoke passed until the widget is live on the approved real domain and the checklist below is completed.

## Manual Browser Checklist

- Open `https://alte.edu.ge` page containing widget.
- Open `https://join.alte.edu.ge` page containing widget.
- Verify widget loads without layout break.
- Verify KA/EN UI text.
- Verify source links and handover cards render correctly.

## DevTools Network Checks

- Browser should call the production FastAPI backend only:
  `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Browser should NOT call `api.anthropic.com`.
- Browser should NOT expose API keys.

## CORS Checks

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

## KA Test Cases

- `რა პროგრამები აქვს ალტე უნივერსიტეტს?`
- `რა ღირს სწავლა?`
- `როდის არის მიღების ბოლო ვადა?`
- `მინდა ოპერატორთან საუბარი`

## EN Test Cases

- `I want to apply for medicine from India`
- `How much is medicine tuition?`
- `What documents do international students need?`
- `Can you help with visa and relocation?`

## Expected Results

- Department routing correct
- Sensitive answers conservative
- Source links shown if available
- No contact details in safe smoke
- No intentional lead/task/customer creation
- Handover card shown when needed

## PASS/FAIL Criteria

PASS only if:

- Widget loads on actual domain.
- No browser console errors.
- No CORS errors.
- Backend calls work.
- No `api.anthropic.com` calls.
- No frontend API keys.
- Sidebar department context works.
- Sensitive topics are conservative.
- No contact details are sent in safe smoke.
- No lead/task/customer is intentionally created.

FAIL if any item above fails.
