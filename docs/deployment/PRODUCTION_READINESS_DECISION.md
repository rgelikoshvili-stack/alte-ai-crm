# Production Readiness Decision

## Go Only If

- [ ] GitHub remote exists.
- [ ] Release tag exists.
- [ ] Tests pass.
- [ ] Docker build passes.
- [ ] `startup_check` passes with production-like env.
- [ ] Google Cloud project selected.
- [ ] Billing understood.
- [ ] Cloud SQL cost accepted.
- [ ] Anthropic key created and stored in Secret Manager.
- [ ] CORS origins confirmed.
- [ ] Alte website admin/developer access confirmed.
- [ ] Rollback plan documented.
- [ ] Data privacy owner approves.

## No-Go If

- [ ] Real secrets are in Git, docs, chat, or screenshots.
- [ ] `.env` is tracked.
- [ ] Tests fail.
- [ ] Claude live test fails.
- [ ] Cloud SQL is not planned.
- [ ] CORS uses wildcard.
- [ ] No rollback plan exists.
