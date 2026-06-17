# Phase 9T Official Academic Rules Knowledge Import Result

PHASE_9T_OFFICIAL_ACADEMIC_RULES_KNOWLEDGE_STATUS=DEPLOYED_AND_PRODUCTION_SMOKE_PASSED

Decision state:

BACKEND_DEPLOYED_OFFICIAL_ACADEMIC_RULES_KB_ACTIVE_PENDING_BROWSER_QA_RETEST

## Imported Source Files

- `bakalavriatis_debuleba_2.pdf`
- `sastsavlo_procesis_maregulirebeli_wesi.pdf`
- `magistraturis_debuleba.pdf`
- `academic_calendar_geo_2025_2026.pdf`
- `academic_calendar_eng_2025_2026.pdf`

## Status

- Extraction status: DONE
- Structured KB status: DONE, `backend/app/data/knowledge/official_academic_rules_2025_2026.json`
- Full source chunks retained: DONE, `backend/app/data/knowledge/official_academic_rules_full_chunks.json`
- Calendar JSON status: DONE, `backend/app/data/knowledge/academic_calendar_2025_2026_structured.json`
- QA dataset status: DONE, `backend/app/data/evaluation/alte_official_academic_rules_30_qa.json`
- QA evaluation score: 30/30 PASS
- Chatbot integration status: deployed code prioritizes official academic rules retrieval for academic/calendar/status/ECTS/GPA/exam/mobility questions.

## Answerable

Bachelor/master admission, ECTS, teaching language, academic calendar 2025-2026, registration dates, exams/retakes, student status, mobility, credit recognition, GPA, FX/F, final exam admission, foreign education recognition, and program approval are answerable only when supported by the official files.

## Needs Additional Official Source

Unsupported tuition/payment specifics, unsupported thesis details, career/alumni service functions, and Teaching-Learning Excellence Center functions must not be invented.

## Safety

- Production DB changed in this deploy: NO
- New production DB import approval needed: NO for current approved KB records; YES before applying any future new local artifact rows to production
- Deploy run: YES
- Migration run: NO
- Seed run: NO
- Real Alte site modified: NO
- Contact details sent/requested: NO
- Lead/task/customer intentionally created: NO
- Public launch: NO-GO
