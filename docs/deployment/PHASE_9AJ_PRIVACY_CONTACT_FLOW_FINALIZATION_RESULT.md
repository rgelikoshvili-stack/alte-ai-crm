# Phase 9AJ Privacy Contact Flow Finalization Result

PHASE_9AJ_PRIVACY_CONTACT_FLOW_STATUS=READY_PENDING_OFFICIAL_PRIVACY_URL_AND_CONTACT_FLOW_APPROVAL

Decision state:

```text
BACKEND_DEPLOYED_CHATGPT_STYLE_KB_ROUTING_OPERATOR_READY_PENDING_PRIVACY_CONTACT_APPROVAL
```

Public launch: NO-GO

## Current Status

```text
PRIVACY_URL_STATUS=PENDING
OFFICIAL_PRIVACY_URL=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
CONTACT_DATA_TEST_STATUS=NOT_EXECUTED
PUBLIC_LAUNCH_STATUS=NO_GO
```

The official Alte privacy URL has not been provided in this phase. Real contact-flow testing and production contact data collection remain blocked.

## Contact Form Fields

The contact form approval scope includes these fields:

- name
- phone
- language
- email
- interest/department
- question/message
- consent checkbox
- submit button

Question/message field:

```text
KA label: თქვენი კითხვა / შეტყობინება
EN label: Your question / message
Payload field: message
```

## Consent Copy Draft

Georgian:

```text
ვეთანხმები, რომ ჩემი საკონტაქტო ინფორმაცია გამოყენებული იქნას მხოლოდ ჩემს მოთხოვნაზე პასუხის გასაცემად და შესაბამის დეპარტამენტთან დასაკავშირებლად. გავეცანი კონფიდენციალურობის პოლიტიკას.
```

English:

```text
I agree that my contact information may be used only to respond to my request and connect me with the relevant department. I have reviewed the Privacy Policy.
```

This copy is a draft and must be approved by the appropriate legal/privacy owner before real contact collection.

## Privacy URL Handling

If the official privacy URL is not provided:

```text
PRIVACY_URL_STATUS=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
CONTACT_DATA_TEST_STATUS=NOT_EXECUTED
PUBLIC_LAUNCH_STATUS=NO_GO
```

If the official privacy URL is provided later:

- record it exactly in this approval package;
- validate that it starts with `https://`;
- set `PRIVACY_URL_STATUS=PROVIDED_PENDING_APPROVAL`;
- keep `CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED` until separate approval is recorded;
- do not run real contact-flow unless separately approved.

## Contact Form Submit Behavior

After user submits the approved contact form, the intended behavior is:

- send contact details only through backend endpoints;
- include the selected/inferred department;
- include the question/message text in the `message` field;
- include consent acceptance metadata;
- route the request to the correct operator/CRM queue;
- create lead/task/customer records only after explicit approval and only under the approved storage policy.

Current status:

```text
CONTACT_FORM_SUBMIT_WITH_REAL_DATA=BLOCKED
CRM_LEAD_TASK_CUSTOMER_CREATION_APPROVAL=NOT_APPROVED
```

## Wait For Operator Behavior

When the user clicks "Wait for operator" / "დაელოდე ოპერატორს":

- phone/email/name are not required;
- the conversation is marked for operator attention when the existing backend/CRM flow supports it;
- the operator should see conversation id, department, latest user message, waiting status, and timestamp;
- no lead/customer is automatically created from the wait action;
- no fake contact details are required.

Current status:

```text
WAIT_FOR_OPERATOR_CONTACT_DATA_REQUIRED=NO
WAIT_FOR_OPERATOR_LEAD_CUSTOMER_AUTO_CREATE=NO
```

## Approval Gates

Contact form submission must remain gated until all of these are approved:

- official privacy URL approved;
- consent copy approved;
- storage destination approved;
- CRM lead/task creation approved;
- synthetic contact-flow test approved;
- real data launch approved;
- real-site embed approved.

## Synthetic Test Policy

Synthetic contact-flow testing may run only after explicit approval text is recorded.

Required approval text:

```text
Approve Phase 9AJ synthetic contact-flow test with non-real contact data only.
```

Synthetic data must be clearly fake, must not include real phone/email/name, and must be removed or marked test-only according to the approved CRM cleanup policy.

## Real Data Test Policy

Real data testing is not approved in this phase.

Before any real contact data test:

- official privacy URL must be approved and visible;
- final consent copy must be approved;
- storage/CRM destination must be approved;
- retention/access policy must be approved;
- synthetic test must pass;
- site owner must approve real-data test execution.

## Lead Task Customer Creation Policy

```text
LEAD_TASK_CUSTOMER_CREATION_EXECUTED=NO
LEAD_TASK_CUSTOMER_CREATION_WITH_REAL_DATA=BLOCKED
```

Informational questions and no-contact operator handover must not create lead/task/customer records.

Lead/task/customer creation may be enabled only for an approved contact form submission with consent, approved privacy URL, approved storage destination, and explicit launch/test approval.

## Rollback Policy

If privacy/contact-flow approval is blocked or revoked:

- keep the real-site embed blocked;
- keep public launch NO-GO;
- disable contact form submission if enabled in a future phase;
- keep wait-for-operator available only if it does not collect personal data;
- remove or hide any unapproved privacy copy or placeholder URL;
- verify no production contact data was collected in the blocked state.

## Safety Status

```text
REAL_CONTACT_DATA_SENT=NO
CONTACT_FLOW_EXECUTED=NO
LEAD_TASK_CUSTOMER_CREATED=NO
DB_MIGRATION_STATUS=NOT_RUN
DB_SEED_STATUS=NOT_RUN
SECRET_MANAGER_CHANGED=NO
REAL_ALTE_SITE_MODIFIED=NO
FRONTEND_API_KEYS_EXPOSED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```

Public launch remains NO-GO.
