# Phase 9AA Broader Browser-Origin QA Result

PHASE_9AA_BROADER_BROWSER_QA_STATUS=PASSED_WITH_PUBLIC_LAUNCH_STILL_NO_GO

Decision state:
BACKEND_DEPLOYED_SELECTED_45_DOCS_BROADER_BROWSER_ORIGIN_QA_PASSED_PUBLIC_LAUNCH_NO_GO

## Scope

- Branch: `phase-9s-agent-preview-cors-note`
- Backend URL verified: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Browser origin simulated: `https://nimble-croissant-2f66e8.netlify.app`
- CORS preflight for `/chat/message`: `200`
- Health check: `200`
- Active Cloud Run revision: `alte-ai-crm-backend-00023-gbr`
- Traffic: `100%`
- Broad QA routing fix commit: `b9b2305`
- Image tag: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9aa-broad-qa-routing`
- Image digest: `sha256:48f10840d5f71f10c0b6cc007bf495dc08ae26d1e968b43609df63d739cc8631`
- Cloud Build ID: `afc28d30-b536-4aa6-96df-2172728f6533`

Browser automation could not attach in this environment, so the QA was run as browser-origin HTTP requests with the Netlify `Origin` header and CORS preflight. No frontend code was changed.

## Result Summary

- Total checks: `14`
- Passed: `14`
- Failed: `0`
- Source-backed informational checks: `12`
- Unsupported/no-source fallback checks: `1`
- Contact request without details checks: `1`
- Extra lead/task/customer created: `NO`

## QA Matrix

| Area | Result | Source-backed | Handover | Lead/task side effect |
| --- | --- | --- | --- | --- |
| Programs / admission | PASS | yes | yes | none |
| Bachelor / master | PASS | yes | no | none |
| Academic calendar | PASS | yes | no | none |
| Exams | PASS | yes | no | none |
| ECTS / mobility | PASS | yes | yes | none |
| Financial support | PASS | yes | yes | none |
| Ombudsman | PASS | yes | no | none |
| Library | PASS | yes | no | none |
| Plagiarism / ethics | PASS | yes | yes | none |
| AI policy | PASS | yes | yes | none |
| Career services | PASS | yes | no | none |
| Special needs students | PASS | yes | yes | none |
| Unknown unsupported question | PASS | no, correctly `no_approved_source_found` | yes | none |
| Contact request without details | PASS | not required | yes | none |

## Fixes Applied During QA

The first broad QA run found two issues:

- A Georgian programs/admission phrasing did not force knowledge retrieval.
- A clearly unsupported future/space-campus scholarship question matched unrelated finance sources.

The backend was patched to:

- Treat program catalog / educational program / Georgian programs-admission wording as official knowledge questions.
- Block clearly unsupported future campus/scholarship questions from using unrelated approved sources.

Targeted regression test:

- `python -m pytest app\tests\test_phase_9aa_selected_alte_45_missing_docs.py -q`
- Result: `4 passed`

## Safety Confirmation

- No production migration was run.
- No production seed was run.
- No DB schema change was made.
- No Secret Manager change was made.
- No CORS change was made.
- No real `alte.edu.ge` or `join.alte.edu.ge` site change was made.
- No contact details were sent in the smoke test.
- No lead, task, or customer was created by broad QA.
- `.env` and `.local-secrets` were not committed.

## Public Launch Recommendation

Recommendation: `NO-GO` for full public launch.

Reason: broad browser-origin QA passed, but visual end-to-end widget QA and an explicitly approved contact-creation test remain separate launch gates. The backend knowledge routing is ready for broader controlled QA, not public launch completion.
