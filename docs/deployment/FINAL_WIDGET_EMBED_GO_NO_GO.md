# Final Widget Embed Go/No-Go

## GO Only If

- [ ] Cloud Run backend health is 200.
- [ ] `/diagnostics/ai` is 200 and no secrets are exposed.
- [ ] CORS for `alte.edu.ge` passes.
- [ ] CORS for `join.alte.edu.ge` passes.
- [ ] website developer/admin access approved.
- [ ] privacy/data approval completed.
- [ ] final widget asset URL confirmed.
- [ ] rollback owner assigned.
- [ ] hidden/staging test page identified.
- [ ] smoke checklist owner assigned.

## NO-GO If

- privacy approval pending.
- website access pending.
- final widget asset URL missing.
- CORS fails for real domains.
- rollback plan missing.
- secrets appear in docs/browser/logs.
- widget breaks page layout.
- no owner for post-embed monitoring.

## Current Decision

```text
NO-GO_FOR_ACTUAL_SITE_EMBED
```
