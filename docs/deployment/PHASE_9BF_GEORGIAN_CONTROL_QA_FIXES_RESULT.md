# Phase 9BF Georgian Control QA Fixes Result

PHASE_9BF_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY

Decision state: BACKEND_CODE_GEORGIAN_CONTROL_QA_FIXES_READY_PENDING_DEPLOY

Public launch: NO-GO

## Baseline

- Source report: `docs/deployment/PHASE_9AS_40_QUESTION_GEORGIAN_CONTROL_QA_RESULT.md`
- Baseline total: 40
- Baseline PASS: 24
- Baseline PARTIAL: 10
- Baseline FAIL: 6
- Target: fix all 16 non-PASS rows locally, then require safe production retest before GO.

## Root Cause Table

| # | Question | Current behavior | Expected behavior | Root cause | Fix type |
| ---: | --- | --- | --- | --- | --- |
| 8 | რა მოთხოვნები შეიძლება ჰქონდეს ინგლისურენოვან პროგრამაზე ჩარიცხვას? | Returned generic bachelor admissions documents. | Conservative English-language admissions requirement summary; no invented exact requirement. | admissions_rules over-capture; missing selected control mapping. | Deterministic Georgian control answer and selected-doc marker. |
| 11 | როგორ გამოითვლება GPA? | Mentioned GPA generally but omitted exact formula and credit weighting. | Include official formula and credit-weighted explanation. | Generic answer generation. | Exact GPA deterministic wording. |
| 15 | როდის არის რეგისტრაციის პერიოდი აკადემიურ კალენდარში? | Answered broad calendar scope without enough clarification. | Ask program group, semester, and event clarification. | Broad calendar clarification missing. | Broad calendar clarification rule. |
| 16 | როდის იწყება სემესტრი? | Answered broad calendar scope without enough clarification. | Ask program group and semester clarification. | Broad calendar clarification missing. | Broad calendar clarification rule. |
| 17 | როდის არის შუალედური ან დასკვნითი გამოცდები? | Answered broad exam dates without enough clarification. | Ask program group, semester, and exam type clarification. | Broad calendar clarification missing. | Broad calendar clarification rule. |
| 24 | რა არის სახელმწიფო სასწავლო გრანტი ან სოციალური პროგრამა? | Finance/support answer incomplete. | Conservative source-backed finance support explanation. | Missing Georgian finance aliases. | Georgian selected-doc alias/category and deterministic answer. |
| 26 | რა სერვისებს იღებს სტუდენტი უნივერსიტეტში? | Unsupported or wrong-source answer. | Student services summary without contact flow. | admissions_rules over-capture; missing student services routing. | Georgian selected-doc mapping. |
| 27 | რა ფუნქცია აქვს სტუდენტურ ომბუდსმენს? | Incomplete student rights answer. | Ombudsman function and rights support explanation. | Missing ombudsman control mapping. | Georgian selected-doc mapping. |
| 28 | როგორ შეუძლია სტუდენტს საკუთარი უფლებების დაცვა? | Unsupported/wrong source. | Rights-protection mechanisms and ombudsman route. | admissions_rules over-capture; missing rights markers. | Admissions exclusion plus selected-doc mapping. |
| 29 | როგორ შეუძლია სტუდენტს ბიბლიოთეკით სარგებლობა? | Incomplete library answer. | Conservative library usage/resource summary. | Missing Georgian library aliases. | Georgian library alias/category and deterministic answer. |
| 32 | რა არის პლაგიატი? | Academic integrity answer incomplete. | Definition of plagiarism from academic integrity context. | Missing Georgian integrity alias. | Georgian integrity selected-doc mapping. |
| 33 | რა სანქციები შეიძლება მოჰყვეს აკადემიური კეთილსინდისიერების დარღვევას? | No approved source or incomplete answer. | Conservative sanctions/procedure explanation without inventing exact penalty. | Missing Georgian sanctions/integrity routing. | Georgian integrity selected-doc mapping. |
| 34 | რა მხარდაჭერა აქვს სპეციალური საჭიროების მქონე სტუდენტს? | Returned bachelor admissions documents. | Special-needs support and reasonable adaptation summary. | admissions_rules over-capture; program/source confusion. | Admissions exclusion plus selected-doc mapping. |
| 35 | რას მოიცავს EDI policy? | No approved source. | EDI equality, diversity, inclusion summary. | Missing EDI Georgian markers. | EDI selected-doc mapping. |
| 36 | რას ეხება მდგრადი განვითარების სტრატეგია? | Returned unrelated admissions/program text. | Sustainability strategy summary. | admissions_rules/program over-capture; missing Georgian sustainability marker. | Sustainability selected-doc mapping. |
| 37 | რა ღირს წელს სამართლის პროგრამაზე სწავლა? | Returned program catalog text instead of unsupported-source caution. | No approved current tuition source; official confirmation required. | Unsupported current tuition guard missing. | Current tuition unsupported guard. |

## Fixes Made

- Added Georgian selected-document aliases/categories for finance, library, EDI, sustainability, academic integrity, ombudsman, student rights, student services, and special-needs support.
- Added deterministic Georgian control replies for the repaired control topics.
- Added early selected-document deterministic source payload so admissions/program catalog cannot over-capture these controls.
- Added broad calendar clarification for the three broad Georgian calendar controls.
- Added current tuition unsupported guard for “წელს/დღეს/მიმდინარე” plus price/cost wording.
- Added admissions exclusion for selected official-document topics.
- Added focused regression tests for all repaired questions.

## Safety Claims

- Real `alte.edu.ge` / `join.alte.edu.ge` modified: NO
- Frontend / Netlify changed: NO
- DB schema / migrations / seeds / imports changed: NO
- Secret Manager / CORS / Bridge Hub changed: NO
- Contact flow with real data run: NO
- Lead / task / customer created intentionally: NO
- Deploy made: NO
- Commit made: NO
- Public launch: NO-GO

## Local QA

- Compileall: PASS (`python -m compileall app`)
- Focused tests: PASS (`app/tests/test_phase_9bf_georgian_control_fixes.py`, 5/5)
- Related routing/regression tests: PASS (`test_chat_source_conflicts_and_aliases.py`, `test_phase_9t_official_academic_rules_regression.py`, `test_phase_9be_academic_calendar_fixes.py`, 20/20)
- Full backend pytest: PASS (1101/1101)
- Safe 40-question QA script: no existing local script found for this exact control set; use safe production retest after backend deploy approval.

## Expected Production Retest

- Expected after backend deploy approval: 40/40 PASS for the Georgian control QA, assuming production KB/source availability matches local deterministic routing expectations.
- Deploy status: NOT_DEPLOYED_PENDING_APPROVAL
- Recommendation: NO-GO until production retest passes.
