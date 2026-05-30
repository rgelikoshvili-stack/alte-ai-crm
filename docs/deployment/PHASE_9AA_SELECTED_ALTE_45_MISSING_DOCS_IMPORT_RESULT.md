# Phase 9AA Selected Alte 45 Missing Docs Import Result

PHASE_9AA_SELECTED_ALTE_45_MISSING_DOCS_IMPORT_STATUS=PRODUCTION_KB_IMPORTED_ROUTING_FIX_PENDING_DEPLOY_APPROVAL

## Scope

Imported the selected missing official source documents from the local Alte documentation package into the production Knowledge Base.

Source package:

```text
C:\Users\Acer\Documents\Codex\2026-05-19\unexpected-status-403-forbidden-detail-code\alte_documents
```

The import used the existing pre-extracted `alte_documents_chunks.jsonl` artifact. No PDF OCR was run.

## Production Import Summary

- Selected missing documents requested for this step: `32`
- Local documents found/processable: `32`
- Local documents not processed: `0`
- Production sources created: `32`
- Production snippets created: `46`
- Production selected source count: `32`
- Production selected snippet count: `46`
- Production selected approved snippet count: `46`
- Owner: `phase_9aa_selected_alte_45_missing_docs`
- Source domain for retrieval: `alte.edu.ge`
- Existing 9 official sources replaced: NO

## Imported Documents

| # | Requested title | Source filename | Chunks |
| ---: | --- | --- | ---: |
| 10 | ინდივიდუალური სასწავლო გეგმის შემუშავების მეთოდოლოგია | `063_RRPR4gLRZ4.pdf` | 2 |
| 11 | სტუდენტთა ინდივიდუალური სასწავლო გეგმის შემუშავების მეთოდოლოგია | `098_q1YQAQhajF.pdf` | 2 |
| 12 | ელექტრონული სწავლების ადმინისტრირების წესი | `058_lCBeyC0gSb.pdf` | 1 |
| 14 | Examination Regulations | `076_ExaminationRegulations.pdf` | 2 |
| 15 | პლაგიატი, მისი ფორმები, პრევენციის საშუალებები და სანქციები | `065_QlAZe56OHS.pdf` | 2 |
| 16 | ეთიკის კოდექსი | `074_vQyJ19AYWH.pdf` | 3 |
| 18 | სტუდენტთა უფლებებისა და კანონიერი ინტერესების დაცვის მექანიზმები | `095_LHzTgcc2Rc.pdf` | 2 |
| 19 | სტუდენტური ომბუდსმენის დებულება | `080_73ut09R5Pa.pdf` | 1 |
| 20 | ომბუდსმენი | `030_F9yutbkbxH.pdf` | 2 |
| 21 | თვითმმართველობის დებულება | `082_6tvL7mhYc7.pdf` | 1 |
| 22 | სტუდენტების არჩევის წესი | `007_yfZG9xzy2l.pdf` | 1 |
| 23 | სკოლის საბჭოებში მონაწილეობის წესი | `008_lg07GuicOD.pdf` | 2 |
| 24 | ბიბლიოთეკის დებულება | `068_TRphmMn9Xg.pdf` | 1 |
| 25 | ბიბლიოთეკით სარგებლობის წესები | `086_e1Y852YO2T.pdf` | 1 |
| 26 | ბიბლიოთეკის წესები DOCX | `087_uLr992q8e0.docx` | 1 |
| 27 | კარიერული განვითარებისა და კურსდამთავრებულთა მომსახურების წესი | `092_UM4rez8Sgq.pdf` | 1 |
| 28 | Rules of Career Development of Students and Services of Alumni | `093_jHEsy8iDO8.pdf` | 2 |
| 29 | სპეციალური საჭიროების მქონე პირთა მომსახურების წესი | `088_Wmnayjohgb.pdf` | 1 |
| 30 | სსმ პირთა მომსახურების წესი | `089_fI35AQtlhc.pdf` | 2 |
| 32 | დაფინანსების წესი | `114_D87lOzA1tj.pdf` | 1 |
| 33 | აკადემიური მიღწევებისთვის დეკანის გრანტის დანიშვნის წესი | `096_au4xEQ3RLj.pdf` | 1 |
| 34 | Dean's List Award Terms and Conditions | `097_jTV38r4nF8.pdf` | 1 |
| 36 | გენერაციული ხელოვნური ინტელექტის გამოყენების პოლიტიკა | `131_yM6EMjQz9I.pdf` | 2 |
| 37 | Generative Artificial Intelligence Usage Policy | `132_UPP7tK2imL.pdf` | 2 |
| 38 | ინფორმაციული ტექნოლოგიების მართვის პოლიტიკა და ინფრასტრუქტურა | `106_3cvbwTPgx5.pdf` | 1 |
| 39 | IRO Policy | `115_C8hEJJ7ftX.pdf` | 1 |
| 40 | IRO Policy Annex | `116_iz3giyVdLF.pdf` | 2 |
| 41 | მდგრადი განვითარების სტრატეგია | `119_Gjvu8QaVrf.pdf` | 1 |
| 42 | Alte Sustainability Strategy | `120_kyxH61FeCu.pdf` | 1 |
| 43 | Sustainability Report 2024 | `121_KBTF24F2Dw.pdf` | 1 |
| 44 | EDI Policy | `122_vj966IoEsX.pdf` | 1 |
| 45 | კვლევითი კომპონენტის დაგეგმვის/განხილვის/შეფასების მექანიზმები | `112_9NYXk63jy8.pdf` | 1 |

## Coverage

Before this import, exact production coverage for the selected 45-document list was documented as `9/45`, with several additional topics only partially covered by broader documents.

After this import:

- Exact added coverage: `32` documents
- Exact covered documents: `41/45`
- Remaining items are partially covered by existing broader sources or same-source equivalents and should be separately normalized if exact one-row-per-title coverage is required:
  - `Catalogue of Educational Programmes`
  - `Regulations Governing the Educational Process`
  - `გამოცდების ჩატარების დებულება`
  - `სტუდენტთა მომსახურების წესი`

## Production Chat Smoke

Production smoke for a newly imported AI policy question:

- `/chat/session/start`: `200`
- `/chat/message`: `200`
- Answer present: YES
- Lead created: NO
- Task created: NO
- Observed source status before deploy: `not_required`

This showed that production needs the prepared routing fix to force Knowledge Base retrieval for the newly imported official-policy/library/career/ombudsman/AI-policy topics. The routing fix is implemented in code and awaits deploy approval.

## Safety

- Production DB modified: YES, Knowledge Base source/snippet records only
- Existing 9 official sources changed/replaced: NO
- Migration run: NO
- Seed run: NO
- Schema changed: NO
- Secret Manager changed: NO
- Cloud Run deployed: NO
- CORS changed: NO
- Real `alte.edu.ge` or `join.alte.edu.ge` changed: NO
- Public chatbot UI changed: NO
- Lead/task/customer created: NO
- Credentials, tokens, hashes, or connection-string values printed: NO
- Public launch: NO-GO

## Decision State

```text
BACKEND_PRODUCTION_KB_SELECTED_45_DOCS_IMPORTED_ROUTING_FIX_READY_PENDING_DEPLOY_APPROVAL
```
