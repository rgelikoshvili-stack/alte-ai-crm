# Phase 9Z - Alte Chatbot Required Knowledge Package

PHASE_9Z_ALTE_CHATBOT_REQUIRED_KNOWLEDGE_STATUS=READY_PENDING_REVIEW_AND_DB_APPLY

Decision state:

BACKEND_DEPLOYED_CHATBOT_REQUIRED_KNOWLEDGE_READY_PENDING_REVIEW_AND_APPLY

## Source

Source directory:

`C:\Users\Acer\Documents\Codex\2026-05-19\unexpected-status-403-forbidden-detail-code\alte_documents`

The source export contains `132` Alte documentation files. This phase selected only student/applicant-facing documents that are useful for the chatbot and skipped internal-only administrative materials unless directly relevant to a user-facing question.

## Final Files

- JSONL: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_knowledge.jsonl`
- Markdown: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_knowledge.md`
- Sources: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_sources.md`
- Builder: `backend/app/scripts/build_alte_chatbot_required_knowledge.py`
- Verifier: `backend/app/scripts/verify_alte_chatbot_required_knowledge.py`

## Included Knowledge Scope

The generated package includes chatbot-ready Georgian Q&A records from the required source categories:

- Educational program catalog
- Academic calendar
- Study process regulation
- Bachelor regulation
- Master regulation
- Examination regulation
- ECTS/credit recognition
- Individual study plan
- E-learning administration
- Plagiarism rules
- Financial support mechanisms
- Dean's grant
- Student services
- Student rights protection mechanisms
- Ombudsman regulation
- Student self-government
- Library rules
- Special needs support
- Career development and alumni services
- Generative AI usage policy
- University/school provisions
- Ethics code

## Output Summary

- Generated records: `394`
- Generated language: Georgian
- Format: question-answer records with topic, department, source, and answer policy metadata
- Duplicate content skipped: `6`
- Direct internal-only administrative documents skipped where they were not student/applicant-facing

## Safety

- Production DB modified: NO
- `--apply run: NO`
- Cloud Run deploy: NO
- CORS change: NO
- Secret Manager change: NO
- Real Alte site modified: NO
- Contact-flow test run: NO
- Lead/task/customer creation: NO
- Public launch: NO-GO

## Next Step

Before DB import, the generated JSONL/Markdown should be reviewed for official wording, sensitive policy handling, and department routing. After review, a separate explicit approval is required to create or run a DB apply step.
