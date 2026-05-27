# Phase 9Z - Alte Chatbot Required Knowledge Package

PHASE_9Z_ALTE_CHATBOT_REQUIRED_KNOWLEDGE_STATUS=APPLIED_TO_PRODUCTION_KB_PENDING_SAFE_SMOKE_AND_PUBLIC_LAUNCH_APPROVAL

Decision state:

BACKEND_DEPLOYED_CHATBOT_REQUIRED_KNOWLEDGE_APPLIED_PENDING_SAFE_SMOKE_AND_PUBLIC_LAUNCH_APPROVAL

## Source

Source directory:

`C:\Users\Acer\Documents\Codex\2026-05-19\unexpected-status-403-forbidden-detail-code\alte_documents`

The source export contains `132` Alte documentation files. This phase selected only student/applicant-facing documents that are useful for the chatbot and skipped internal-only administrative materials unless directly relevant to a user-facing question.

## Final Files

- JSONL: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_knowledge.jsonl`
- Markdown: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_knowledge.md`
- Sources: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_sources.md`
- Reviewer CSV: `backend/reports/alte_chatbot_required_knowledge_reviewer_queue.csv`
- Smoke questions: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_smoke_questions.jsonl`
- Review summary: `backend/app/knowledge_seed/alte_chatbot_required_knowledge/alte_chatbot_required_review_summary.md`
- Builder: `backend/app/scripts/build_alte_chatbot_required_knowledge.py`
- Apply script: `backend/app/scripts/apply_alte_chatbot_required_knowledge.py`
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

- Generated records: `433`
- Reviewer queue rows: `433`
- Expanded coverage: payment/finance routing, state/social grants, formal communication, international student routing, IT support, and student service department routing
- Smoke question bank: `20` no-contact questions for post-import validation
- Generated language: Georgian
- Format: question-answer records with topic, department, source, and answer policy metadata
- Duplicate content skipped: `6`
- Direct internal-only administrative documents skipped where they were not student/applicant-facing
- Dry-run apply result: PASS
- Production apply result: PASS
- Production apply mode: `--apply --approve-for-chatbot`
- Created sources: `433`
- Created snippets: `433`
- Re-approval update after user approval: `433` sources and `433` snippets updated to `approved` for chatbot retrieval
- Review-required metadata retained: `360`
- Approved for chatbot retrieval: `433`
- Post-apply session payload smoke: PASS `2/2`
- Post-apply test site API smoke: PASS `10/10`
- Post-apply production knowledge smoke: PASS `25/25`
- Post-apply smoke warning: one IT-support case returned `should_create_lead=true` without contact details, but no customer/lead/task record was created

## Safety

- Production DB modified: YES - Knowledge Base source/snippet records only
- `--apply run: YES`
- Lead/task/customer creation: NO
- Contact details sent in smoke: NO
- Contact-flow test run: NO
- Migration/seed run: NO
- Cloud Run deploy: NO
- CORS change: NO
- Secret Manager change: NO
- Real Alte site modified: NO
- Contact-flow test run: NO
- Lead/task/customer creation: NO
- Public launch: NO-GO

## Next Step

The user approved direct use of the official extracted document content. The package was applied to production Knowledge Base tables only. Sensitive records retain review-required metadata and conservative answer text, but are approved for chatbot retrieval. Public launch remains NO-GO until website/privacy/embed/smoke approvals are complete.
