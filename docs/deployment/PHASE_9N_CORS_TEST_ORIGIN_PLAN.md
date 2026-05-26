# Phase 9N-CORS Test Origin Plan

PHASE_9N_CORS_TEST_ORIGIN_STATUS=APPROVED_PENDING_CORS_UPDATE

## Purpose

Test the Safe Pro Sidebar widget in a real browser from a non-Alte temporary hosted page before touching the real Alte website.

## Current Status

- TEST_ORIGIN_URL=https://alte-ai-chat-test.netlify.app
- TEST_ORIGIN_CORS_APPROVAL_STATUS=APPROVED_FOR_TEMPORARY_BROWSER_SMOKE
- TEST_ORIGIN_CORS_DEPLOY_STATUS=EXECUTED
- HOSTED_BROWSER_SMOKE_STATUS=BLOCKED_CORS_ACTUAL_NETLIFY_ORIGIN_PENDING_UPDATE
- TEMP_CORS_UPDATE_APPROVED_ORIGIN=https://nimble-croissant-2f66e8.netlify.app
- ACTUAL_NETLIFY_TEST_ORIGIN=https://nimble-croissant-2f66e8.netlify.app
- PREVIOUS_PLANNED_TEST_ORIGIN=https://alte-ai-chat-test.netlify.app

## Required Before CORS Update

1. Final test origin URL.
2. Approval to add the temporary origin to production CORS.
3. Approval to redeploy Cloud Run.
4. Rollback/removal plan.

## Candidate Hosting Options

### Option A - User-Owned Temporary Domain/Subdomain

- Recommended if the user controls DNS/hosting.
- Example: `https://alte-chat-test.example.com`

### Option B - Netlify/Vercel Static Page

- Fast static hosting option.
- Requires exact final HTTPS origin before CORS approval.

### Option C - Cloud Storage Static Hosting

- Possible Google Cloud static hosting option.
- Requires separate approved GCP work if used.

### Option D - GitHub Pages

- Simple static hosting option.
- Requires exact final HTTPS origin before CORS approval.

## Recommendation

Use a user-controlled temporary HTTPS origin.

## Security

- Do not add wildcard CORS.
- Add exact origin only.
- Do not enable credentials unless explicitly required and approved.
- Remove the temporary origin after test if it is not needed.

## Execution Update

- Temporary test origin URL recorded: `https://alte-ai-chat-test.netlify.app`
- CORS update executed on Cloud Run.
- Final serving revision: `alte-ai-crm-backend-00009-bhk`
- Image unchanged: `v0.9-security-reliability-fixes`
- Hosted browser smoke remains pending manual verification.
- Actual deployed Netlify origin is `https://nimble-croissant-2f66e8.netlify.app`; it needs to be added to production CORS before browser retest.
