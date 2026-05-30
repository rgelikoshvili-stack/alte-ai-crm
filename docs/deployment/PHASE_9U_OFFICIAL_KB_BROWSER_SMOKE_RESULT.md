# Phase 9U Official KB Browser Smoke Result

PHASE_9U_OFFICIAL_KB_BROWSER_SMOKE_STATUS=FAILED_PENDING_FIX

Decision state:
BACKEND_DEPLOYED_OFFICIAL_KB_BROWSER_SMOKE_FAILED_PENDING_FIX

## Scope

- Test URL: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Origin tested: `https://nimble-croissant-2f66e8.netlify.app`
- Test mode: browser-origin HTTP requests with Netlify `Origin` header.
- In-app browser automation status: unavailable in this environment due browser runtime startup failure.
- Real Alte site modified: NO
- Public launch remains: NO-GO

## Result Summary

- Total official KB/contact-safety checks: `8`
- Passed: `6`
- Failed: `2`
- CORS preflight `/chat/session/start`: PASS, exact Netlify origin, no wildcard
- CORS preflight `/chat/message`: PASS, exact Netlify origin, no wildcard
- No contact details sent: YES
- `/chat/handover` called: NO
- Lead/task/customer intentionally created: NO

## Passed Checks

| Check | Result |
| --- | --- |
| Bachelor completion ECTS | PASS, answered `240`, did not say `180` |
| Master ECTS | PASS, answered `120` |
| Teaching language | PASS, Georgian with some English-language programs |
| Student status suspension | PASS, maximum total `5` years |
| Computer Science spring registration | PASS, `9-14 March`; semester starts `30 March` |
| Unsupported 2031 space-campus scholarship | PASS, returned `no_approved_source_found` / no approved-source style fallback |

## Failed Checks

| Check | Failure |
| --- | --- |
| Master's admission documents | FAIL. Production response was source-backed but did not list the required official document checklist. |
| Operator contact request safety | FAIL. Production response directly asked the user to provide contact information: name, phone, or email. |

## Local Fix Prepared

Local backend patch prepared, not deployed:

- Added deterministic official answer for master's admission document checklist:
  - ID copy
  - CV
  - 3x4 photo in printed/electronic form
  - military registration certificate copy for male applicants
  - notarized diploma copy
  - diploma supplement copy
- Expanded contact-safety sanitizer for Georgian wording such as direct requests to provide contact information, name, phone, or email.
- Added targeted regression tests.

Local verification:

- `python -m pytest app\tests\test_phase_9x_browser_contact_safety.py app\tests\test_phase_9t_official_academic_rules_regression.py -q`
- Result: `10 passed`

## Safety

- Production DB modified: NO
- Production migration run: NO
- Production seed run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Frontend design changed: NO
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Contact details sent: NO
- Lead/task/customer intentionally created: NO
- Public launch complete: NO

## Next Step

Deploy the local backend fix only after approval, then rerun Phase 9U browser or browser-origin smoke. Do not mark final site embed approval or public launch complete until the retest passes.
