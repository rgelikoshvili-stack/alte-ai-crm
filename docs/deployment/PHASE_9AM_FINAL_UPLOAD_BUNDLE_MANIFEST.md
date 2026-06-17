# Phase 9AM Final Upload Bundle Manifest

PHASE_9AM_FINAL_UPLOAD_BUNDLE_MANIFEST_STATUS=READY_PENDING_UPLOAD_APPROVAL

Public launch: NO-GO

## Bundle

Bundle directory:

```text
dist/final_alte_widget_upload/
```

ZIP archive:

```text
dist/final_alte_widget_upload.zip
```

ZIP SHA256:

```text
EEE750AA2E960BECC71E840C75C57D58C4E02CECAE63AAD8C72769A87F32FE2A
```

ZIP root contains:

```text
alte-ai-chat-widget.js
alte-ai-chat-widget.html
variants/
```

## File Manifest

| ZIP path | Source path | Target production path | Proposed production URL | Size bytes | SHA256 | UTF-8 / charset note | Upload required | Approval required |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `alte-ai-chat-widget.js` | `test_site/alte-ai-chat-widget.js` | `/assets/alte-ai-chat-widget.js` | `https://alte.edu.ge/assets/alte-ai-chat-widget.js` | 2878 | `E53C4C2D9789B4BCD780D9E86B1EAA9444B81904CC3617184CC7ABCFE316D2D4` | JavaScript loader; preserve UTF-8. | YES | YES |
| `alte-ai-chat-widget.html` | `test_site/alte-ai-chat-widget.html` | `/assets/alte-ai-chat-widget.html` | `https://alte.edu.ge/assets/alte-ai-chat-widget.html` | 13568 | `0036D835E485879D77A488F9C9C6B09D3C85910B5F121759D4F8360848E6739B` | HTML shell includes `<meta charset="utf-8"/>`; default backend is Cloud Run. | YES | YES |
| `variants/pro-v2-chat.jsx` | `test_site/variants/pro-v2-chat.jsx` | `/assets/variants/pro-v2-chat.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-chat.jsx` | 51342 | `CC6973DEA991F08DAC4BE4D0914150985478CFA7F50347F7EE3E99011D729856` | JSX; preserve UTF-8 Georgian; includes mobile responsive behavior. | YES | YES |
| `variants/pro-v2-icons.jsx` | `test_site/variants/pro-v2-icons.jsx` | `/assets/variants/pro-v2-icons.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-icons.jsx` | 8532 | `1CE844A74E9A6058A142D8D5AAAC36F16C76C615BC9B6E42689B88B0A845EE30` | JSX icons; preserve UTF-8. | YES | YES |
| `variants/pro-v2-modals.jsx` | `test_site/variants/pro-v2-modals.jsx` | `/assets/variants/pro-v2-modals.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-modals.jsx` | 13165 | `ADF6FA5330ED1A22397D3E93A18F7E84A34CA11D8EFC08D3C4D56DD0954BFEA2` | JSX modals; includes contact message textarea; preserve UTF-8 Georgian. | YES | YES |
| `variants/pro-v2-page.jsx` | `test_site/variants/pro-v2-page.jsx` | `/assets/variants/pro-v2-page.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-page.jsx` | 14118 | `BB9F1A815954919A237C9F6AF78CBF7A09896F6332C63282C936B37A38433422` | JSX page wrapper; preserve UTF-8. | YES | YES |
| `variants/pro-v2-strings.jsx` | `test_site/variants/pro-v2-strings.jsx` | `/assets/variants/pro-v2-strings.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-strings.jsx` | 16497 | `283991B8E485040CB74936D7349CAD15981C13F7C1F037B3FB28434A64443F95` | JSX strings; preserve UTF-8 Georgian; no mojibake. | YES | YES |
| `variants/tweaks-panel.jsx` | `test_site/variants/tweaks-panel.jsx` | `/assets/variants/tweaks-panel.jsx` | `https://alte.edu.ge/assets/variants/tweaks-panel.jsx` | 23873 | `82C38755258809F6ACF49C0B6B2ECC8DDCDCD97FA453E3530F546B6626ACB77B` | JSX support panel; preserve UTF-8. | YES | YES |

## Consistency Checks

```text
ZIP_ROOT_STRUCTURE=PASSED
LOADER_FETCHES_HTML_RELATIVE_TO_ASSET_BASE=PASSED
HTML_LOADS_VARIANTS_RELATIVE_TO_HTML=PASSED
NETLIFY_ONLY_REFERENCES=NONE_FOUND
LOCAL_ONLY_PATHS=NONE_FOUND
DIRECT_ANTHROPIC_BROWSER_CALL=NONE_FOUND
FRONTEND_API_KEYS=NONE_FOUND
DEFAULT_BACKEND=https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Upload Gate

```text
ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL
ASSET_UPLOAD_REQUIRED=YES
ASSET_UPLOAD_APPROVAL_REQUIRED=YES
REAL_ALTE_SITE_MODIFIED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```

Do not upload these files until final asset upload approval is explicitly provided.
