# Phase 9AI ChatGPT-Style KB Clarification Operator Result

PHASE_9AI_STATUS=PASSED_PENDING_PRIVACY_CONTACT_APPROVAL

Decision state:

```text
BACKEND_DEPLOYED_CHATGPT_STYLE_KB_ROUTING_OPERATOR_READY_PENDING_PRIVACY_CONTACT_APPROVAL
```

Public launch: NO-GO

## Problem Solved

Phase 9AI implements the ChatGPT-style decision flow for Alte's approved knowledge base:

User question -> detect language -> classify department/topic -> ask clarification when broad or ambiguous -> search the relevant source group -> answer only from approved sources -> offer the correct department/operator when no exact approved answer exists.

The chatbot must not blindly search every file before understanding the topic.

## Department And Source Maps

Department/topic/source map:

```text
backend/app/data/knowledge/department_topic_source_map.json
```

Source groups:

```text
backend/app/data/knowledge/source_groups.json
```

Mapped departments:

- admissions
- programs
- finance
- study_process
- academic_calendar
- international_admissions
- medicine_md
- library
- career
- it_support
- human_operator

Important routing rule:

```text
Do NOT route to international admissions just because source_domain is join.alte.edu.ge.
Only route there when user text explicitly indicates international/foreign context.
```

## Clarification Behavior

Generic Georgian clarification:

```text
ზუსტად რომ გიპასუხოთ, გთხოვთ დააზუსტოთ — რომელი საკითხი გაინტერესებთ?
```

Options:

- მიღება
- პროგრამები
- სწავლის საფასური
- სტუდენტის სტატუსი

Generic English clarification:

```text
To answer accurately, please clarify which topic you mean.
```

Specific Georgian clarifications:

```text
რომელ პროგრამაზე გსურთ ინფორმაცია — ბაკალავრიატზე, მაგისტრატურაზე, მედიცინა/MD-ზე თუ საერთაშორისო მიღებაზე?
```

```text
გადახდებზე რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: სწავლის საფასური გაინტერესებთ, გადახდის გრაფიკი თუ ფინანსურ დეპარტამენტთან დაკავშირება?
```

```text
სტუდენტის სტატუსთან დაკავშირებით რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: შეჩერება, აღდგენა, შეწყვეტა თუ მობილობა გაინტერესებთ?
```

Clarification replies do not ask for phone/email/name and do not create lead/task/customer records.

## Scoped Retrieval Behavior

The backend computes `department_key` and `source_group` before retrieval.

Primary source routing examples:

- Bachelor/Master ECTS -> `official_academic_rules`
- Student status and mobility -> `student_status_and_mobility`
- Calendar dates -> `academic_calendar_2025_2026`
- Admission documents -> `admissions_rules`
- Finance -> `finance_sources`, with conservative fallback if exact approved support is missing
- Library -> `library_sources`, with conservative fallback if exact approved support is missing
- IT support -> `it_support_sources`, with conservative fallback if exact approved support is missing

Official KB facts preserved:

- Bachelor completion: 240 ECTS, not 180.
- Master: 120 ECTS.
- Student status suspension: max 5 years.
- Computer Science spring registration: 9–14 March; semester starts 30 March.

## Unsupported Answer Behavior

Georgian unsupported copy:

```text
ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე. შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან, რომ თქვენი კითხვა სწორ დეპარტამენტს გადაეცეს.
```

English unsupported copy:

```text
I couldn’t find an exact answer in the approved official sources. I can connect you with the relevant operator so your question is routed to the correct department.
```

Unsupported answers offer operator handover and do not invent scholarships, prices, discounts, deadlines, or contact details.

## Contact Message Field

The contact form includes the question/message textarea:

```text
KA label: თქვენი კითხვა / შეტყობინება
EN label: Your question / message
KA placeholder: დაწერეთ თქვენი კითხვა ან მოკლე ტექსტი ოპერატორისთვის...
EN placeholder: Write your question or message for the operator...
Payload field: message
```

The field is prefilled from the latest user message when possible and can be edited by the user.

## Wait For Operator

Wait-for-operator action:

```text
KA action: დაელოდე ოპერატორს
EN action: Wait for operator
```

Confirmation:

```text
თქვენი მოთხოვნა გადაეცა ოპერატორს. გთხოვთ დაელოდოთ — ოპერატორი მალე დაგიკავშირდებათ ამ ჩატში.
```

```text
Your request has been sent to an operator. Please wait — an operator will join this chat soon.
```

Operator CRM visibility remains aligned for:

- waiting status
- department
- latest user question/message
- timestamp
- conversation id

No fake contact details are required for waiting-for-operator, and wait-for-operator does not automatically create a lead/customer.

## QA Status

Local tests:

```text
PYTEST_STATUS=PASSED_852
VERIFIER_STATUS=PASSED
```

Production QA:

```text
PRODUCTION_9AI_CHATGPT_STYLE_QA_STATUS=PASSED_12_OF_12
PRODUCTION_9AI_CHATGPT_STYLE_QA_REPORT=docs/evaluation/PHASE_9AI_CHATGPT_STYLE_ROUTING_QA_RESULT.md
CLOUD_RUN_REVISION=alte-ai-crm-backend-00034-rgn
```

Visual QA:

```text
VISUAL_QA_STATUS=PASSED
NETLIFY_REDEPLOY_REQUIRED=NO_FRONTEND_ASSETS_CHANGED
```

Visual QA confirmed:

- desktop 1440x900 PASS;
- mobile 430x932 PASS, sidebar hidden;
- mobile 390x844 PASS, sidebar hidden;
- mobile 375x667 PASS, sidebar hidden;
- Georgian encoding PASS, no mojibake;
- contact textarea PASS;
- wait-for-operator action PASS;
- "სწავლა მაინტერესებს" clarification UI PASS.

## Safety Status

```text
REAL_CONTACT_DATA_SENT=NO
LEAD_TASK_CUSTOMER_CREATED=NO
DB_MIGRATION_STATUS=NOT_RUN
DB_SEED_STATUS=NOT_RUN
SECRET_MANAGER_CHANGED=NO
REAL_ALTE_SITE_MODIFIED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```

Public launch remains NO-GO.
