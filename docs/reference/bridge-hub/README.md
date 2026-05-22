# Bridge Hub Reference Copies

These files are exact reference copies from the Bridge Hub project. They are not imported by the Alte AI CRM runtime and should be used only as implementation guidance when building matching patterns for Alte.

Alte-specific mapping lives in:

- `docs/alte-bridge-reference-adaptation-plan.md`

Copied areas:

- Architecture and operational docs
- Security, secret hygiene, credential masking, tenant and RBAC contracts
- Correlation, audit, auth, RBAC, rate-limit, subscription and tenant middleware examples
- Response envelope and observability examples
- Dashboard/sidebar/static JavaScript UI references
- Contract test examples for security, response envelope, rate-limit, subscription and tenant/auth behavior

Do not edit these copied files directly when implementing Alte features. Create Alte-native code in the normal `backend/app` or future frontend folders and use these as reference only.
