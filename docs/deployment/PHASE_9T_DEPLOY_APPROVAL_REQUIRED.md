# Phase 9T Deploy Approval Required

PHASE_9T_DEPLOY_APPROVAL_STATUS=REQUIRED_FOR_PRODUCTION_RETEST

The official academic rules ECTS regression fix is implemented in backend code, but it has not been deployed to Cloud Run in this task.

Production retest with `backend/app/scripts/production_official_academic_rules_chat_smoke.py` requires a new approved Cloud Run deploy. Until that deploy is approved and completed, production may still serve the previous chatbot behavior for the bachelor ECTS question.

Safety state:

- Production migration run: NO
- Production seed run: NO
- Production DB schema change: NO
- Secret Manager change: NO
- CORS change: NO
- Real Alte site change: NO
- Contact-flow test run: NO
- Public launch: NO-GO
