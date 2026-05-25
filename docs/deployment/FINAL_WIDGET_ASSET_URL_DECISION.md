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

## Option B — Google Cloud Storage/CDN Hosting

Requires additional approved GCP static hosting setup.

Not executed in this phase.

## Option C — GitHub/Static Raw Hosting

Not recommended for production.

## Recommendation

Use Alte-controlled hosting if the website team can upload static assets. If not possible, prepare a separate approved Cloud Storage hosting phase.
