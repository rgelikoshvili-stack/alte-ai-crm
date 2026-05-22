# Alte AI CRM - Bridge Hub Reference Adaptation Plan

Primary Alte source of truth:

- `Alte_AI_CRM_Master_Plan_v3_FINAL.docx`

Bridge Hub files copied under `docs/reference/bridge-hub/` are reference-only. They must not be imported directly into Alte runtime without Alte-specific review, naming, tests, and product fit.

## Adaptation Principles

1. Alte is a university CRM and admissions chatbot, not an accounting ERP.
2. Use Bridge Hub patterns only for architecture, safety, contracts, and UI structure.
3. Do not copy accounting, posting, ledger, tax, Balance.ge, 1C, RS.ge, payroll, inventory, or bank logic into Alte.
4. Keep AI as analysis-only. CRM services decide changes.
5. Keep API routes thin and move business rules into services.
6. Every important CRM event must remain audit logged.
7. Do not add external channels, real Claude calls, or frontend widget behavior before the approved phase.

## What To Reuse From Bridge Hub

| Bridge Hub area | Alte adaptation | Target phase |
| --- | --- | --- |
| `response_utils.py` | Standard API response envelope for future public/operator endpoints | Backend hardening |
| `correlation_middleware.py` | Request ID / correlation header for audit and support tracing | Auth/Security hardening |
| `audit_log_middleware.py` | HTTP-level audit pattern, adapted to Alte CRM entities | Auth/Security hardening |
| `auth_middleware.py` + `rbac_middleware.py` | Alte operator login, roles, and route permission guard | Phase 5C or security phase |
| `tenant_middleware.py` | Optional future multi-tenant support if Alte expands beyond one institution | Later SaaS readiness |
| `rate_limit_middleware.py` + rate limit services | Protect chat/session endpoints, login, and public widget API | Pre-widget hardening |
| `credential_response_sanitizer.py` | Prevent raw token/API key exposure in admin/status endpoints | Security hardening |
| `masking.py` | Mask phone, email, token-like values in logs/admin responses where needed | Security hardening |
| Secret hygiene tests | Alte no-secret contract tests | Immediate safe test addition |
| Response envelope tests | API consistency tests | Backend hardening |
| Dashboard/static UI examples | Visual/reference ideas only for CRM dashboard shell | Phase 5B frontend |
| Backup/PITR/staging docs | Deployment readiness checklist | Production readiness |

## What Not To Reuse

Do not copy or adapt these Bridge Hub domains into Alte:

- Accounting posting, journal, ledger, period lock, closing, trial balance
- Balance.ge, 1C, ORIS, FINA, RS.ge connector logic
- Tax, VAT, payroll, inventory, bank reconciliation
- Accounting-specific dashboards and reports
- Production migration gates for accounting ledger tables

## Current Alte Implementation Status

Completed:

- Phase 0: backend foundation
- Phase 1: CRM core
- Phase 2: website chat backend with mock AI
- Phase 3: mock lead qualification
- Phase 4: knowledge base and source governance
- Phase 5A: CRM operator dashboard API readiness
- Phase 5B: CRM operator frontend shell
- Phase 5C: optional auth, RBAC, correlation ID, token login, and response sanitizing helpers

Current gap before production:

- No public website widget UI yet
- No real Claude integration yet
- No external channels yet
- No production deployment hardening yet
- Auth/RBAC is present but still needs production operator seeding, password reset, session policy, and deployment validation

## Recommended Next Sequence

### Phase 5B - CRM Operator Frontend

Build the operator-facing UI against existing Phase 5A APIs:

- `/dashboard`
- `/inbox`
- `/conversations/:id`
- `/leads`
- `/leads/:id`
- `/pipeline`
- `/tasks`
- `/knowledge`
- `/settings`

Use Bridge Hub static/dashboard files only as layout references. Create Alte-native UI, copy no accounting labels.

Status: completed as a static dependency-free frontend shell.

### Phase 5C - Auth, RBAC, Audit, Security Hardening

Adapt Bridge Hub security patterns into Alte-native modules:

- JWT login/session endpoints
- Role permissions for admin, manager, admissions, international admissions, finance, student services, operator
- Correlation middleware
- Route-level RBAC
- Secret/credential response sanitizer
- Masking helper
- Rate limiting for public chat and login
- Security contract tests

Status: completed as optional `AUTH_REQUIRED` enforcement, token login, role checks, correlation IDs, sanitizing helpers, and tests.

### Phase 6 - Analytics and SLA

Build analytics from existing CRM data:

- Leads by program, channel, source domain, country, priority, status
- Handover count and response SLA
- Hot lead conversion
- Knowledge source coverage and no-source answer rate
- AI/mock intent accuracy review

### Later Controlled Phases

Only after frontend and security:

- Real Claude integration
- Website widget UI and proactive triggers
- WhatsApp/Messenger/Instagram/Email integrations
- WhatsApp history import
- Advanced bulk messaging and calendar workflows

## Implementation Rule For Future Tasks

For every future task:

1. Start from `Alte_AI_CRM_Master_Plan_v3_FINAL.docx`.
2. Check this adaptation plan for reusable Bridge Hub patterns.
3. Implement Alte-native files only.
4. Add tests in the same phase.
5. Run compile and pytest.
6. Do not proceed to the next phase without approval.
