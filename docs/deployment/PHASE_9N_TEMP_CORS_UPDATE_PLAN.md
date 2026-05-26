# Phase 9N Temporary CORS Update Plan

TEMP_CORS_UPDATE_STATUS=EXECUTED_TEMP_TEST_ORIGIN_READY

## Existing Allowed Origins

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

## New Temporary Origin

```text
https://nimble-croissant-2f66e8.netlify.app
```

TEMP_CORS_UPDATE_APPROVED_ORIGIN=https://nimble-croissant-2f66e8.netlify.app
ACTUAL_NETLIFY_TEST_ORIGIN=https://nimble-croissant-2f66e8.netlify.app
PREVIOUS_PLANNED_TEST_ORIGIN=https://alte-ai-chat-test.netlify.app

## Required Future Command Pattern

Update the Cloud Run CORS environment/configuration to include the exact temporary test origin in addition to the existing Alte origins.

Important preservation requirements:

- preserve all existing environment variables.
- preserve Secret Manager mappings.
- preserve Cloud SQL attachment.
- preserve current production backend service.
- do not print secret values.

## Execution Gate

Do not execute until:

- concrete HTTPS test origin URL is provided.
- temporary CORS approval is recorded.
- Cloud Run redeploy approval is recorded.

## Rollback

Remove the temporary origin from CORS and redeploy the existing backend service configuration after testing if the temporary origin is no longer needed.

## Execution Update

- Update executed with exact origin only: `https://alte-ai-chat-test.netlify.app`
- Existing origins preserved:
  - `https://alte.edu.ge`
  - `https://join.alte.edu.ge`
- Wildcard CORS was not used.
- New serving revision: `alte-ai-crm-backend-00009-bhk`
- Backend image unchanged: `v0.9-security-reliability-fixes`

## Actual Netlify Origin Update

- The currently deployed Netlify site origin is `https://nimble-croissant-2f66e8.netlify.app`.
- The previous planned origin `https://alte-ai-chat-test.netlify.app` remains allowed as an optional/alternate test origin.
- The actual Netlify origin is approved for exact-origin CORS update.
