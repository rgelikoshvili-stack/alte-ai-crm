# Test Knowledge Seed Approval Gate

## Seed File

```text
backend/app/knowledge_seed/alte_required_test_knowledge_v1.json
```

## Seed Command

```powershell
python -m app.scripts.seed_required_test_knowledge
```

For production mode, the script requires an explicit approval flag and should only be run after content review.

## Current Status

```text
PENDING_APPROVAL
```

## Warning

Do not seed unreviewed content into production as official public answers.

The Phase 8O seed file is manually curated and conservative, but several snippets are marked review required because exact official details still need confirmation.

## Approval Fields

- approved: PENDING
- approved by: PENDING
- approval date: PENDING
- notes: PENDING

## Required Explicit Phrase

Production test knowledge seed may proceed only after the user explicitly says:

```text
Approve Phase 8Q-Execution for production test knowledge seed
```
