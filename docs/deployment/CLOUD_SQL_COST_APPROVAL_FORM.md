# Cloud SQL Cost Approval Form

## A. Current Planned Database

- `PROJECT_ID=project-1e145fd0-c30e-4aac-a34`
- `REGION=europe-west1`
- `INSTANCE=alte-ai-crm-db`
- `DATABASE=alte_ai_crm`
- `USER=alte_app`
- `ENGINE=PostgreSQL 16`

## B. Tier Decision Fields

- Selected tier: Low-cost pilot production tier - smallest acceptable Cloud SQL PostgreSQL shared-core or equivalent pilot production tier available in Google Cloud Console for PostgreSQL 16.
- Storage size: Minimum practical starting storage for pilot. Suggested: 10 GB SSD or the minimum allowed by Google Cloud SQL.
- Backup enabled: Yes for pilot, but confirm cost.
- High availability: No for pilot/MVP. Review HA later for production-critical launch.
- Estimated monthly cost: `PENDING_USER_REVIEW_IN_GOOGLE_CLOUD_PRICING_CALCULATOR`
- Billing owner: `PENDING_USER`
- Approval date: `PENDING`
- Approved by: `PENDING`

## C. Recommendation

For pilot/MVP, choose the low-cost pilot production tier.

Do not use this document as a price source. The user must verify the final price in Google Cloud Console or Google Cloud Pricing Calculator before approval.

## D. Cloud SQL Pilot Tier Comparison

| Option | Use case | Pros | Cons | Cost risk | Decision |
| --- | --- | --- | --- | --- | --- |
| Option A - Lowest dev/test tier | Temporary testing, internal demo | Lowest cost, easy to start | Not recommended for public pilot, limited performance, may become unstable with real traffic | lowest | Not recommended for public pilot. Acceptable only for temporary internal testing. |
| Option B - Low-cost pilot production tier | First public pilot, low traffic website chatbot, small CRM operator team | Best balance for MVP/pilot, low-to-medium cost risk, can upgrade later, suitable starting point before omnichannel traffic | Not high availability, must monitor CPU/storage/connections/slow queries, may need upgrade after WhatsApp/Messenger/Instagram are added | low-to-medium | Recommended for Alte AI CRM pilot. |
| Option C - Higher production tier | Larger traffic, more operators, omnichannel traffic, production-critical launch | Better performance, safer for growth, more room for analytics and operator usage | Higher monthly cost, may be unnecessary for first pilot | medium-to-high | Later upgrade option, not needed for first pilot unless expected traffic requires it. |

## E. Upgrade Triggers

- CPU consistently high.
- Database connections near limit.
- Slow dashboard or inbox queries.
- Increased public traffic.
- WhatsApp/Messenger/Instagram integrations added.
- More operators using CRM daily.
- Storage growth beyond estimate.
- Analytics/reporting queries become slow.

## F. Upgrade Path

- Increase Cloud SQL tier.
- Increase storage.
- Enable or consider high availability.
- Add monitoring alerts.
- Optimize indexes and queries before a large cost increase.
- Review connection pooling if needed.

## G. Current Status

`PENDING_USER_APPROVAL`

Do not create the Cloud SQL instance until this form is approved.

## H. Approval Notes

- This is not final approval.
- This is a technical recommendation only, not financial approval.
- Actual pricing must be checked in Google Cloud Console or Google Cloud Pricing Calculator.
- Cloud SQL can create ongoing monthly cost.
- User/billing owner must explicitly approve before Phase 8F-Execution.
- Production-critical use should later review HA, backups, storage growth, and monitoring.
