# Cloud SQL Cost Approval Form

## A. Current Planned Database

- `PROJECT_ID=project-1e145fd0-c30e-4aac-a34`
- `REGION=europe-west1`
- `INSTANCE=alte-ai-crm-db`
- `DATABASE=alte_ai_crm`
- `USER=alte_app`
- `ENGINE=PostgreSQL 16`

## B. Tier Decision Fields

- Selected tier: Smallest acceptable low-cost Cloud SQL PostgreSQL tier for pilot/MVP. Suggested placeholder: `db-f1-micro` or the current lowest available shared-core PostgreSQL tier in Google Cloud Console.
- Storage size: Minimum practical starting storage for pilot. Suggested: 10 GB SSD or the minimum allowed by Google Cloud SQL.
- Backup enabled: Yes for pilot, but confirm cost.
- High availability: No for pilot/MVP. Review HA later for production-critical launch.
- Estimated monthly cost: `PENDING_USER_REVIEW_IN_GOOGLE_CLOUD_PRICING_CALCULATOR`
- Billing owner: `PENDING_USER`
- Approval date: `PENDING`
- Approved by: `PENDING`

## C. Recommendation

For pilot/MVP, choose the smallest acceptable low-cost Cloud SQL PostgreSQL tier.

Do not use this document as a price source. The user must verify the final price in Google Cloud Console or Google Cloud Pricing Calculator before approval.

## D. Current Status

`PENDING_USER_APPROVAL`

Do not create the Cloud SQL instance until this form is approved.

## E. Approval Notes

- This is not final approval.
- Actual pricing must be checked in Google Cloud Console or Google Cloud Pricing Calculator.
- Cloud SQL can create ongoing monthly cost.
- User/billing owner must explicitly approve before Phase 8F-Execution.
- Production-critical use should later review HA, backups, storage growth, and monitoring.
