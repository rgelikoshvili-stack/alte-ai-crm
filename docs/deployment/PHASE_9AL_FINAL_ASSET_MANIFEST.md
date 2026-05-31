# Phase 9AL Final Asset Manifest

PHASE_9AL_ASSET_MANIFEST_STATUS=READY_PENDING_APPROVAL_AND_UPLOAD

Public launch: NO-GO

## Proposed Production Asset URL

```text
FINAL_ASSET_URL_STATUS=PENDING_APPROVAL
PROPOSED_FINAL_ASSET_URL=https://alte.edu.ge/assets/alte-ai-chat-widget.js
ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL
```

The approved public embed snippet references only the loader script, but the loader requires the HTML shell and variants to be uploaded under the same asset base.

## Upload Package

Recommended production asset base:

```text
https://alte.edu.ge/assets/
```

Required files:

| Source file path | Proposed production path | Proposed production URL | Size bytes | SHA256 | Charset / note | Ready for upload | Approval required |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| `test_site/alte-ai-chat-widget.js` | `/assets/alte-ai-chat-widget.js` | `https://alte.edu.ge/assets/alte-ai-chat-widget.js` | 2878 | `E53C4C2D9789B4BCD780D9E86B1EAA9444B81904CC3617184CC7ABCFE316D2D4` | JavaScript; keep UTF-8; loader fetches HTML shell. | YES | YES |
| `test_site/alte-ai-chat-widget.html` | `/assets/alte-ai-chat-widget.html` | `https://alte.edu.ge/assets/alte-ai-chat-widget.html` | 13568 | `0036D835E485879D77A488F9C9C6B09D3C85910B5F121759D4F8360848E6739B` | HTML includes `<meta charset="utf-8"/>`; preserve UTF-8; default backend is Cloud Run. | YES | YES |
| `test_site/variants/pro-v2-chat.jsx` | `/assets/variants/pro-v2-chat.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-chat.jsx` | 51342 | `CC6973DEA991F08DAC4BE4D0914150985478CFA7F50347F7EE3E99011D729856` | JSX; preserve UTF-8 Georgian; includes responsive mobile guard. | YES | YES |
| `test_site/variants/pro-v2-modals.jsx` | `/assets/variants/pro-v2-modals.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-modals.jsx` | 13165 | `ADF6FA5330ED1A22397D3E93A18F7E84A34CA11D8EFC08D3C4D56DD0954BFEA2` | JSX; preserve UTF-8 Georgian; includes contact modal fields. | YES | YES |
| `test_site/variants/pro-v2-strings.jsx` | `/assets/variants/pro-v2-strings.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-strings.jsx` | 16497 | `283991B8E485040CB74936D7349CAD15981C13F7C1F037B3FB28434A64443F95` | JSX strings; preserve UTF-8 Georgian; no mojibake. | YES | YES |
| `test_site/variants/pro-v2-icons.jsx` | `/assets/variants/pro-v2-icons.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-icons.jsx` | 8532 | pending rehash at upload time | JSX icons. | YES | YES |
| `test_site/variants/pro-v2-page.jsx` | `/assets/variants/pro-v2-page.jsx` | `https://alte.edu.ge/assets/variants/pro-v2-page.jsx` | 14118 | pending rehash at upload time | JSX page wrapper. | YES | YES |
| `test_site/variants/tweaks-panel.jsx` | `/assets/variants/tweaks-panel.jsx` | `https://alte.edu.ge/assets/variants/tweaks-panel.jsx` | 23873 | pending rehash at upload time | JSX support panel. | YES | YES |

## Dist Widget Note

`dist/widget/alte-ai-chat-widget.js` and `dist/widget/alte-ai-chat-widget.html` exist, but the current verified Netlify/live package is sourced from `test_site/` and `test_site/variants/`.

For final upload, use the verified `test_site` package unless a separate rebuild produces matching hashes and passes visual QA.

## Upload Gate

```text
ASSET_READY_FOR_UPLOAD=YES
ASSET_UPLOAD_EXECUTED=NO
ASSET_UPLOAD_APPROVAL_REQUIRED=YES
REAL_ALTE_SITE_MODIFIED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```

Before upload:

- confirm official privacy URL;
- confirm contact-flow remains gated or approved;
- approve the final asset URL;
- upload the full package, not only the loader JS;
- verify served files preserve UTF-8 and current SHA256 hashes;
- run real-domain smoke after staged embed approval.
