# Phase 9N-CORS Test Origin Plan

PHASE_9N_CORS_TEST_ORIGIN_STATUS=PENDING_TEST_ORIGIN_URL

## Purpose

Test the Safe Pro Sidebar widget in a real browser from a non-Alte temporary hosted page before touching the real Alte website.

## Current Status

- TEST_ORIGIN_URL=PENDING
- TEST_ORIGIN_CORS_APPROVAL_STATUS=PENDING
- TEST_ORIGIN_CORS_DEPLOY_STATUS=NOT_EXECUTED
- HOSTED_BROWSER_SMOKE_STATUS=NOT_EXECUTED

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

## Current Decision

No production CORS update is executed until a concrete test origin URL and explicit approval are recorded.
