# Actual Site Embed Runbook

Do not execute these steps in Phase 9G-H.

Phase 9I selected Alte-controlled hosting. Use this placeholder unless the website team chooses another approved path:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

Actual upload and embed are still not executed.

## Prerequisites

- Privacy approved
- Content approval decided
- Final asset URL selected
- Website admin/developer access confirmed
- Rollback owner assigned

## Embed Steps

1. Upload static widget asset.
2. Insert config/snippet on test/staging page if available.
3. Verify widget loads.
4. Run real-domain browser smoke.
5. Verify CORS.
6. Verify no direct Anthropic browser calls.
7. Verify no contact-flow test in safe smoke.
8. Verify no unexpected lead/task/customer creation.
9. Approve public rollout only after explicit approval.

## Rollback Steps

- Remove the script snippet.
- Disable widget config.
- Restore previous page version.

## Emergency Criteria

- CORS failure
- Backend outage
- Incorrect sensitive answer
- Unexpected lead/customer/task creation
- Frontend console errors
- Performance/layout issue
