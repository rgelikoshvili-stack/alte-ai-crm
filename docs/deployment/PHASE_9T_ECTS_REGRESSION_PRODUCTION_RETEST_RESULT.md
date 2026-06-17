# Phase 9T ECTS Regression Production Retest Result

PHASE_9T_ECTS_REGRESSION_PRODUCTION_RETEST_STATUS=DEPLOYED_AND_PASSED

Decision state:
BACKEND_DEPLOYED_OFFICIAL_ACADEMIC_RULES_ECTS_REGRESSION_FIX_VERIFIED_PUBLIC_LAUNCH_NO_GO

## Deploy

- Source branch: `phase-9s-agent-preview-cors-note`
- Source commit: `f1027d8`
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Active revision: `alte-ai-crm-backend-00024-8p8`
- Traffic: `100%`
- Public backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Image tag: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9t-ects-regression-fix`
- Image digest: `sha256:49eb4939ce39bf818c5e72667a5da7777a469081f2e7cafd52202a82469ada82`
- Cloud Build ID: `0837ed04-bd78-4926-b7be-d68e3560c941`

## Production Retest

Production retest used `/chat/session/start` and `/chat/message` against the public Cloud Run backend. Output was sanitized and did not print full chatbot replies.

| Check | Expected | Source-backed | Forbidden value check | Lead/task side effect | Result |
| --- | --- | --- | --- | --- | --- |
| Bachelor completion ECTS | contains `240` | yes, 10 sources | no `180`, no `3-წლიანი`, no `3 წელი` | none | PASS |
| Master ECTS | contains `120` | yes, 10 sources | none | none | PASS |
| Student status suspension | contains `5` | yes, 10 sources | none | none | PASS |

## Screenshot

Retest screenshot artifact:

`docs/deployment/PHASE_9T_ECTS_REGRESSION_PRODUCTION_RETEST_SCREENSHOT.png`

The in-app browser automation could not attach in this environment, so the screenshot is a generated production retest summary image based on the sanitized live smoke output.

## Safety

- Production migration run: NO
- Production seed run: NO
- DB schema change: NO
- Secret Manager change: NO
- CORS change: NO
- Real `alte.edu.ge` or `join.alte.edu.ge` change: NO
- Contact details sent: NO
- Lead/task/customer created: NO
- Public launch: NO-GO
