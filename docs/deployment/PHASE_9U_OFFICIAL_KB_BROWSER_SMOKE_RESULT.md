# Phase 9U Official KB Browser Smoke Result

PHASE_9U_OFFICIAL_KB_BROWSER_SMOKE_STATUS=PASSED_PENDING_FINAL_SITE_EMBED_APPROVAL

Decision state:
BACKEND_DEPLOYED_OFFICIAL_KB_BROWSER_VERIFIED_PENDING_FINAL_SITE_EMBED_APPROVAL

## Scope

- Test URL: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Origin tested: `https://nimble-croissant-2f66e8.netlify.app`
- Test mode: browser-origin HTTP requests with Netlify `Origin` header.
- In-app browser automation status: unavailable in this environment due browser runtime startup failure; browser-origin request mode was used.
- Real Alte site modified: NO
- Public launch remains: NO-GO

## Deploy

- Source branch: `phase-9s-agent-preview-cors-note`
- Final source commit: `641bd5a`
- Final Cloud Build ID: `3edecfec-69c1-4f6a-ad9c-94493627b701`
- Final image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9u-official-kb-browser-fix3`
- Final image digest: `sha256:d81804ec8fdcfd7fbaeb38be6292693d8d8069fa59a9641dd0cc5585d0b47094`
- Final Cloud Run revision: `alte-ai-crm-backend-00027-4lk`
- Traffic: `100%`

## Result Summary

- Total official KB/contact-safety checks: `8`
- Passed: `8`
- Failed: `0`
- CORS preflight `/chat/session/start`: PASS, exact Netlify origin, no wildcard
- CORS preflight `/chat/message`: PASS, exact Netlify origin, no wildcard
- No contact details sent: YES
- `/chat/handover` called: NO
- Lead/task/customer intentionally created: NO

## Smoke Matrix

| Check | Result |
| --- | --- |
| Bachelor completion ECTS | PASS, answered `240`, did not say `180` |
| Master ECTS | PASS, answered `120` |
| Teaching language | PASS, Georgian with some English-language programs |
| Student status suspension | PASS, maximum total `5` years |
| Computer Science spring registration | PASS, `9-14 March`; semester starts `30 March` |
| Master's admission documents | PASS, returned official checklist |
| Unsupported 2031 space-campus scholarship | PASS, returned `no_approved_source_found` / no approved-source style fallback |
| Operator contact request safety | PASS, no direct request to type name, phone, email, or contact details; no lead/task/customer created |

## Master's Admission Checklist Verified

Production response included:

- ID copy
- CV
- 3x4 photo in printed/electronic form
- military registration certificate copy for male applicants
- notarized diploma copy
- diploma supplement copy

## Local Verification

- `python -m pytest app\tests\test_phase_9x_browser_contact_safety.py app\tests\test_phase_9t_official_academic_rules_regression.py -q`
- Result: `12 passed`

## Safety

- Production DB schema changed: NO
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

Final site embed approval remains a separate gate. Do not mark public launch complete until final embed approval and real-site smoke are explicitly approved and completed.
