# Phase 9AG Privacy Contact Approval Gate Result

PHASE_9AG_PRIVACY_CONTACT_GATE_STATUS=NO_GO_PRIVACY_URL_PENDING_CONTACT_FLOW_NOT_APPROVED

Decision state:

```text
BACKEND_DEPLOYED_GEORGIAN_ENCODING_FIXED_PENDING_PRIVACY_AND_EMBED_APPROVAL
```

Public launch: NO-GO

## Scope

- This phase prepares the privacy/contact-flow approval gate only.
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Backend routing/KB logic changed: NO
- CORS changed: NO
- Secret Manager changed: NO
- Production DB changed: NO
- Migration/seed run: NO
- Production contact-flow test executed: NO
- Contact details sent or requested in testing: NO
- Lead/task/customer created: NO

## Current Privacy And Contact Status

```text
PRIVACY_URL_STATUS=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
CONTACT_DATA_TEST_STATUS=NOT_EXECUTED
PUBLIC_LAUNCH_STATUS=NO_GO
LEAD_TASK_CUSTOMER_CREATION_STATUS=NOT_EXECUTED_PENDING_CONTACT_FLOW_APPROVAL
```

No official privacy URL was provided in the Phase 9AG request. The current gate therefore remains pending.

Exact field to fill only after the project owner provides the official URL:

```text
OFFICIAL_PRIVACY_URL=<approved official Alte privacy policy URL>
```

If a URL is later provided, it must:

- start with `https://`;
- be approved by the site/privacy owner;
- be recorded in this gate or a later approval record;
- be inserted into the widget/contact UI only after approval;
- not imply contact-flow approval by itself.

## Existing Configuration Review

- Current docs record privacy/data approval only in principle, pending the official privacy URL.
- Existing widget/privacy docs still reference placeholder privacy URL handling.
- The Phase 9AF readiness doc exists, but its Georgian consent draft is not treated as final because this Phase 9AG package is the current approval gate.
- Contact-flow text exists as draft copy in Georgian and English below.
- Lead/task/customer creation remains disabled/gated for no-contact and informational paths.
- No production contact-flow test was run in this phase.

## Proposed Safe Contact-Flow Copy

Do not enable this as live contact collection until the official privacy URL and contact-flow behavior are approved.

Georgian:

```text
ოპერატორთან დაკავშირების მოთხოვნის გაგზავნამდე, გთხოვთ გაეცნოთ კონფიდენციალურობის პოლიტიკას. თქვენი საკონტაქტო ინფორმაცია გამოყენებული იქნება მხოლოდ თქვენს მოთხოვნაზე პასუხის გასაცემად და შესაბამის დეპარტამენტთან დასაკავშირებლად.
```

English:

```text
Before submitting an operator contact request, please review the Privacy Policy. Your contact information will be used only to respond to your request and connect you with the relevant department.
```

## Approved Vs Blocked Behaviors

Approved before contact-flow approval:

- Answer informational questions from approved sources.
- Return conservative no-approved-source fallback for unsupported questions.
- Show a safe operator/handover card when the user asks for an operator.
- Run no-contact tests.
- Verify that no lead/task/customer is created.

Blocked before contact-flow approval:

- Asking the user to type phone/email/name directly in chat.
- Sending or storing real contact details.
- Running a production contact-flow test with real data.
- Creating a production lead/task/customer.
- Marking contact creation launch-ready.
- Treating privacy URL approval as contact-flow approval.

## Synthetic Contact-Flow Test Requirements

Synthetic contact-flow testing requires all of the following first:

- Official privacy URL provided and approved.
- Legal/privacy owner approved Georgian and English consent copy.
- Contact form fields approved.
- Storage destination approved.
- CRM lead/task/customer creation behavior approved.
- Synthetic contact-flow test explicitly approved.
- Test data format confirmed synthetic only.
- Test result reporting must sanitize any submitted values.

Required approval phrase:

```text
Approve Phase 9AG synthetic contact-flow test only; no real contact data.
```

## Real Contact-Flow Test Requirements

Real contact-flow testing requires all of the following:

- Synthetic contact-flow test passed.
- Official privacy URL is live and visible in the contact UI.
- Final privacy/data approval is recorded.
- Contact-flow owner and CRM owner approve production behavior.
- Real-site embed is approved and no-contact smoke has passed.
- Real contact-flow test approval is explicitly recorded.
- Public launch approval remains separate and must not be inferred.

## CRM Lead/Task/Customer Creation Requirements

CRM record creation must remain gated until:

- user submits an approved contact form;
- consent is visible and accepted;
- official privacy URL is visible;
- required fields are clear;
- CRM destination and operator access roles are approved;
- synthetic test is approved and executed first;
- real-data test is separately approved if needed.

Informational questions and unsupported questions must not create lead/task/customer records.

## Rollback And Safety Rules

- If a placeholder privacy URL appears on a real page, remove or disable the widget until the approved URL is inserted.
- If the assistant asks for phone/email/name directly before approval, rollback the affected widget/backend release.
- If any lead/task/customer is created during no-contact testing, stop testing and investigate before continuing.
- If contact submission works without visible consent or privacy URL, disable contact submission.
- Real-site rollback is removal of the widget config block and widget script tag from the affected template/page.
- Do not change CORS, Secret Manager, DB schema, or production data as part of this gate unless separately approved.

## Approval Checklist

| Approval Item | Status |
| --- | --- |
| Official privacy URL provided | PENDING |
| Privacy URL starts with `https://` | PENDING |
| Legal/privacy owner approved Georgian copy | PENDING |
| Legal/privacy owner approved English copy | PENDING |
| Contact form fields approved | PENDING |
| Storage destination approved | PENDING |
| CRM lead/task creation approved | PENDING |
| Synthetic contact-flow test approved | PENDING |
| Real contact-flow test approved | PENDING |
| Real-site embed approved | PENDING |
| Public launch approved | NO-GO |

## Final Recommendation

```text
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_OFFICIAL_PRIVACY_URL_CONTACT_FLOW_APPROVAL_SYNTHETIC_CONTACT_TEST_FINAL_ASSET_URL_REAL_SITE_EMBED_REAL_DOMAIN_SMOKE_AND_FINAL_PUBLIC_LAUNCH_APPROVAL
```

This gate does not approve or execute contact collection. Public launch remains NO-GO.
