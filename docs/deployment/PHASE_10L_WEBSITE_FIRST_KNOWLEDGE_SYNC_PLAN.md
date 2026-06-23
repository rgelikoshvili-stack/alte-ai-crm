# Phase 10L Website-First Knowledge Sync Plan

Date: 2026-06-23

Status: `PLANNING_ONLY`

Decision:

`WEBSITE_FIRST_FRESHNESS_PRIORITY_DEFINED_PUBLIC_LAUNCH_NO_GO`

## Current Production Context

- Backend revision: `alte-ai-crm-backend-00065-l8r`
- Traffic: `100%`
- Health: `200`
- Chat-only embed readiness: `READY_FOR_APPROVAL`
- Contact-flow: `BLOCKED`
- Public launch: `NO-GO`

## Scope

This plan defines a website-first knowledge architecture for Alte AI CRM. It does not implement a crawler, crawl or scrape the real site, modify production KB, modify the real website, deploy code, change frontend/Netlify, change DB/schema/migrations, or enable contact-flow.

Core rule:

- Variable or freshness-sensitive information must use approved website sync first.
- Stable information may use approved structured KB or uploaded files when no newer approved website content exists.

## Freshness Classifier: Variable vs Stable Knowledge

The router should classify each question as either `variable_freshness_sensitive` or `stable_reference`. The classification should be deterministic first, with optional assisted review later only for admin workflows. Public answers must respect the classification before retrieval ranking.

### Variable Knowledge

Variable knowledge must include:

- all periods, dates, deadlines, schedules
- admissions deadlines
- registration dates
- academic calendar dates
- semester start/end dates
- exam/midterm/final/retake periods
- tuition/fees/prices
- grants/funding/scholarships
- current admissions status
- current program availability
- contact details and office hours
- current campaigns/news/announcements
- any question containing year-specific terms such as `2026`, `2027`, `2028`
- any question asking `current`, `updated`, `latest`, `this year`

Georgian variable markers:

- `როდის`
- `ვადა`
- `ბოლო ვადა`
- `რეგისტრაცია`
- `ჩარიცხვა`
- `მიღება`
- `სემესტრი`
- `კალენდარი`
- `გამოცდა`
- `საფასური`
- `ფასი`
- `რა ღირს`
- `გრანტი`
- `დაფინანსება`
- `სტიპენდია`

English variable markers:

- `when`
- `deadline`
- `application deadline`
- `admission deadline`
- `registration`
- `semester`
- `calendar`
- `exam`
- `tuition`
- `fee`
- `cost`
- `scholarship`
- `grant`
- `funding`
- `latest`
- `updated`
- `current`

### Stable Knowledge

Stable knowledge may include:

- program type/level
- general program description
- credits/ECTS only if officially approved and not superseded by website
- general admission document categories
- academic integrity principles
- general library/student service rules
- ombudsman/general support descriptions
- general student rights/policies
- historical/archived references

Stable classification must not override the variable classifier. If a question contains both stable and variable markers, the variable/freshness-sensitive route wins. Example: `Computer Science პროგრამა რამდენი კრედიტია 2028 წელს?` must be treated as variable because it is year-specific.

## Source Priority Model

Approved source priority:

| Source class | Priority | Public chatbot usable | Notes |
| --- | ---: | --- | --- |
| `approved_website_sync` | 100 | Yes | Highest-priority source for variable/current information. |
| `approved_structured_kb` | 80 | Yes | Preferred stable source; usable for variable answers only when explicitly marked current/approved. |
| `approved_uploaded_file` | 60 | Yes | Usable when structured KB is missing or as supporting source; loses to approved website on conflicts. |
| `archived_historical` | 20 | Conditional | Not used for current claims; only for historical/archived answers with clear labeling. |
| `unapproved_draft` | N/A | No | Never usable by the public chatbot. |

## Retrieval Decision Policy

### Variable Or Freshness-Sensitive Questions

If the question is variable/freshness-sensitive:

1. Search `approved_website_sync` first.
2. If an approved website answer exists with sufficient confidence, use it.
3. If the website answer is missing, use `approved_structured_kb` only if the item is marked current and approved.
4. Use `approved_uploaded_file` only as supporting evidence when it is current/approved and does not conflict with website content.
5. If confidence is not sufficient, ask a clarification question or return a safe fallback.
6. Do not invent missing dates, deadlines, prices, schedules, or availability claims.

Safe fallback pattern:

- Georgian: current information must be confirmed on the official page or with the relevant admissions/finance/administrative office.
- English: current information must be confirmed on the official page or with the relevant admissions/finance/administrative office.

### Stable Questions

If the question is stable:

1. Search `approved_structured_kb` first.
2. If structured KB is missing, search `approved_uploaded_file`.
3. Search `approved_website_sync` as an override check when newer approved content exists.
4. If website content conflicts with file/KB content, website wins when approved and current.
5. If sources are insufficient, ask clarification or provide a safe no-source fallback.

### Conflict Handling

If website and file/KB content conflict:

