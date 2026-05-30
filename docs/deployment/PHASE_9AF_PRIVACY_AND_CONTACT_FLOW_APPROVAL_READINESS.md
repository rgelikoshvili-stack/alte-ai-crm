# Phase 9AF Privacy And Contact Flow Approval Readiness

PHASE_9AF_PRIVACY_CONTACT_READINESS_STATUS=NO_GO_PENDING_OFFICIAL_PRIVACY_URL_AND_CONTACT_FLOW_APPROVAL

Decision state:

```text
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL
```

Public launch: NO-GO

## Scope

- This is an approval-readiness package only.
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Backend production behavior changed: NO
- CORS changed: NO
- Secret Manager changed: NO
- Production DB changed: NO
- Migration/seed run: NO
- Real contact details requested or sent: NO
- Lead/task/customer creation executed: NO
- Production contact-flow test executed: NO

## Current Privacy URL Status

```text
OFFICIAL_PRIVACY_URL_STATUS=PENDING
```

The official Alte privacy policy URL has not been provided or recorded yet. Privacy/data approval remains in-principle only until the official URL and contact-flow copy are approved by the responsible owner.

Exact field to fill after approval:

```text
OFFICIAL_PRIVACY_URL=<approved official Alte privacy policy URL>
```

Approved URL insertion points before real-site embed:

- Widget privacy link in the contact card / consent area.
- Widget footer/settings privacy link, if visible.
- Final embed approval record.
- Real-domain smoke checklist.
- Any website CMS/template copy that references chatbot data handling.

Do not publish the widget on the real site with `#privacy-policy-pending` or any placeholder privacy URL.

## Proposed Contact-Flow Policy

Contact-flow status:

```text
CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST
```

- The bot may answer informational questions without asking for contact details.
- If the user asks for an operator, the widget may show a safe handover/contact card.
- Before approval, assistant text must not ask the user to type phone, email, full name, WhatsApp, or other personal contact details directly in free text.
- Before approval, no production lead, task, or customer record may be created.
- Once approved, contact collection must happen through an explicit contact form or clearly approved contact UI, not through an ambiguous chatbot prompt.
- Contact data creation must be tested separately with approved synthetic data only.

## Proposed Consent Copy

Georgian:

```text
ოპერატორთან დაკავშირების მოთხოვნის გაგზავნით ადასტურებთ, რომ ეთანხმებით თქვენი საკონტაქტო მონაცემების გამოყენებას მხოლოდ კონსულტაციისთვის, თქვენს მოთხოვნაზე პასუხის გასაცემად და შესაბამის დეპარტამენტთან დასაკავშირებლად. მონაცემების დამუშავება მოხდება ალტე უნივერსიტეტის კონფიდენციალურობის პოლიტიკის შესაბამისად.
```

English:

```text
By submitting an operator contact request, you confirm that you agree to the use of your contact details only for consultation, responding to your request, and connecting you with the relevant Alte University department. Your data will be processed according to Alte University's Privacy Policy.
```

Short Georgian card text:

```text
ოპერატორთან დაკავშირებისთვის გამოიყენეთ დამტკიცებული საკონტაქტო ფორმა. ფორმის გაგზავნამდე გაეცანით კონფიდენციალურობის პოლიტიკას და დაადასტურეთ თანხმობა.
```

Short English card text:

```text
To contact an operator, use the approved contact form. Before submitting it, review the Privacy Policy and confirm consent.
```

## Contact Form Requirements After Approval

The approved contact form must show:

- Official privacy URL.
- Consent text.
- Clear purpose of collection.
- Required fields.
- Submit action.
- Department or topic context, when available.
- Confirmation that the request will be sent to the relevant Alte University team.

The approved form must avoid:

- Hidden consent.
- Prechecked consent boxes.
- Open-ended requests for personal details before the form is shown.
- Creating CRM records before the user submits the approved form.

## Approved And Disallowed Contact Data Behavior

Allowed before contact-flow approval:

- Source-backed informational answers.
- Unsupported-answer fallback with no approved source.
- Operator/handover card without collecting personal data.
- No-contact smoke tests.
- Verifying that no lead/task/customer is created.

