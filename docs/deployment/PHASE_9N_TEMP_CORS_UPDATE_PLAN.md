# Phase 9N Temporary CORS Update Plan

TEMP_CORS_UPDATE_STATUS=NOT_EXECUTED_PENDING_TEST_ORIGIN

## Existing Allowed Origins

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

## New Temporary Origin

```text
PENDING_TEST_ORIGIN_URL
```

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
