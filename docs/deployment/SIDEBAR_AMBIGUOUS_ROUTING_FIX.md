# Sidebar Ambiguous Routing Fix

## Bug Found

Phase 9D-Redeploy deployed image `v0.9-department-routing-sidebar`, but production department routing smoke failed two ambiguous sidebar-context cases:

1. `selected_department=finance` + message `მაინტერესებს დეტალები` routed to `Admissions`.
2. `selected_department=medicine` + message `დეტალები მაინტერესებს` routed to `Admissions`.

No customer, lead, task, contact-flow, or contact-detail side effect occurred. The bug was limited to department selection priority.

## Expected Behavior

When a user chooses a sidebar department and then sends an ambiguous or generic message, the selected sidebar department must be preserved.

Examples:

- `selected_department=finance` + `მაინტერესებს დეტალები` -> `finance`
- `selected_department=medicine` + `დეტალები მაინტერესებს` -> `medicine`
- `selected_department=international` + `details please` -> `international`
- `selected_department=it_support` + `help please` -> `it_support`
- `selected_department=student_services` + `მეტი ინფორმაცია მინდა` -> `student_services`

## Strong Keyword Override

Strong explicit message keywords still override sidebar context when the user clearly asks about another department.

Examples:

- `selected_department=finance` + `პორტალში ვერ შევდივარ` -> `it_support`
- `selected_department=medicine` + `სტიპენდია მაინტერესებს` -> `finance`
- `selected_department=admissions` + `I need visa help` -> `international`

## Implementation

The backend routing helper now:

- detects ambiguous low-information messages;
- uses strong message keywords from the user message only;
- avoids letting a generic AI department guess override selected sidebar context;
- applies `selected_department` when the message is ambiguous and no strong keyword points elsewhere;
- records routing reason `sidebar_context_for_ambiguous_message`.

## No-Contact Guard

No-contact behavior is unchanged:

- no phone/email -> no customer;
- no phone/email -> no lead;
- no phone/email -> no admissions lead;
- finance/tuition/deadline no-contact remains no lead/task/customer;
- frontend still does not create CRM records.

## Verification

Added tests:

- `backend/app/tests/test_sidebar_ambiguous_department_priority.py`
- `backend/app/tests/test_phase_9e_sidebar_ambiguous_routing_fix.py`

## Redeploy

Redeploy is required before production behavior changes.

Decision state:

```text
BACKEND_CODE_FIXED_SIDEBAR_AMBIGUOUS_ROUTING_PENDING_REDEPLOY
```
