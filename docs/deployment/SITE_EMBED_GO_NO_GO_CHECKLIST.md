# Site Embed GO/NO-GO Checklist

SITE_EMBED_GO_NO_GO_STATUS=NO_GO_PENDING_APPROVALS

Phase 9K update: security/reliability fixes are code-complete locally and pending redeploy. The widget privacy URL placeholder `#privacy-policy-pending` remains a GO blocker until the official URL is approved.

Phase 9L-M-N update: final approval intake, website handoff package, asset manifest, actual-embed execution record, real-domain smoke plan/result, and public launch decision are prepared. Site embed remains NO-GO until approvals and execution are complete.

Decision state:

```text
BACKEND_DEPLOYED_FINAL_HANDOFF_READY_NO_GO_PENDING_APPROVALS_AND_SITE_EMBED
```

## Technical

- [x] Backend health verified
- [x] Claude diagnostics verified
- [x] Department routing verified
- [x] Finance no-contact verified
- [x] Sidebar widget verified
- [x] Final asset files prepared
- [x] Embed snippets prepared

## Content

- [x] Conservative decision CSV prepared
- [ ] Conservative decision CSV reviewed
- [ ] Human reviewer decisions approved
- [ ] Sensitive topics remain HANDOVER_ONLY or NEEDS_OFFICIAL_SOURCE unless approved
- [ ] Tuition/deadline/document/Medicine/International/visa rules approved
- [ ] Public answer policy approved

## Privacy

- [ ] Consent text approved
- [ ] Privacy Policy URL confirmed
- [ ] Data retention approved
- [ ] Delete/export process approved
- [ ] Lead creation consent approved

## Website

- [ ] Final asset URL confirmed
- [ ] Asset uploaded to Alte-controlled hosting
- [ ] Embed location confirmed
- [ ] Rollback plan confirmed
- [ ] Real-domain smoke plan confirmed

## Launch

- [ ] Real-domain smoke passed
- [ ] No CORS errors
- [ ] No frontend secrets
- [ ] No direct Anthropic calls
- [ ] No unexpected lead/task/customer creation
- [ ] Public launch approval granted