Disallowed before contact-flow approval:

- Asking the user to type phone/email/name directly.
- Sending or storing real contact details.
- Running a production contact-flow test.
- Creating a production lead/task/customer.
- Marking CRM contact creation ready for launch.

Allowed only after explicit approval:

- Synthetic-data-only contact-flow test.
- Verification that a synthetic request appears in Operator CRM.
- Recording synthetic CRM IDs in a sanitized test report.
- Cleanup/archive only through a separately approved process.

## No-Contact Testing Policy

No-contact tests may continue to verify:

- Informational questions do not create lead/task/customer.
- Operator intent does not request direct phone/email/name in assistant text.
- Contact card appears only as a safe approval-gated next step.
- Unsupported questions do not invent facts.
- Real-domain smoke can validate widget load, routing, and answer behavior without contact details.

No-contact tests must not:

- Submit a contact form.
- Enter personal data.
- Trigger intentional CRM record creation.
- Use real applicant/user contact details.

## Required Before Synthetic Contact Data Test

All items below must be approved before any synthetic contact-flow test:

- Official privacy URL provided.
- Legal/privacy owner approved the text.
- Contact form fields approved.
- Consent copy approved in Georgian and English.
- Storage destination approved.
- CRM lead/task creation behavior approved.
- Synthetic contact-flow test approved.
- Test data format approved as synthetic only.
- Cleanup/archive owner approved, if cleanup is needed.

Required approval phrase:

```text
Approve Phase 9AF synthetic contact-flow test only; no real contact data.
```

## Required Before Real Contact Data Flow

All items below must be completed before any real contact data is accepted:

- Official privacy URL is live and linked from the widget.
- Final privacy/data approval is recorded.
- Contact-flow behavior is approved by legal/privacy owner and business owner.
- CRM storage destination and operator access roles are approved.
- Synthetic contact-flow test has passed.
- Real-site embed has been approved and passed no-contact smoke.
- Real contact-flow test approval is explicitly recorded.
- Public launch approval remains separate and must not be inferred.

## Lead/Task/Customer Creation Gate

Lead/task/customer creation status:

```text
LEAD_TASK_CUSTOMER_CREATION_STATUS=NOT_EXECUTED_PENDING_CONTACT_FLOW_APPROVAL
```

Before any lead/task/customer creation is allowed:

- User must submit the approved contact form.
- Consent must be visible and accepted.
- Privacy URL must be visible.
- Required fields must be explicit.
- CRM destination must be approved.
- The test must use synthetic data unless real-data testing is separately approved.

Informational questions and unsupported questions must never create lead/task/customer records.

## Approval Checklist

| Approval Item | Status |
| --- | --- |
| Official privacy URL provided | PENDING |
| Legal/privacy owner approved text | PENDING |
| Contact form fields approved | PENDING |
| Consent copy approved in Georgian | PENDING |
| Consent copy approved in English | PENDING |
| Storage destination approved | PENDING |
| CRM lead/task creation approved | PENDING |
| Synthetic contact-flow test approved | PENDING |
| Real contact-flow test approved | PENDING |
| Real-site embed approved | PENDING |
| Final public launch approved | NO-GO |

## Rollback And Safety Notes

- If the widget shows a placeholder privacy URL on the real site, remove the widget until the approved URL is inserted.
- If the assistant asks for phone/email/name directly before approval, rollback the affected widget/backend change.
- If any lead/task/customer is created during no-contact testing, stop testing and investigate before continuing.
- If the contact form submits without visible consent or privacy URL, disable the contact-flow UI.
- Rollback real-site embed by removing the widget config block and widget script tag from the affected page/template.
- Do not change CORS, Secret Manager, DB schema, or production data as part of a contact-flow rollback unless separately approved.

## Final Recommendation

```text
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_OFFICIAL_PRIVACY_URL_CONTACT_FLOW_APPROVAL_SYNTHETIC_CONTACT_TEST_REAL_SITE_EMBED_REAL_DOMAIN_SMOKE_AND_FINAL_PUBLIC_LAUNCH_APPROVAL
```

This package prepares the approval path. It does not approve or execute real contact collection.
