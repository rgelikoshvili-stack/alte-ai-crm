# Phase 9AO Full Chatbot Functionality QA Result

PHASE_9AO_FULL_FUNCTIONALITY_STATUS=FAILED_PENDING_FIXES

Decision state:

```text
BACKEND_DEPLOYED_FULL_CHATBOT_FUNCTIONALITY_QA_FAILED_PENDING_FIXES
```

Public launch: NO-GO

## Test Run

Test date/time:

```text
2026-05-31 15:20:24 +04:00
```

Tested URLs:

- Netlify widget: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Local Operator CRM: `http://127.0.0.1:5173`

No real Alte site was modified. No assets were uploaded. No deploy was run. No production DB migration or seed was run. No Secret Manager, CORS, Bridge Hub, or production config was changed. Contact form submission was not executed.

## Summary

```text
TOTAL_CHECKS_RUN=962
PASSED_CHECKS=959
FAILED_CHECKS=3
PUBLIC_LAUNCH_STATUS=NO_GO
```

Backend status:

- Production backend responded to live Netlify-origin chat requests.
- `/chat/session/start`, `/chat/message`, and `/chat/handover/{conversation_id}` worked in safe QA flows.
- Full backend test suite passed locally: `888 passed`.

Netlify widget status:

- Widget loads and opens.
- Georgian UI renders without mojibake.
- Message input works.
- Enter sends message.
- Shift+Enter creates newline.
- KA/EN toggle works.
- Reset/new chat works.
- Mobile viewport has no horizontal scroll.
- Frontend did not call `api.anthropic.com`.
- No frontend API key exposure was detected in network checks.
- No CORS console errors were detected.

## Browser UI Smoke

Result: PARTIAL PASS

Passed:

- Widget opens.
- Georgian UI renders correctly.
- No `áƒ` mojibake detected.
- Message input works.
- Enter sends message.
- Shift+Enter creates newline.
- KA/EN toggle works.
- Reset/new chat works.
- Mobile `390x844` check showed no horizontal scroll.
- Contact form opens without submission.
- Wait for operator button is visible and produces confirmation.

Sidebar department visibility:

| Department | Result |
| --- | --- |
| მიღება | PASS |
| პროგრამები | PASS |
| დაფინანსება | PASS |
| საერთ. სტუდენტები | PASS |
| მედიცინა / MD | FAIL - visible label appears as `მედიცინა/MD` without spaces |
| ბიბლიოთეკა | PASS |
| კარიერა | PASS |
| IT დახმარება | PASS |
| ცოცხალი ოპერატორი | PASS |

Bug:

- `BUG-9AO-UI-01`: expected sidebar label `მედიცინა / MD` was not found exactly; the visible label appears to be `მედიცინა/MD`.

## Official KB Answer Tests

Result: PARTIAL PASS

| Case | Result | Route | Source status | Evidence snippet |
| --- | --- | --- | --- | --- |
| Bachelor ECTS | PASS | `study_process` | `answered_from_approved_source` | Answer included `240 ECTS` and did not include `180`. |
| Master ECTS | PASS | `programs` | `answered_from_approved_source` | Answer included `120 ECTS`. |
| Student status suspension | PASS | `study_process` | `answered_from_approved_source` | Answer said suspension total term must not exceed `5` years. |
| Computer Science spring registration | FAIL | `admissions` | `answered_from_approved_source` | Reply was fallback: `ამ მომენტში AI სერვისთან კავშირი შეფერხებულია...`; it did not include `9-14 March` or `30 March`. |

The Computer Science case was retried once and failed the same way. This appears reproducible during this QA run.

Bug:

- `BUG-9AO-KB-01`: Computer Science spring registration question returns an AI-service fallback even though approved sources are attached. Expected answer must include `9-14 March` registration and semester start `30 March` if mentioned.

## Clarification Behavior Tests

Result: PASS

| Question | Result | Route | Evidence |
| --- | --- | --- | --- |
| `სწავლა მაინტერესებს` | PASS | `admissions` | Asked clarification and showed `მიღება`, `პროგრამები`, `სწავლის საფასური`, `სტუდენტის სტატუსი`. |
| `პროგრამები მაინტერესებს` | PASS | `programs` | Asked program clarification and showed `ბაკალავრიატი`, `მაგისტრატურა`, `მედიცინა/MD`, `საერთაშორისო მიღება`. |
| `გადახდებზე მაინტერესებს` | PASS | `finance` | Asked whether user means tuition, payment schedule, or finance department. Did not route to International Admissions. |
| `სტატუსზე მაქვს კითხვა` | PASS | `study_process` | Asked status clarification and showed `შეჩერება`, `აღდგენა`, `შეწყვეტა`, `მობილობა`. |

## Department Routing Tests

Result: PASS

| Question | Result | Route | Source status / behavior |
| --- | --- | --- | --- |
| `ბიბლიოთეკის რესურსები როგორ გამოვიყენო?` | PASS | `library` | No approved source found; offered operator handover. Did not route International Admissions. |
| `emis.alte.edu.ge-ში ვერ შევდივარ` | PASS | `it_support` | Routed to IT support context. |
| `მინდა ფინანსურ დეპარტამენტთან დაკავშირება` | PASS | `finance` | Routed to Finance. Did not route International Admissions. |
| `I am an international student and want to apply to Medicine` | PASS | `medicine` | Routed to Medicine with acceptable international/medicine context. |

