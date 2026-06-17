# Phase 9T Official Academic Rules Deploy Result

PHASE_9T_OFFICIAL_ACADEMIC_RULES_DEPLOY_STATUS=DEPLOYED_AND_PRODUCTION_SMOKE_PASSED

Decision state:

BACKEND_DEPLOYED_OFFICIAL_ACADEMIC_RULES_KB_ACTIVE_PENDING_BROWSER_QA_RETEST

## Scope

The Phase 9T chatbot retrieval update was deployed so `/chat/message` can retrieve official academic rules/calendar records from the approved production Knowledge Base.

## Build And Deploy

- Source commit: `f9cea7e`
- Clean deploy worktree used: YES
- Image built: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9t-academic-rules-kb2`
- Cloud Build: PASS
- Cloud Run service: `alte-ai-crm-backend`
- Deployed revision: `alte-ai-crm-backend-phase9t-kb2`
- Traffic: 100% to `alte-ai-crm-backend-phase9t-kb2`
- Production URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

## Production Smoke

- `/health`: 200
- Academic rules smoke questions: 5
- `answered_from_approved_source`: 5/5
- Source count returned: 10 for each smoke question
- Lead created: NO
- Task created: NO
- Customer created: NO
- Contact details sent/requested: NO

Smoke topics:

- Bachelor ECTS
- Autumn midterm exam dates
- GPA formula
- Student status suspension grounds
- Bachelor thesis conservative handling

## Safety

- Production DB modified in this deploy: NO
- Migration run: NO
- Seed run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Real Alte site modified: NO
- Public chatbot UI changed: NO
- Contact-flow test run: NO
- Public launch: NO-GO

## Notes

The production KB import had already been approved and applied before this deploy. This deploy only activated code-side retrieval behavior so academic rules questions do not incorrectly filter official KB records by website origin.

