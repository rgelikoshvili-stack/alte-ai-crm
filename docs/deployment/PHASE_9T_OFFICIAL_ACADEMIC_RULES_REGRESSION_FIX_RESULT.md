# Phase 9T Official Academic Rules Regression Fix Result

PHASE_9T_OFFICIAL_ACADEMIC_RULES_REGRESSION_STATUS=FIXED_PENDING_BROWSER_OR_DEPLOY_RETEST

Decision state:
BACKEND_CODE_OFFICIAL_ACADEMIC_RULES_REGRESSION_FIXED_PENDING_RETEST_OR_DEPLOY_APPROVAL

## Observed Regression

Question:

`რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?`

Wrong chatbot answer observed:

`საბაკალავრო პროგრამის დასასრულებლად საჭიროა 180 ECTS კრედიტი (3-წლიანი პროგრამა).`

Correct official answer:

`საბაკალავრო პროგრამის დასასრულებლად საჭიროა 240 ECTS კრედიტი.`

One-cycle programs must be answered separately when relevant:

- Medicine one-cycle program: 360 ECTS
- Dentistry one-cycle program: 300 ECTS

## Root Cause

Older Alte marketing/program overview KB snippets include Business Administration `180 კრედიტი/3 წელი` wording. Those generic program snippets could be retrieved ahead of the uploaded official academic rules for a general bachelor completion question.

The official academic rules source says a bachelor program requires at least 240 credits, with separate exception wording for legally allowed 180-credit bachelor programs. The chatbot must not turn that exception or marketing text into the general bachelor completion answer.

## Fix Summary

- Official academic rules questions now first search `official_academic_rules` sources.
- Initial Claude/AI knowledge context also prioritizes `official_academic_rules` for academic rules questions.
- Deterministic conservative replies were added for high-risk official facts:
  - Bachelor ECTS: 240
  - Master ECTS: 120
  - Teaching language: Georgian; some programs in English
  - Student status suspension maximum: 5 years
- Clearly unsupported future/campus scholarship questions remain blocked from unrelated source-backed answers.
- Regression tests cover the stale 180-credit snippet conflict.

## Evaluation Update

- `alte_official_academic_rules_30_qa.json` Q05 now explicitly requires `240 ECTS`.
- Q05 forbids `180 ECTS`, `180 კრედიტ`, `3-year program`, and `3-წლიანი` for the general bachelor completion question.

## Tests

- `python -m compileall app`: PASS
- `pytest --basetemp .pytest_tmp_9t_regression`: `731 passed`
- `python -m app.scripts.evaluate_official_academic_rules_30_qa`: `30/30 PASS`
- `python -m app.scripts.verify_phase_9t_official_academic_rules_knowledge`: PASS

## Production Retest

Production chatbot was not retested with this fix because a new Cloud Run deploy is required first.

Deploy approval required doc:

`docs/deployment/PHASE_9T_DEPLOY_APPROVAL_REQUIRED.md`

## Safety

- Production DB modified: NO
- Production migration run: NO
- Production seed run: NO
- DB schema changed: NO
- Secret Manager changed: NO
- CORS changed: NO
- Real Alte site modified: NO
- Contact details requested: NO
- Lead/task/customer intentionally created: NO
- Public launch: NO-GO
