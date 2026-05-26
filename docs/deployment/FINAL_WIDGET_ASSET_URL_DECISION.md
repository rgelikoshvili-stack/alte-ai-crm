# Final Widget Asset URL Decision

FINAL_WIDGET_ASSET_HOSTING_OPTION=ALTE_CONTROLLED_HOSTING
FINAL_WIDGET_ASSET_URL_STATUS=PENDING_UPLOAD_BY_ALTE_WEBSITE_TEAM
FINAL_WIDGET_ASSET_URL_PLACEHOLDER=https://alte.edu.ge/assets/alte-ai-chat-widget.js

## Option A — Alte-Controlled Hosting

Recommended for final production.

Example final assets:

- `https://alte.edu.ge/assets/alte-ai-chat-widget.js`
- approved CMS static asset path

Requires website admin/developer access.

Selected option: Alte-controlled hosting.

Reasons:

- Best ownership/control by Alte.
- Easiest rollback by website team.
- Avoids third-party raw hosting.
- Aligns with official site governance.

Requirements:

- Website developer uploads the final asset package.
- Replace the placeholder URL with the actual static asset URL if the website team uses a different path.
- Verify CORS and backend calls from the real domain.
- Run real-domain smoke after embed.

Actual upload/site modification was not executed in this phase.

## Phase 9L-M-N Final Handoff Update

- Final handoff package created: `docs/final_handoff/FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md`
- Widget asset manifest created: `docs/final_handoff/WIDGET_ASSET_MANIFEST.md`
- Asset upload still not executed.
- Final URL remains pending until the website team confirms the approved live asset URL.
- Public launch remains blocked.

## Phase 9L-P Asset Handoff Update

- Asset hosting status: `ALTE_CONTROLLED_HOSTING_SELECTED_PENDING_UPLOAD`
- Asset handoff status: `READY_PENDING_ALTE_UPLOAD_AND_EMBED`
- Final placeholder URL: `https://alte.edu.ge/assets/alte-ai-chat-widget.js`
- Actual upload: NOT EXECUTED
- Actual embed: NOT EXECUTED
- Use final handoff snippets from `docs/final_handoff/` only after official privacy URL and final execution confirmation are recorded.

## Phase 9J Gate

Final site embed is blocked until the Phase 9J approval record and GO/NO-GO checklist are complete.

Decision state:

```text
BACKEND_DEPLOYED_FINAL_PRE_EMBED_GATE_READY_NO_GO_PENDING_APPROVALS
```

## Option B — Google Cloud Storage/CDN Hosting

Requires additional approved GCP static hosting setup.

Not executed in this phase.

## Option C — GitHub/Static Raw Hosting

Not recommended for production.

## Recommendation

Use Alte-controlled hosting if the website team can upload static assets. If not possible, prepare a separate approved Cloud Storage hosting phase.
## Phase 9Q-9R Pro v2 Asset Update

- Final safe Pro v2 widget asset prepared locally.
- Current upload target remains pending Alte website team action.
- Netlify test package requires redeploy before browser retest.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_REBUILT_AND_FUNCTION_GAPS_AUDITED_PENDING_NETLIFY_REDEPLOY
```
