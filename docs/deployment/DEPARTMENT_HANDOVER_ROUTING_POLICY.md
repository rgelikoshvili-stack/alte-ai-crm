# Department Handover Routing Policy

## Purpose

The website chatbot must answer from the Knowledge Base only when it has enough approved source confidence. If confidence is low, source is missing, the topic is sensitive, or the student asks for a human, the backend routes the conversation to the correct department/operator.

The frontend sends context only. It does not decide CRM actions, lead creation, handover, or task creation.

## Departments

| Topic | Department |
| --- | --- |
| Admission, application, programs, enrollment, bachelor, master | Admissions |
| International student, foreign applicant, `join.alte.edu.ge`, visa, relocation, India, Nigeria, Pakistan, Nepal, Bangladesh | International Admissions |
| Medicine, MD, Dentistry, clinical/medical program | Medicine / MD |
| Tuition, fees, payment, scholarship, grant, loan, funding | Finance |
| Deadline, academic calendar, intake, registration | Admissions / Academic Registry confirmation |
| Required documents | Admissions |
| International required documents | International Admissions |
| Library, career, clubs, ombudsman, mentor, student life | Student Services |
| Portal, login, EMIS, technical issue, website issue | IT Support |
| Unknown question without context | General / Admissions fallback |

## Sidebar Context

The Safe Pro widget sends these fields on every message:

- `selected_department`
- `selected_topic`
- `source_domain`
- `language`
- `page_url`
- `widget_variant`

If the message is ambiguous, the backend may use `selected_department` as the routing target. Strong message keywords override sidebar context.

## Handover Conditions

The backend sets `should_handover=true` when:

- confidence is below `0.70`;
- approved source is missing for a sensitive topic;
- the topic is sensitive and requires official confirmation;
- the AI cannot answer;
- the student asks for a human/operator;
- selected sidebar context indicates a department and the answer is uncertain.

Response fields include:

- `route_department`
- `department_key`
- `handover_reason`
- `routing_reason`

## Sensitive Topics

Sensitive topics include tuition/prices, deadlines, grants, scholarships, required documents, Medicine/MD requirements, international admissions requirements, visa/relocation/legal wording, accreditation, payment, and contracts.

If exact approved source is missing, the chatbot must not invent facts. It should route to the correct department/operator.

## No-Contact Lead Guard

- General info, finance, deadline, tuition, documents, and program questions without phone/email must not create customer/lead/task unless a separately approved handover task policy requires task-only routing.
- Admission/program/medicine/international interest without phone/email asks for contact details before lead creation.
- With phone/email, existing lead/task/customer policy may run.
- Backend enforces this. Frontend does not create CRM records.

## Examples

- KA: `რა ღირს სწავლა?` -> Finance; conservative answer or Finance handover; no lead without contact.
- EN: `How much is medicine tuition?` -> Finance or Medicine/MD plus Finance context; no lead without contact.
- KA: `რა საბუთებია საჭირო?` with International selected -> International Admissions.
- EN: `I want to apply for medicine from India` -> Medicine / MD with international priority; ask for phone/email before lead.
- EN: `I have a portal login problem` -> IT Support.
- KA: selected Finance + `მაინტერესებს დეტალები` -> Finance handover/context.
## Phase 9D-Redeploy Verification Note

Image `v0.9-department-routing-sidebar` was deployed to Cloud Run and production endpoint checks passed.

Production smoke result:

- Department routing smoke: `26/28` passed
- Finance no-contact smoke: `24/24` passed
- Broader knowledge smoke: `25/25` passed

Open routing issue:

- Ambiguous sidebar messages must preserve explicit `selected_department` / `selected_topic` context.
- Current production verification found Finance and Medicine ambiguous sidebar cases routing to `Admissions`.

Policy clarification:

- When the user selects a sidebar department and then sends an ambiguous message, selected sidebar context must outrank a generic AI department guess.
- Strong message keywords can override sidebar context only when the message is clearly about another department.

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```

## Phase 9E Sidebar Ambiguity Rule

The routing implementation has been updated so ambiguous sidebar messages preserve `selected_department`.

Rule:

1. Strong explicit user-message keywords win.
2. Explicit human/operator request uses `selected_department` when present.
3. Ambiguous/generic/low-information messages use `selected_department`.
4. AI intent is used after sidebar ambiguity handling.
5. Domain defaults are used after that.

Examples:

- Finance sidebar + `მაინტერესებს დეტალები` -> Finance.
- Medicine sidebar + `დეტალები მაინტერესებს` -> Medicine / MD.
- Finance sidebar + `პორტალში ვერ შევდივარ` -> IT Support.
- Medicine sidebar + `სტიპენდია მაინტერესებს` -> Finance.

Redeploy is required before this fixed behavior is active in production.

Decision state:

```text
BACKEND_CODE_FIXED_SIDEBAR_AMBIGUOUS_ROUTING_PENDING_REDEPLOY
```
