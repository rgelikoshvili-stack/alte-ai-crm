# Secret Manager Approval Gate

Initial status: `PENDING_APPROVAL`

Secret Manager creation remains blocked until the user explicitly says:

`Approve Secret Manager creation`

## Before Creating Secrets

- [x] Cloud SQL pilot tier approved.
- [ ] Cloud SQL instance creation approved or planned for the execution phase.
- [ ] DB password generated locally.
- [ ] JWT secret generated locally.
- [ ] Anthropic key created or rotated and not exposed.
- [ ] `DATABASE_URL` can be constructed from Cloud SQL connection details.
- [ ] User understands secrets must not be printed, pasted into chat, or committed.
- [ ] `gcloud` active project confirmed.
- [ ] Billing/project confirmed.

## Approval Fields

- Secret creation approved: `YES/NO`
- Approved by: `PENDING`
- Approval date: `PENDING`
- Notes: `PENDING`

## Decision

Do not create Secret Manager secrets until approval is explicit and current.
