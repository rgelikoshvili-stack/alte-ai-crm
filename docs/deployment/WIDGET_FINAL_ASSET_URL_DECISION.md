# Widget Final Asset URL Decision

## Current Widget Asset

```text
widget/alte-chat-widget.v0.8.js
```

## Allowed Hosting Options

1. Alte website/CMS static file.
2. Google Cloud Storage static file.
3. Other approved static host.

## Recommended First Option

Alte website/CMS static asset hosting, if developer access exists.

This keeps rollback simple: the Alte developer can remove the script tags or replace the uploaded static file.

## Required Final Value

```text
FINAL_WIDGET_ASSET_URL=PENDING
```

## Examples

```text
https://alte.edu.ge/path/to/alte-chat-widget.v0.8.js
https://join.alte.edu.ge/path/to/alte-chat-widget.v0.8.js
https://storage.googleapis.com/APPROVED_BUCKET/alte-chat-widget.v0.8.js
```

Do not create a bucket or upload the asset in this phase.
