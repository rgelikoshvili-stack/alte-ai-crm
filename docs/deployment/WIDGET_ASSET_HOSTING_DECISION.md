# Widget Asset Hosting Decision

## Purpose

Choose where to host the reviewed Safe Pro widget asset for the production website embed.

```text
WIDGET_ASSET_HOSTING_STATUS=PENDING_FINAL_URL
```

## Option A - Host Widget File On Alte Website/CDN

Best for production.

Requires Alte website developer/admin access.

Final URL example:

```text
https://alte.edu.ge/path/to/alte-university-ai-chatbot-safe-pro.html
```

or, if the widget is converted to a JS asset later:

```text
https://alte.edu.ge/path/to/alte-university-ai-chatbot-safe-pro.js
```

Pros:

- Alte controls the asset lifecycle.
- Rollback is straightforward through the website/CMS.
- No new Google Cloud static hosting resource is required.

Cons:

- Requires website admin/developer access.
- Cache invalidation depends on Alte website/CDN tooling.

Decision: recommended for real site launch if available.

## Option B - Host Widget Static Asset On Approved Cloud Storage/CDN Later

Requires a separately approved GCP static hosting setup.

Pros:

- Versioned static assets can be managed independently from the website CMS.
- CDN can be added later if approved.

Cons:

- Requires new cloud resource configuration.
- Requires CORS/cache/IAM/public asset decisions.
- Not approved in this phase.

Decision: later option only; do not create Cloud Storage/CDN in Phase 9C.

## Option C - Temporary Standalone Page

Good for demo/review.

Current preview:

```text
widget/standalone-safe-pro-demo.html
```

Cons:

- Not a final public embed path.
- Local browser requests may be blocked by production CORS.
- Does not replace real-domain browser smoke.

Decision: use only for UI preview.

## Recommendation

For real site launch, use Alte-controlled hosting if possible.

If Alte-controlled hosting is not possible, prepare approved static asset hosting in a later phase. Do not perform the actual website embed until final asset URL, privacy/data approval, official content approval, website deployment confirmation, and real-domain smoke approval are complete.
