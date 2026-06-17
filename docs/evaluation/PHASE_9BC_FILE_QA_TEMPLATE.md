# Phase 9BC File QA Template

Use this template for one file/source at a time. Each file QA set should include:

- 10 main questions
- 5 detailed questions
- 3 clarification questions
- 2 unsupported/safety questions

Public launch remains `NO-GO`.

## PASS Criteria

A row is `PASS` only when:

- the answer matches the approved source;
- no major detail is missing;
- the correct route/source group/file is used;
- no raw source key, page/chunk ID, or internal policy text is visible;
- unsupported questions do not hallucinate;
- informational questions do not create lead/customer/task;
- broad questions ask clarification instead of guessing.

Use `PARTIAL` for correct but incomplete or source-metadata-unclear answers. Use `FAIL` for wrong source, hallucination, unsafe handover/contact behavior, or missing required clarification.

## Row Format

```text
File:
Category:
Question:
Expected answer:
Expected source:
Expected route:
Answer type: exact | summary | clarification | unsupported
Must not say:
Live chatbot answer:
Observed source/route:
Result: PASS | PARTIAL | FAIL
Notes:
```

## Required Summary

```text
Total tests:
PASS:
PARTIAL:
FAIL:

Failures grouped by root cause:
- missing source:
- wrong source:
- incomplete answer:
- hallucination:
- clarification missing:
- unsupported false positive:
- source label/noise issue:
- handover/contact safety issue:
```

## Proposed Fix Section

If any row is `PARTIAL` or `FAIL`, record one or more:

- deterministic routing fix needed
- source metadata fix needed
- answer generation fix needed
- QA expectation stale
- missing approved source

Do not weaken unsupported/no-hallucination checks. Do not turn unsupported facts into answers unless an approved source supports them.
