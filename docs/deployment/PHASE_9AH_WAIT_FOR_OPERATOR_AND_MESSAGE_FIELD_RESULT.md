# Phase 9AH Wait For Operator And Message Field Result

PHASE_9AH_WAIT_FOR_OPERATOR_STATUS=READY_PENDING_PRIVACY_CONTACT_APPROVAL

Decision state:

```text
BACKEND_DEPLOYED_WAIT_FOR_OPERATOR_READY_PENDING_PRIVACY_CONTACT_APPROVAL
```

Public launch: NO-GO

## Requirement Summary

Phase 9AH improves the operator handover UX without changing official KB/routing behavior and without touching the real Alte site.

Implemented:

- Contact form now includes a question/message textarea.
- Contact form payload maps the textarea to `message`.
- The textarea is prefilled from the latest user message when available.
- Handover card now offers two actions:
  - `დატოვე კონტაქტი` / `Leave contact`
  - `დაელოდე ოპერატორს` / `Wait for operator`
- No-contact wait action sets the chat conversation to `waiting_for_operator`.
- Operator CRM inbox/detail can display waiting status, selected/inferred department, latest message, timestamp, and conversation id.

## Contact Form Fields

Current contact form fields:

- `სახელი და გვარი` / `Full name`
- `ტელეფონი` / `Phone`
- `ენა` / `Language`
- `ელ.ფოსტა` / `Email`
- `ინტერესის სფერო` / `Area of interest`
- `თქვენი კითხვა / შეტყობინება` / `Your question / message`
- consent checkbox
- `გაგზავნა` / `Send`

New textarea:

```text
KA label: თქვენი კითხვა / შეტყობინება
EN label: Your question / message
KA placeholder: დაწერეთ თქვენი კითხვა ან მოკლე ტექსტი ოპერატორისთვის...
EN placeholder: Write your question or message for the operator...
```

Payload mapping:

```text
CONTACT_FORM_MESSAGE_FIELD=message
```

The backend also accepts `question` and `note` aliases for compatibility, but the Pro v2 widget sends `message`.

## Wait For Operator Behavior

When the user clicks `დაელოდე ოპერატორს` / `Wait for operator`:

- the widget calls `/chat/handover/{conversation_id}`;
- it sends `mode=waiting_for_operator`;
- it sends `reason=wait_for_operator`;
- it sends `selected_department`, `selected_topic`, `language`, `source_domain`, and latest user `message`;
- it does not require phone/email/name;
- it does not create a lead/customer/task for anonymous waiting chats;
- it shows the safe confirmation:

```text
თქვენი მოთხოვნა გადაეცა ოპერატორს. გთხოვთ დაელოდოთ — ოპერატორი მალე დაგიკავშირდებათ ამ ჩატში.
```

```text
Your request has been sent to an operator. Please wait — an operator will join this chat soon.
```

## Backend Support Status

BACKEND_WAIT_FOR_OPERATOR_SUPPORT=SUPPORTED_WITH_EXISTING_SCHEMA

No DB migration was required. Existing fields are used:

- `conversations.status = waiting_for_operator`
- `conversations.human_handover = true`
- `messages.metadata_json` for selected department/topic and handover metadata
- `audit_logs.metadata_json` for no-contact waiting handover evidence

No-contact wait action:

- creates no customer;
- creates no lead;
- creates no task;
- records only conversation/message/audit metadata needed for the operator queue.

Production backend deployment:

```text
CLOUD_RUN_REVISION=alte-ai-crm-backend-00033-cbw
BACKEND_DEPLOY_STATUS=DEPLOYED_100_PERCENT_TRAFFIC
```

## Operator CRM Visibility Status

OPERATOR_CRM_WAITING_VISIBILITY=SUPPORTED_LOCALLY_AND_BACKEND_READY

Operator inbox/detail now exposes:

- conversation id;
- waiting status;
- selected/inferred department;
- latest user question/message;
- timestamp;
- no fake contact details.

If no contact form was submitted, customer fields remain empty.

## Unsupported Answer Behavior

Unsupported official-source questions now use this conservative handover copy:

```text
ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე. შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან, რომ თქვენი კითხვა სწორ დეპარტამენტს გადაეცეს.
```

```text
I couldn't find an exact answer in the approved official sources. I can connect you with the relevant operator so your question is routed to the correct department.
```

The copy does not ask the user to type phone/email/name directly.

## Smoke And QA Status

Local/backend verification status:

```text
SYNTHETIC_NO_CONTACT_SMOKE_STATUS=PASSED
VISUAL_QA_STATUS=PASSED
NETLIFY_DEPLOY_STATUS=DEPLOYED_FROM_MASTER_TEST_SITE_ASSETS
```

Production no-contact smoke:

- unsupported 2031 scholarship question returned `no_approved_source_found`;
- unsupported answer offered operator routing without inventing scholarship details;
- assistant did not ask for phone/email/name directly;
- wait-for-operator handover returned `waiting_for_operator`;
- response included no lead id and no task id;
- smoke wrote only conversation waiting metadata.

Production smoke policy:

- unsupported question smoke may run with no contact data;
- wait-for-operator trigger may run only because it writes conversation waiting metadata and no lead/customer/task;
- real contact form submission remains blocked until privacy/contact-flow approval.

Live Netlify visual QA:

- desktop 1440x900: PASS;
- mobile 430x932: PASS, `sidebarVisible=false`;
- mobile 390x844: PASS, `sidebarVisible=false`;
- mobile 375x667: PASS, `sidebarVisible=false`;
- Georgian encoding check: PASS, `hasMojibake=false`;
- Phase 9AH contact/wait UI check: PASS;
- contact modal includes `თქვენი კითხვა / შეტყობინება`;
- handover card includes `დატოვე კონტაქტი` and `დაელოდე ოპერატორს`.

Screenshot evidence:

```text
docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png
docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png
docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png
docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png
```

## Safety Status

```text
PRIVACY_URL_STATUS=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
REAL_CONTACT_DATA_SENT=NO
LEAD_TASK_CUSTOMER_CREATED=NO
DB_MIGRATION_STATUS=NOT_RUN
DB_SEED_STATUS=NOT_RUN
SECRET_MANAGER_CHANGED=NO
REAL_ALTE_SITE_MODIFIED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```

Public launch remains NO-GO.
