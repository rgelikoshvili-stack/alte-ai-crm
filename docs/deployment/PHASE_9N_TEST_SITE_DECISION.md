# Phase 9N-Test Site Decision

PHASE_9N_TEST_SITE_STATUS=LOCAL_TEST_PACKAGE_READY_PENDING_OPTIONAL_TEST_ORIGIN

## Option A - Local Preview Only

- No Cloud/GCP changes.
- Good for UI preview.
- Browser API may be blocked by production CORS.
- API smoke uses backend scripts.

## Option B - Temporary Hosted Test Domain

Example:

```text
https://alte-ai-chat-test.<approved-domain>
```

- Requires hosting and CORS allowlist.
- Allows real browser test before Alte site embed.
- Requires explicit approval before CORS change/deploy.

## Option C - Alte Hidden Test Page

- Best full browser test.
- Touches Alte website.
- Not executed in this phase unless explicitly approved.

## Recommendation

Prepare the local `test_site/` package now and do not modify the real Alte site. If full browser testing is required, request approval for a temporary test origin and CORS update.
