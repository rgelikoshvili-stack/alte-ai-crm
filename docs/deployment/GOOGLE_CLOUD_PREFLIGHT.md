# Google Cloud Preflight

## A. Account / Project

- [ ] Google Cloud account exists.
- [ ] Billing is enabled.
- [ ] Correct `PROJECT_ID` is selected.
- [ ] `gcloud` CLI is installed.
- [ ] `gcloud auth login` completed.
- [ ] `gcloud config set project PROJECT_ID` completed.

## B. APIs

Confirm these APIs are enabled:

- [ ] Cloud Run API
- [ ] Artifact Registry API
- [ ] Cloud SQL Admin API
- [ ] Secret Manager API
- [ ] Cloud Build API
- [ ] IAM API

## C. Region

- [ ] Choose `europe-west1` or `europe-west3`.
- [ ] Use the same region for Cloud Run and Artifact Registry.
- [ ] Cloud SQL region is close/same where possible.

## D. Database

- [ ] Cloud SQL PostgreSQL instance planned.
- [ ] Database name planned.
- [ ] App user planned.
- [ ] Password generated locally, not committed.
- [ ] Migration strategy planned.

## E. Secrets

- [ ] `DATABASE_URL` secret planned.
- [ ] `JWT_SECRET` planned.
- [ ] `ANTHROPIC_API_KEY` planned.
- [ ] No secrets in docs, Git, chat, or screenshots.

## F. CORS

- [ ] `https://alte.edu.ge` confirmed.
- [ ] `https://join.alte.edu.ge` confirmed if needed.
- [ ] No wildcard production CORS.

## G. Release

- [ ] Tests pass.
- [ ] Release checkpoint passes.
- [ ] Docker build passes.
- [ ] `startup_check` passes.
- [ ] Rollback plan exists.
