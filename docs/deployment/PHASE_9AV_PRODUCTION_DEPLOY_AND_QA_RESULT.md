# Phase 9AV Production Deploy and QA Result

`PHASE_9AV_DEPLOY_STATUS=FAILED_PENDING_FIXES`

Decision state:

`BACKEND_DEPLOYED_CLAUDE_INTENT_ROUTER_QA_FAILED_PENDING_FIXES`

Public launch:

`NO-GO`

## Deployment

- Code commit: `03574f8` (`phase 9av: add claude intent router scoped retrieval`)
- Branch pushed: `origin/phase-9s-agent-preview-cors-note`
- Backend image tag: `v0.9-phase-9av-claude-intent-router`
- Cloud Run service: `alte-ai-crm-backend`
- Cloud Run region: `europe-west1`
- New revision: `alte-ai-crm-backend-00042-6tf`
- Traffic split: `alte-ai-crm-backend-00042-6tf` serving 100%
- Production backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

The deploy updated the existing Cloud Run service image only. No migration, seed, schema change, DB import, Secret Manager change, CORS change, Bridge Hub change, frontend change, Netlify deploy, real-site upload, or real-site embed was performed.

## Pre-Commit Verification

- `python -m compileall app`: PASS
- Full backend pytest: PASS, 988 passed
- Phase 9AV verifier: PASS
- Local Phase 9AV QA: PASS, 27/27
- Final review: No blocking issues found

## Production QA

Focused Phase 9AT knowledge fixes QA:

- Status: PASS
- Passed: 7/7
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

Operator alignment QA:

- Status: PASS
- Passed: 7/7
- Operator API auth: AUTH_OK
- Official informational answers excluded from handover queue: VERIFIED
- Explicit operator requests set handover: VERIFIED
- Wait-for-operator still sets waiting state: VERIFIED
- Lead/task/customer created: NO

Full Phase 9AS knowledge coverage QA:

- Status: FAILED
- Total: 53
- Passed: 32
- Failed: 21
- Skipped: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

## Remaining Failures

The full 9AS production run still has critical coverage and expectation failures:

- official academic facts: 7/17 passed, 10 failed
- academic calendar: 8/9 passed, 1 failed
- admissions: 3/6 passed, 3 failed
- clarification: 5/6 passed, 1 failed
- routing: 4/6 passed, 2 failed
- unsupported: 1/4 passed, 3 failed
- operator handover: 4/5 passed, 1 failed

Notable remaining failed areas include student status/mobility/assessment answers, foreign applicant/admissions routing, one help clarification expectation, finance operator wording expectations, international medicine routing expectations, and unsupported false-positive/fallback behavior.

## Safety Confirmations

- Real Alte site modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- Contact creation flow executed: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- DB schema changed: NO
- Migration run: NO
- Seed/import run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Public launch: NO-GO

## Recommendation

Do not approve public launch. The Claude Intent Router deploy is live and focused/operator QA passed, but full 9AS coverage is still below the required bar. The next phase should fix the 21 remaining full-knowledge QA failures or update stale expectations only where the approved source inventory proves the expected answer is unavailable.