1. `approved_website_sync` wins for public answer selection.
2. Record the conflict in retrieval metadata.
3. If the conflict is high risk, route the item to manual review before relying on stale lower-priority sources.
4. Do not expose raw conflict metadata or internal source IDs to public users.

High-risk conflict categories:

- dates
- deadlines
- tuition/fees
- admissions rules
- program requirements
- ECTS/credits
- legal/privacy text
- contact details

## Answer Behavior

- Public source label should show a clean official website label when website content wins.
- If using files, show a clean file/source-group label.
- Do not show raw internal source IDs, chunk IDs, file paths, sync job IDs, crawler IDs, or draft labels.
- Do not invent missing dates, deadlines, or prices.
- If website lacks current information, say the current information must be confirmed on the official page or with the relevant admissions/finance office.
- If the answer uses archived historical content, clearly label it as historical and do not present it as current.
- If a variable question has no approved current source, prefer safe fallback or clarification over a stale answer.

## Proposed Architecture

### Source Metadata Fields

Future implementation should store source metadata sufficient for priority and safety decisions:

- `source_class`: `approved_website_sync`, `approved_structured_kb`, `approved_uploaded_file`, `archived_historical`, `unapproved_draft`
- `approval_status`: `draft`, `reviewed`, `approved`, `rejected`, `archived`
- `freshness_class`: `variable_freshness_sensitive`, `stable_reference`, `mixed`
- `effective_date`
- `expires_at` or `valid_until`
- `last_verified_at`
- `source_url` for website sync
- `public_source_label`
- `internal_source_id`
- `conflict_status`
- `manual_review_required`

This Phase 10L plan does not require a DB/schema change. These fields are proposed for later implementation phases.

### Classifier Output

Future classifier output should be structured:

```json
{
  "freshness_class": "variable_freshness_sensitive",
  "matched_markers": ["deadline", "2028"],
  "requires_website_first": true,
  "high_risk_categories": ["dates", "deadlines"],
  "safe_to_use_stable_kb_without_website": false
}
```

### Retrieval Metadata

Future retrieval metadata should include:

```json
{
  "selected_source_class": "approved_website_sync",
  "selected_priority": 100,
  "conflicts_detected": false,
  "manual_review_required": false,
  "public_source_label": "Official Alte website"
}
```

## Example Decisions

| Question | Freshness class | First source | Expected behavior |
| --- | --- | --- | --- |
| `როდის მთავრდება მიღება?` | variable | approved website sync | Website-first deadline/admissions answer or safe fallback. |
| `2028 წლის აკადემიური კალენდარი მითხარი` | variable | approved website sync | If no approved 2028 website calendar exists, safe unsupported/current-info fallback. |
| `რა ღირს სამედიცინო სწავლა?` | variable | approved website sync | Website-first tuition answer; no invented amount. |
| `მითხარი მედიცინის პროგრამაზე` | stable | structured KB | General program answer; website can override if newer. |
| `აკადემიური კეთილსინდისიერება რას ნიშნავს?` | stable | structured KB | Stable policy/principle answer from approved KB/files. |
| `ბაკალავრიატზე რა საბუთებია საჭირო?` | stable unless asking current/updated | structured KB | General document categories; website override if current requirements differ. |

## Rollout Phases

### Phase 10M: Local Preview Crawler For Approved Test URLs Only

- Build a local-only preview crawler for explicitly approved test URLs.
- Do not crawl real production site broadly.
- Do not write to production KB.
- Store preview output outside public retrieval.
- Verify robots/scope controls and URL allowlist behavior.

### Phase 10N: Draft Website Sync Storage And Priority Model

- Add draft storage for website sync output.
- Store source priority metadata.
- Keep draft content unavailable to the public chatbot.
- Add conflict detection metadata.
- No public retrieval from unapproved draft content.

### Phase 10O: Admin Review/Approval Workflow

- Let admins review draft website sync entries.
- Approve, reject, archive, or request correction.
- Record reviewer and verification timestamps.
- Require manual review for high-risk conflicts.

### Phase 10P: Website-First Retrieval Implementation

- Implement freshness classifier in `/api/chat/message` and `/api/knowledge/ask` retrieval planning.
- Route variable questions to approved website sync first.
- Preserve stable KB-first behavior for stable questions.
- Add clean public website source labels.
- Add conflict recording and high-risk review flags.

### Phase 10Q: Production-Safe Website Sync QA

- Test with approved URLs only.
- Verify variable questions use website-first priority.
- Verify stable questions still answer from approved structured KB/files when appropriate.
- Verify conflicts prefer approved website content.
- Verify no raw source IDs are exposed.
- Verify no invented dates, deadlines, prices, or schedules.

## Safety Constraints

- Planning only in Phase 10L.
- No crawler implemented.
- No real site crawled or scraped.
- No production KB changed.
- No real `alte.edu.ge` or `join.alte.edu.ge` changes.
- No frontend/Netlify changes.
- No DB/schema/migration changes.
- No Secret Manager/CORS/Bridge Hub changes.
- Contact-flow remains BLOCKED.
- No lead/customer/task creation.
- Public launch remains NO-GO.
