# Optional Test Origin CORS Plan

OPTIONAL_TEST_ORIGIN_CORS_STATUS=NOT_CONFIGURED_PENDING_APPROVAL

## Current Production Allowed Origins

Current production allowed origins likely include:

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

## Localhost/Test Site Behavior

Localhost or a separate hosted test site may fail browser CORS because it is not part of the production allowlist.

## Required For A Separate Hosted Browser Test

- final test origin URL.
- approval to add it temporarily to CORS.
- Cloud Run redeploy with updated CORS.
- smoke test from that origin.
- optional removal after test.

## Current Decision

No origin is added in this phase. No Cloud Run redeploy is performed.
