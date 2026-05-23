# Cloud SQL Tier Decision

## A. Purpose

Production must use PostgreSQL, not SQLite. SQLite remains suitable only for local demo and tests.

## B. Recommended Starting Option

For MVP / pilot:

- Database engine: PostgreSQL 16
- Region: `europe-west1`
- Instance name: `alte-ai-crm-db`
- Database: `alte_ai_crm`
- User: `alte_app`
- Tier: small/low-cost pilot tier, selected after review in Google Cloud Console

Do not rely on this document for exact pricing. Actual monthly price must be checked in Google Cloud Pricing Calculator or Cloud SQL Console before approval.

## C. Options

| Option | Recommended use | Pros | Cons | Cost risk | Decision |
| --- | --- | --- | --- | --- | --- |
| Smallest dev/test tier | Development validation only | Lowest cost, quick validation | Not production-grade, limited performance | Low | Not recommended for production |
| Small production pilot tier | First controlled production pilot | Reasonable balance for MVP traffic | May need scaling after adoption | Medium | Preferred pending cost approval |
| Larger production tier later | Higher traffic and SLA needs | More capacity and reliability headroom | Higher recurring cost | Higher | Future option |

## D. Cost Approval

- [ ] Cloud SQL monthly cost reviewed.
- [ ] Backup/storage cost reviewed.
- [ ] Region confirmed.
- [ ] Billing owner approved.
- [ ] Decision owner recorded.
- [ ] Approval date recorded.

## E. Current Recommendation

Decision status: `PENDING_APPROVAL`

Do not create the Cloud SQL instance until cost/tier approval is recorded.
