# Phase 9D Department Handover Result

## Implemented

- Added backend department routing helper: `backend/app/services/department_routing_service.py`
- Added request support for widget context:
  - `selected_department`
  - `selected_topic`
  - `page_url`
  - `widget_variant`
- Added response routing fields:
  - `route_department`
  - `department_key`
  - `routing_reason`
- Updated chat service to apply backend-enforced department routing and handover decisions.
- Updated Safe Pro widget to send selected department/topic context on every message.
- Updated Safe Pro widget to display active department context and department-aware handover cards.
- Added safe production smoke script: `backend/app/scripts/production_department_handover_smoke.py`

## Tests Added

- `backend/app/tests/test_department_routing_service.py`
- `backend/app/tests/test_department_handover_chat.py`
- `backend/app/tests/test_widget_department_context.py`

## Deployment Status

Production redeploy is required before Cloud Run serves the Phase 9D routing changes.

```text
PHASE_9D_DEPLOYMENT_STATUS=PENDING_REDEPLOY
```

## Safety Confirmation

- Frontend does not call Anthropic directly.
- Frontend does not expose API keys or secrets.
- Frontend does not create CRM customers/leads/tasks.
- Backend decides routing, handover, lead/task/customer behavior.
- No production DB changes were made in this phase.
- No seed or migration was run.
- No Cloud Run deploy was run.
- Public launch is not complete.

Decision state:

```text
BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY
```
