# Phase 9AP Netlify Redeploy And Visual QA Result

PHASE_9AP_NETLIFY_STATUS=PASSED

Decision state:
BACKEND_DEPLOYED_FULL_CHATBOT_FUNCTIONALITY_FIXES_VERIFIED_PENDING_APPROVALS

Public launch: NO-GO

## Scope

This phase completed live Netlify verification for the Phase 9AP frontend fixes.

Real Alte site modified: NO

REAL_ALTE_SITE_MODIFIED=NO

Real Alte asset upload executed: NO

Real-site embed executed: NO

Backend changed in this phase: NO

Production DB modified: NO

Secret Manager modified: NO

CORS changed: NO

Bridge Hub touched: NO

CONTACT_FLOW_EXECUTED=NO

LEAD_TASK_CUSTOMER_CREATED=NO

REAL_CONTACT_DATA_SENT=NO

## Netlify Deploy Source

Deploy source branch:

```text
master
```

Reason:

Earlier Phase 9AB identified that the Netlify production test site follows the repository default branch, `master`, with publish directory `test_site`.

## Netlify Redeploy Method

Netlify CLI was not used because the previous authenticated CLI redeploy attempt failed with `FAILED_UNAUTHORIZED`.

Redeploy was triggered by pushing the required frontend source sync to `master`.

Master sync commit:

```text
1b89682 phase 9ap: sync netlify frontend fixes
```

Files synced to `master`:

```text
test_site/variants/pro-v2-chat.jsx
test_site/variants/pro-v2-strings.jsx
```

No unrelated dirty files were committed.

## Live Source Freshness

Live source URL checked:

```text
https://nimble-croissant-2f66e8.netlify.app/variants/pro-v2-chat.jsx?phase9ap=1b89682
https://nimble-croissant-2f66e8.netlify.app/variants/pro-v2-strings.jsx?phase9ap=1b89682
```

Result:

```text
LIVE_SOURCE_FRESH=YES
HTTP_STATUS=200
```

Verified live source contains:

```text
latestUserText() || m.text
მედიცინა / MD
```

Verified live source does not contain:

```text
m.text || latestUserText()
მედიცინა/MD
```

Mojibake check:

```text
MOJIBAKE_FOUND=NO
```

## Visual QA

Command:

```text
python -m app.scripts.visual_qa_netlify_widget
```

Result:

```text
VISUAL_QA_STATUS=PASSED
```

Checks:

- Desktop 1440x900: PASS
- Mobile 430x932: PASS
- Mobile 390x844: PASS
- Mobile 375x667: PASS
- No horizontal scroll: PASS
- Georgian text / mojibake: PASS
- Contact textarea visible: PASS
- Wait-for-operator visible: PASS
- Clarification UI visible: PASS

## Focused Contact Prefill Browser Check

Live URL:

```text
https://nimble-croissant-2f66e8.netlify.app/join.html?phase9ap=1b89682
```

Question used:

```text
2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?
```

Result:

```text
CONTACT_PREFILL_PASS=True
MESSAGE_TEXTAREA_VISIBLE=True
NO_MOJIBAKE=True
```

No contact form was submitted.

## Production Focused QA

Command:

```text
python -m app.scripts.production_phase_9ap_fix_9ao_bugs_qa
```

Result:

```text
PRODUCTION_9AP_QA_STATUS=PASSED
PRODUCTION_9AP_QA_CHECKS=16/16
```

Verified:

- Computer Science spring registration answer is source-backed.
- Answer includes 9-14 March.
- Answer includes 30 March.
- Source group is `academic_calendar_2025_2026`.
- No generic AI fallback.
- Broad clarification still works.
- Unsupported question does not hallucinate.
- No lead/task/customer created.
- No real contact data sent.
- No direct contact-data request in normal informational answer.

## Backend Status

No backend redeploy was run in this Netlify phase.

Current deployed backend remains:

```text
Revision: alte-ai-crm-backend-00035-g2b
Image: v0.9-phase-9ap-fix-9ao-qa-bugs
```

## Final Recommendation

Ready for owner approval review: YES

Ready for public launch: NO-GO

Remaining blockers:

- Official Privacy URL
- Contact-flow approval
- Asset upload approval
- Staged real-site embed approval
- Real-domain smoke
- Dirty tree reconciliation
- Final public launch approval
