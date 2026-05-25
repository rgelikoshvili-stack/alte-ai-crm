# Phase 9N Test Site Browser Smoke Checklist

BROWSER_TEST_SITE_SMOKE_STATUS=PENDING_MANUAL_OR_HOSTED_TEST

## Checklist

- [ ] Open `test_site/index.html` locally or hosted URL.
- [ ] Open `test_site/join.html` locally or hosted URL.
- [ ] Widget visible.
- [ ] Sidebar visible.
- [ ] KA/EN switch works.
- [ ] DevTools Network shows no `api.anthropic.com`.
- [ ] DevTools Network exposes no API key.
- [ ] DevTools Network calls only the backend Cloud Run API.
- [ ] KA questions tested.
- [ ] EN join page questions tested.
- [ ] No contact details sent.
- [ ] No intentional lead/task/customer creation.

## CORS Handling

If a CORS error appears from local or non-allowed test origin:

- Record it as expected for a non-allowed origin.
- Do not treat it as a backend failure.
- Request optional test origin CORS approval before full browser test.
