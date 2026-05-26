# Pro v2 Extraction Result

PRO_V2_EXTRACTION_STATUS=EXTRACTED

## Source

```text
docs/knowledge_evidence/uploaded_pro_v2_widget/Alte_AI_Chat_Pro_v2_standalone.html
```

## Script

```text
tools/extract_pro_v2_standalone.py
```

## Outputs

```text
docs/knowledge_evidence/uploaded_pro_v2_widget/extracted/extracted_template.html
docs/knowledge_evidence/uploaded_pro_v2_widget/extracted/extracted_app.js
docs/knowledge_evidence/uploaded_pro_v2_widget/extracted/extracted_styles.css
docs/knowledge_evidence/uploaded_pro_v2_widget/extracted/extracted_manifest_summary.json
docs/knowledge_evidence/uploaded_pro_v2_widget/extracted/extracted_text_index.txt
docs/knowledge_evidence/uploaded_pro_v2_widget/extracted/extracted_asset_list.json
```

## Summary

- Bundler manifest detected: YES
- Bundler template detected: YES
- Manifest assets: 32
- Decoded assets: 32
- Unsafe code execution: NO
- External network calls during extraction: NO

## Limitations

- Some extracted code is bundled/minified vendor code.
- Functional behavior is inferred from readable application assets and text search.
- Uploaded standalone remains reference/evidence only; production logic is rebuilt safely.
