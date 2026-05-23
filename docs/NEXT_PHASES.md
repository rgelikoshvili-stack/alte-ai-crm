# Next Phases

## Phase 8B: Real Claude Live Validation

- Requires a real Anthropic API key configured locally.
- Run `GET /diagnostics/ai`.
- Run `python -m app.scripts.ai_direct_dry_run`.
- Run `python -m app.scripts.claude_live_smoke`.
- Verify `ai_interactions.provider = claude`.
- Confirm customer, lead, task, conversation, and message side effects are still created by CRM services, not by Claude directly.

## Phase 8C: Production Deployment Preparation

Status: prepared in repository; no real Google Cloud deployment yet.

- Dockerfile review.
- Cloud Run configuration.
- Cloud SQL configuration.
- Secret Manager mapping.
- Production CORS.
- Health and diagnostics checks.
- No real deployment until explicit approval.

## Phase 8D: Actual Cloud Run Deployment

- Create/confirm Google Cloud project resources.
- Build and push backend image.
- Configure Cloud Run, Cloud SQL, and Secret Manager.
- Run migrations and approved seed.
- Verify production health and diagnostics.

## Phase 8E: Staging Website Widget Embed

- Backend public URL.
- Widget public URL.
- CORS for `https://alte.edu.ge` and `https://join.alte.edu.ge`.
- Script snippet.
- Privacy/consent text review.
- Staging test page.

## Phase 9: Omnichannel Planning

- Meta Developers account.
- WhatsApp Business API.
- Messenger.
- Instagram.
- Email.
- SMS.

No omnichannel implementation before the website chat flow is stable.

## Phase 10: Advanced CRM

- Agent module.
- Bulk messaging approval.
- Calendar integration.
- SLA automation.
- Advanced analytics.
