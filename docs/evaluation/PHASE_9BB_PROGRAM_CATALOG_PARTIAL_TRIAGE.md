# Phase 9BB Program Catalog Partial Triage

`PHASE_9BB_TRIAGE_STATUS=DOCUMENTED`

Decision state: `BACKEND_CODE_PROGRAM_CATALOG_PARTIAL_FIXES_READY_PENDING_DEPLOY`

Public launch remains NO-GO.

## Scope

- Baseline: Phase 9BA Program Catalog QA, `11 PASS / 9 PARTIAL / 0 FAIL`
- File: `01_program_catalog.pdf`
- Source: Higher Education Program Catalog
- Goal: convert the 9 PARTIAL rows to PASS without weakening source-backed, no-hallucination, or handover safety behavior.

## Triage Table

| Row | Question | Expected answer | Live answer summary | Expected route/source | Observed route/source | Root cause | Proposed fix | Regression risk | Test to add |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA-11 | პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია საბაკალავრო პროგრამა? | Bachelor programs are 240 ECTS, not 180. | Correct 240 ECTS fact, but from official academic rules. | `program_catalog_sources` / Higher Education Program Catalog | `official_academic_rules` | wrong_source, missing_source_metadata | Let explicit catalog scope override generic ECTS routing; add catalog deterministic 240 ECTS answer. | Could break generic Bachelor ECTS 9AS route if not scoped narrowly. | Catalog-scoped bachelor credits routes to catalog; generic Bachelor ECTS remains official rules. |
| QA-12 | პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია სამაგისტრო პროგრამა? | Master programs are 120 ECTS. | Correct 120 ECTS fact, but from official academic rules. | `program_catalog_sources` / Higher Education Program Catalog | `official_academic_rules` | wrong_source, missing_source_metadata | Let explicit catalog scope override generic ECTS routing; add catalog deterministic 120 ECTS answer. | Could break generic Master ECTS 9AS route if not scoped narrowly. | Catalog-scoped master credits routes to catalog; generic Master ECTS remains official rules. |
| QA-13 | რომელი პროგრამებია ინგლისურენოვანი პროგრამების კატალოგში? | English-language program versions are identified distinctly. | Generic catalog field summary, not the English-language program list. | `program_catalog_sources` / Higher Education Program Catalog | `program_catalog_sources` | incomplete_answer, answer_generation_gap | Add deterministic catalog answer listing Medicine, Computer Science, and AI/Data Analytics English-language versions. | Could over-answer general program-list prompts if marker is broad. | English-language catalog programs list exact English-language versions. |
| QA-14 | რა ენაზე ისწავლება სამართლის საბაკალავრო პროგრამა კატალოგის მიხედვით? | Law bachelor language is Georgian. | Generic university teaching-language answer from academic rules. | `program_catalog_sources` / Higher Education Program Catalog | `official_academic_rules` | wrong_source, answer_generation_gap | Let explicit catalog scope override generic teaching-language routing; add Law bachelor language answer. | Could break general teaching-language route if catalog scope is not required. | Catalog Law bachelor language routes to catalog and answers Georgian. |
| QA-15 | რა ენებზე არის ხელოვნური ინტელექტისა და მონაცემთა ანალიტიკის პროგრამა კატალოგში? | AI and Data Analytics has Georgian and English-language versions. | Generic catalog field summary. | `program_catalog_sources` / Higher Education Program Catalog | `program_catalog_sources` | incomplete_answer, answer_generation_gap | Add deterministic catalog answer for AI/Data Analytics Georgian and English-language versions. | Could affect other AI policy questions if marker is not catalog scoped. | AI/Data Analytics language question answers Georgian and English versions. |
| QA-16 | კრედიტები მაინტერესებს. | Ask which program/level the user means instead of guessing. | Retrieved unrelated admissions documents. | Clarification | `admissions_rules` | clarification_missing, wrong_source | Add punctuation-tolerant broad credit clarification. | Could block answerable ECTS questions if exact level is present. | Broad credit question asks clarification and performs no retrieval. |
| QA-17 | პროგრამები მაინტერესებს. | Ask clarification about bachelor/master/Medicine/international/program type. | Returned catalog summary instead of clarification. | Clarification | `program_catalog_sources` | clarification_missing, incomplete_answer | Normalize broad prompt punctuation and force clarification before retrieval. | Could block specific program-list prompts if matcher is too broad. | Broad program question with punctuation asks clarification; specific list prompts still answer. |
| QA-18 | კატალოგში პროგრამაზე ინფორმაცია მაინტერესებს. | Ask which program or which detail is needed. | Returned generic catalog summary. | Clarification | `program_catalog_sources` | clarification_missing, incomplete_answer | Add broad catalog-detail clarification for program/detail scope. | Could block exact catalog field-summary question if wording is too broad. | Broad catalog detail asks program/detail clarification; exact field-summary still answers. |
| QA-19 | პროგრამების კონსულტანტის ტელეფონის ნომერი მითხარი. | Do not invent a phone number; offer operator/official confirmation if needed. | No phone invented, but fallback text was provider-error styled and incomplete. | No approved source / operator fallback | `program_catalog_sources`, no source | incomplete_answer, answer_generation_gap | Treat consultant phone as unsupported high-risk; produce conservative no-source/operator fallback and no source retrieval. | Could over-route real contact requests if marker is too broad. | Consultant phone is unsupported/no-source, no phone hallucination, no lead/customer/task. |

## Root Cause Summary

- wrong_source: 4 direct rows, 6 total row notes in the Phase 9BA result
- incomplete_answer: 5 direct rows, 6 total row notes in the Phase 9BA result
- clarification_missing: 3 rows
- missing_source_metadata: catalog scope was not authoritative for ECTS/language wording
- answer_generation_gap: deterministic catalog answers were missing for specific language/list details

## Fix Summary

- Catalog-explicit ECTS and teaching-language prompts now prefer `program_catalog_sources`.
- Plain, non-catalog ECTS and teaching-language questions still use `official_academic_rules`.
- Broad credit/program/catalog-detail prompts now ask clarification and do not retrieve broadly.
- Catalog deterministic answers now cover:
  - bachelor credits: 240 ECTS
  - master credits: 120 ECTS
  - Law bachelor teaching language: Georgian
  - English-language catalog program versions
  - AI/Data Analytics Georgian and English-language versions
- Consultant phone requests are treated as unsupported/no approved source, with no phone hallucination.

## Safety

- Public launch remains NO-GO.
- Real site modified: NO.
- Assets uploaded or embedded: NO.
- Contact flow executed: NO.
- Lead/customer/task created: NO.
- DB schema/migration/seed/import: NO.
- Secret Manager/CORS/Bridge Hub changes: NO.
