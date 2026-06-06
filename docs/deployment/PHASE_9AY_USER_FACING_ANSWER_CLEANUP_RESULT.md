# Phase 9AY — User-Facing Answer Cleanup and Source Citation Polish

PHASE_9AY_USER_FACING_CLEANUP_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY
Decision state: BACKEND_DEPLOYED_PROGRAM_CATALOG_SOURCE_QA_PASSED_PENDING_APPROVALS
Public launch: NO-GO

## Scope

This local change keeps the existing retrieval and routing logic, but cleans the final user-facing answer and source labels before they are returned to the chatbot UI.

## Fixes

- User-facing source-backed replies no longer append raw snippet titles or internal `Source:` lines.
- Final public answer text strips internal/debug markers including:
  - `Official source:`
  - `Reference:`
  - `Policy:`
  - `answer only from`
  - `handover if`
  - `official_academic_rules`
  - `chunk`
  - `page` / `p022_c050` style source markers
- Review fix: inline source markers are stripped without deleting the valid answer sentence.
- Control-only source/debug lines are still removed completely.
- Known internal source keys are mapped to readable labels:
  - `ბაკალავრიატის დებულება`
  - `მაგისტრატურის დებულება`
  - `სასწავლო პროცესის მარეგულირებელი წესი`
  - `აკადემიური კალენდარი 2025–2026`
  - `მიღების წესი`
  - `საერთაშორისო მიღების წესი`
- Student status suspension questions now distinguish:
  - suspension period: maximum 5 years
  - suspension grounds: written request, study abroad, illness, pregnancy/childbirth/childcare, military service, unpaid tuition, failed registration, missing required documents, and other legal grounds
- Bachelor admission document answers now return a concrete document list instead of a generic placeholder.

## Safety

- No deploy performed.
- No commit made.
- No real `alte.edu.ge` or `join.alte.edu.ge` changes.
- No upload/embed/frontend/Netlify changes.
- No DB schema, migration, seed, or import changes.
- No Secret Manager, CORS, or Bridge Hub changes.
- No contact flow submitted.
- No lead/customer/task created.
- Public launch remains NO-GO.

## Verification

- `python -m compileall app`: PASS
- Focused cleanup tests: 14 passed
- Full backend pytest: 1045 passed
- Deploy status: NOT_DEPLOYED_PENDING_APPROVAL
- Commit made: NO
