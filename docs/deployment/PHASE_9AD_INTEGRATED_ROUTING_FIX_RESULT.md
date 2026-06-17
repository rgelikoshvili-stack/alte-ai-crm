# Phase 9AD Integrated Routing Fix Result

PHASE_9AD_ROUTING_FIX_STATUS=PASSED_PENDING_MOBILE_VISUAL_QA_PRIVACY_AND_EMBED_APPROVAL

Decision state:
BACKEND_DEPLOYED_INTEGRATED_CHAT_ROUTING_QA_PASSED_PENDING_FINAL_APPROVALS

Public launch: NO-GO

## Scope

- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Netlify test origin: `https://nimble-croissant-2f66e8.netlify.app`
- Real Alte site modified: NO
- Production DB migration/seed/schema change: NO
- Secret Manager change: NO
- CORS change: NO
- Contact details sent: NO

## Phase 9AC Failures

1. Admissions question routed to Programs instead of Admissions/Registration.
   - Case now tracked as `admissions_auto_route_fixed`.
2. Library question routed to International Admissions instead of Library.
   - Case now tracked as `library_auto_route_fixed`.
3. Finance handover question routed to International Admissions instead of Finance.
   - Case now tracked as `finance_handover_route_fixed`.

## Root Cause

Routing used the full message-plus-source context for keyword matching. For Netlify sessions with `source_domain=join.alte.edu.ge`, the source-domain token could win as an International Admissions keyword when a Georgian message had no matching route alias.

The three failed Georgian phrasings also needed explicit aliases:

- `ჩავირიცხო` / enrollment phrasing should override generic bachelor/program wording and route to Admissions.
- `ბიბლიოთეკის` should route to Library, not fall through to the join-domain default.
- `ფინანსურ ... სწავლის საფასურზე` should route to Finance before human-request fallback.

## Files Changed

- `backend/app/services/department_routing_service.py`
- `backend/app/tests/test_department_routing_service.py`
- `backend/app/tests/test_phase_9ad_integrated_routing_fix.py`
- `backend/app/tests/test_phase_9ad_integrated_routing_fix_package.py`
- `backend/app/scripts/production_integrated_chat_routing_operator_qa.py`
- `backend/app/scripts/production_phase_9ad_routing_fix_smoke.py`
- `backend/app/scripts/verify_phase_9ad_integrated_routing_fix.py`
- `docs/deployment/PHASE_9AD_INTEGRATED_ROUTING_FIX_RESULT.md`

## Routing Fix Summary

- Added explicit Georgian route aliases for Admissions, Library, and Finance.
- Added a first-class `library` route label.
- Changed keyword extraction to use the user message for keyword scoring, while still allowing source-domain context for conservative fallback and international/medicine prioritization.
- Kept source priority and official KB answer behavior unchanged.

## Local Tests

Initial focused local regression:

- `test_department_routing_service.py`
- `test_phase_9ad_integrated_routing_fix.py`

Result: `24 passed`

Full local suite:

- `python -m compileall app`: PASS
- `pytest --basetemp .pytest_tmp_9ad_routing_fix`: `779 passed`
- `python -m app.scripts.verify_phase_9ad_integrated_routing_fix`: PASS

## Deployment

- Backend deploy required: YES, because routing fix changed backend service code.
- Image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9ad-routing-fix2`
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- New revision: `alte-ai-crm-backend-00032-lzq`
- Traffic: 100%
- Cloud SQL attachment preserved.
- Existing Secret Manager mappings preserved.
- CORS configuration not changed.

## Production Focused Smoke Result

Script:

- `python -m app.scripts.production_phase_9ad_routing_fix_smoke`

Result: `6/6 passed`

Verified:

- `admissions_auto_route_fixed`: route `Admissions`, not `Programs` or `International Admissions`
- `library_auto_route_fixed`: route `Library`, not `International Admissions`
- `finance_handover_route_fixed`: route `Finance`, not `International Admissions`
- International admissions control
- Bachelor 240 ECTS control
- Unsupported 2031 scholarship control

## Full Integrated QA Rerun Result

Script:

- `python -m app.scripts.production_integrated_chat_routing_operator_qa`

Result: `18/18 passed`

- Official KB answer QA: `6/6 passed`
- Auto-routing QA: `10/10 passed`
- Handover/contact-safety QA: `2/2 passed`
- Backend baseline: PASS
- Netlify origin: PASS
- Operator CRM local page check: PASS

## Contact And CRM Safety

- No phone/email/name request: confirmed by focused smoke and integrated QA.
- No lead/task/customer created: confirmed by focused smoke and integrated QA.
- Contact/request flows remain approval-gated.

## Remaining Blockers

- Mobile visual QA.
- Privacy URL.
- Contact-flow approval.
- Final asset URL.
- Staged real-site embed approval.
- Real-domain smoke.
- Dirty tree reconciliation.
- Final public launch GO approval.
