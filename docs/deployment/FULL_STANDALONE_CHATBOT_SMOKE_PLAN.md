# Full Standalone Chatbot Smoke Plan

Use this plan with:

```text
widget/full-standalone-chatbot-test.html
```

Production backend:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Safe Test Cases

- [x] KA greeting: `გამარჯობა`
- [ ] EN greeting: `Hello`
- [ ] General info no lead.
- [ ] Admissions interest without contact asks for contact and does not create a lead.
- [ ] Admissions interest with controlled test contact creates customer/lead/task only if explicitly approved.
- [x] Finance exact price question does not invent a price.
- [ ] Deadline question does not invent a deadline.
- [x] Medicine from India routes as international/medicine.
- [ ] Human request creates handover/task only if controlled side effects are approved.
- [ ] `sourceDomain=alte.edu.ge` behavior.
- [ ] `sourceDomain=join.alte.edu.ge` behavior.
- [ ] No secrets visible in browser console/network.
- [ ] Consent text visible in KA and EN.

## Phase 8P API Smoke Result

- Backend/API smoke passed without browser CORS.
- Contact-flow flag was not used.
- No phone/email/contact details were submitted.
- No lead/task was intentionally created.
- Observed side effect: the medicine/international admission message triggered existing backend business rules to create a lead/task.
- Phase 8P-Fix applied locally: admissions, international admissions, and medicine admissions require phone or email before lead/task creation.
- Expected post-fix behavior: no contact -> ask for contact details and save conversation/AI summary only; contact present -> create/update customer, lead, and task.
- Human request chat behavior remains contact-gated for task creation; the explicit handover endpoint remains the exception path.
- Cloud Run redeploy is required before production has the no-contact guard.
- Production test knowledge seed was not run.

## Phase 8Q Seeded Knowledge Smoke Result

- Production test knowledge seed executed after explicit approval.
- Idempotency verified: second run created zero new records and skipped existing snippets.
- Safe API smoke after seed passed.
- Contact-flow test was not run.
- No phone/email/contact details were submitted.
- No intentional production lead/task creation was performed.
- Finance exact price behavior remains conservative and did not create lead/task.
- Deadline behavior remains conservative and did not create lead/task.
- Medicine/international no-contact behavior remains guarded: no lead/task, `phone_or_email` requested.
- Official content review remains required before public launch.

## CORS Caveat

Production CORS is intentionally restricted to:

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

Local browser testing from `http://127.0.0.1:5500` may be blocked. Backend/API smoke can still be run without browser CORS:

```powershell
python -m app.scripts.standalone_chatbot_api_smoke
```

Full browser smoke should happen from an allowed Alte domain or after a separately approved temporary CORS test mode.
