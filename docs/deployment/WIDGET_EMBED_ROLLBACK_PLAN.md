# Widget Embed Rollback Plan

## Rollback Actions

1. Remove the widget iframe/script snippet from the website/CMS page.
2. If a config flag is used, disable the widget config.
3. Revert to the previous website version through the CMS or deployment workflow.
4. Clear or invalidate cache if the website/CDN requires it.
5. Confirm the page loads without the widget.
6. Notify backend owner and reviewer owner that rollback was performed.

## Emergency Criteria

Rollback immediately if any of these happen:

- CORS failure on real domain.
- Backend outage affects page behavior.
- Incorrect sensitive answer about tuition, deadlines, requirements, Medicine/MD, international admissions, visa, relocation, or legal topics.
- Unexpected lead/task/customer creation.
- Frontend console errors.
- Performance or layout issue on the website.
- Privacy/consent issue.

## Owners

- Website owner:
- Backend owner:
- Reviewer owner:

## Status

```text
WIDGET_EMBED_ROLLBACK_PLAN_STATUS=PREPARED_PENDING_OWNER_ASSIGNMENT
```