## Unsupported / No-Hallucination Test

Result: PASS

Question:

```text
2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?
```

Observed answer:

```text
ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე. შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან, რომ თქვენი კითხვა სწორ დეპარტამენტს გადაეცეს.
```

Checks:

- No invented scholarship details.
- No fake deadlines, percentages, or eligibility rules.
- No direct phone/email/name request inside the chat answer.
- No lead/task/customer IDs returned by chat response.
- Operator handover was offered.

## Contact Form Field Test

Result: PARTIAL PASS

Visible fields:

- `სახელი და გვარი`: PASS
- `ტელეფონი`: PASS
- `ენა`: PASS
- `ელ.ფოსტა`: PASS
- `ინტერესის სფერო`: PASS
- `თქვენი კითხვა / შეტყობინება`: PASS
- consent checkbox/copy: PASS
- `გაგზავნა`: PASS

Question/message textarea:

- Visible: PASS
- Editable: PASS
- No mojibake: PASS
- Contact submit: NOT EXECUTED

Bug:

- `BUG-9AO-UI-02`: textarea was not prefilled with the latest user question. It was prefilled with generic operator text: `შემიძლია დაგაკავშიროთ ოპერატორთან ამ ჩატში ან დატოვოთ საკონტაქტო ინფორმაცია.`

Contact-flow approval remains:

```text
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
CONTACT_FORM_SUBMIT_EXECUTED=NO
REAL_CONTACT_DATA_SENT=NO
LEAD_TASK_CUSTOMER_CREATED=NO
```

## Wait For Operator Test

Result: PASS

Chatbot:

- Wait for operator button was visible.
- Confirmation was shown after click.
- No phone/email/name was required.
- No contact form submission was executed.

Backend handover smoke:

- `/chat/handover/{conversation_id}` returned `200`.
- Conversation status became `waiting_for_operator`.
- `task_id` was `null`.
- No lead/task/customer was created by the chat response.

Operator CRM visibility:

- Production inbox API returned `200`.
- Waiting conversation was visible in Operator CRM inbox data.
- `status`: `waiting_for_operator`
- `waiting_status`: `waiting_for_operator`
- `human_handover`: `true`
- latest message present: YES
- timestamp present: YES
- selected department visible: `Finance`
- customer attached: NO
- lead attached: NO

Known limitation still applies:

- `pollOperatorMessages()` currently returns `[]` in the final bundle, so visitor-side live operator replies may not stream back yet.

## Safety Checks

Result: PASS

- No lead/task/customer created by informational questions.
- No contact creation flow executed with real data.
- No contact form submit executed.
- No direct phone/email/name request in normal answer.
- No frontend API key detected.
- No direct `api.anthropic.com` browser call detected.
- No CORS console errors detected.
- No Georgian mojibake detected.
- Public launch remains NO-GO.

## Automated QA

Commands run:

```text
python -m compileall app
pytest --basetemp .pytest_tmp_9ao_full_functionality
python -m app.scripts.visual_qa_netlify_widget
python -m app.scripts.production_phase_9ai_chatgpt_style_routing_qa
python -m app.scripts.production_phase_9ah_wait_for_operator_smoke
```

Results:

- Compileall: PASS
- Full pytest: `888 passed`
- Netlify visual QA: PASS
- Phase 9AI routing QA: `12/12 passed`
- Wait-for-operator smoke: PASS
- Focused live 9AO API QA: `12/13 passed`
- Operator CRM visibility check: PASS
- UI probe: `30/31 passed`
- Contact textarea prefill probe: FAILED expected latest-user-question prefill

## Known Limitations

- Visitor-side live operator reply polling is not active in the final bundle because `pollOperatorMessages()` currently returns `[]`.
- Official Privacy URL remains pending.
- Contact creation is not approved.
- Dirty working tree reconciliation remains pending.
- Public launch remains NO-GO.

## Bugs Found

1. `BUG-9AO-KB-01` - Computer Science spring registration question returns AI-service fallback instead of official answer.
   - Severity: launch-blocking for full functionality.
   - Expected: include `9-14 March`; include `30 March` if semester start is mentioned.

2. `BUG-9AO-UI-01` - sidebar exact label mismatch for `მედიცინა / MD`.
   - Severity: minor UI polish unless exact copy is required.
   - Observed: `მედიცინა/MD`.

3. `BUG-9AO-UI-02` - contact message textarea does not prefill with latest user question.
   - Severity: minor-to-medium UX issue.
   - Observed: generic operator text is prefilled instead.

## Recommended Fixes

- Fix or harden the Computer Science spring registration response path so it returns deterministic official text from approved source when the AI provider fails.
- Decide whether sidebar copy must be exactly `მედიცინა / MD`; if yes, adjust the label spacing.
- Change contact modal prefill to use the latest user-authored question when available, while preserving generic fallback text when no user message exists.
- Keep contact submission disabled or unexecuted until privacy/contact-flow approval is recorded.

## Final Recommendation

```text
READY_FOR_PUBLIC_LAUNCH=NO
READY_FOR_OWNER_REVIEW=YES
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_FIXES_AND_APPROVALS
```

The chatbot is largely functional, but Phase 9AO should remain failed pending fixes because the Computer Science official KB answer did not return the required date answer during live QA.

