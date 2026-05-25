# Netlify Test Site Package Manifest

Package path:

```text
dist/netlify_test_site_deploy.zip
```

## Included Files

ZIP root contains files directly, not under `test_site/`:

```text
index.html
join.html
alte-ai-chat-widget.js
alte-ai-chat-widget.html
_redirects
README_GEO.md
NETLIFY_DEPLOY_README_GEO.md
```

## SHA256

| File | SHA256 |
| --- | --- |
| `index.html` | `AEFA1E9905512D4695E05D1670DBD547BF9E7D2EC9BC1E1E3B346B5C4DA269DF` |
| `join.html` | `4EFE66F37F519FA332DC34C3F319ACE0E3F8379EA811F343F48298668C3545BC` |
| `alte-ai-chat-widget.js` | `167485C9EA5406D449DB189EA4EE3292CA5664D2BFDA76DE8E742D02EFCE0332` |
| `alte-ai-chat-widget.html` | `DC1E8DF7162028A464E98ECA513A20A5E0B4A81E8AB06203629DC3CFD708747A` |
| `_redirects` | `47B45ECD4353A1E0921A7AD8E8B9B4A7CC8F77D5760B0B61EC6DB0703AE1F465` |

## Safety Scan

- `api.anthropic.com` absent from deploy assets.
- `ANTHROPIC_API_KEY` absent from deploy assets.
- `sk-ant-` absent from deploy assets.
- Production backend URL present:
  `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- `/chat/session/start` present.
- `/chat/message` present.

## Deployment Status

- Netlify CLI deploy executed: NO
- Manual/Git redeploy required: YES
- Browser smoke passed: NO
