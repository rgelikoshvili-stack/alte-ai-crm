# CORS Localhost Test Decision

## Decision

Do not add localhost to production CORS by default.

## Reason

Production CORS should remain limited to the approved Alte domains:

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

Adding local development origins to production CORS would broaden the browser access surface for the deployed backend. Localhost should only be added temporarily if a specific browser smoke test is approved, and then removed immediately after that test.

## Current Confirmed State

- Real production domain `https://alte.edu.ge` CORS preflight: PASS.
- Real production domain `https://join.alte.edu.ge` CORS preflight: PASS.
- Local standalone demo page loads from `http://127.0.0.1:5500`.
- Browser API calls from `http://127.0.0.1:5500` are blocked by CORS: expected FAIL `400`.
- Backend API smoke works outside browser CORS for both `alte.edu.ge` / `ka` and `join.alte.edu.ge` / `en`.

## Options

### A. Recommended

Host or execute the final browser smoke from an allowed Alte domain or an approved staging page whose origin is included in production CORS.

### B. Temporary Test Mode

Temporarily add these local origins to `CORS_ORIGINS`:

- `http://127.0.0.1:5500`
- `http://localhost:5500`

Then redeploy Cloud Run, run the local browser smoke, remove the local origins, and redeploy production-only CORS.

This option requires explicit approval because it changes Cloud Run production configuration.

## Status

```text
LOCALHOST_CORS_NOT_APPROVED_FOR_PRODUCTION
```

Current deployment decision:

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE
```
