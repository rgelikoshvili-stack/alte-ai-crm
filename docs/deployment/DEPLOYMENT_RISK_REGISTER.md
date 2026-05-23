# Deployment Risk Register

| Risk | Impact | Mitigation | Owner / Check |
| --- | --- | --- | --- |
| Secrets leakage | API or database compromise | Use Secret Manager, never commit `.env`, scan docs before commit | Engineering |
| Wrong project or region | Deploys to wrong account or adds cost | Confirm `PROJECT_ID` and `REGION` in preflight | Operator |
| Cloud SQL cost | Unexpected billing | Review instance tier, storage, backup settings before creation | Project owner |
| Database migration failure | App unavailable or inconsistent schema | Run migrations against staging/disposable DB first | Engineering |
| CORS misconfiguration | Widget cannot call backend or accepts unsafe origins | Use exact origins, no wildcard in production | Engineering |
| Unauthenticated public backend endpoints | Data exposure | Keep `AUTH_REQUIRED=true`, review public endpoints | Security / Engineering |
| AI cost runaway | Unexpected Anthropic spend | Add monitoring, rate limits and quotas before production launch | Project owner |
| Claude invalid JSON fallback | Poor chat experience | Keep parser validation and safe handover fallback | Engineering |
| Log exposure | Sensitive data in logs | Do not log keys, full DB URLs, or raw secrets | Engineering |
| Stale knowledge base | Wrong admissions answers | Use review queues, stale flags, approved-only retrieval | Admissions owner |
| Rollback complexity | Longer outage | Keep previous Cloud Run revision and image tag | Engineering |
