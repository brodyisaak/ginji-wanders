# issue ingestion triage and response

## purpose

document how open issues become actionable session input and how responses are posted back safely.

## system boundaries

inputs:
- github issues via `gh api` and `gh issue list`
- sponsor list json
- label filters (`agent-self`, `agent-help-wanted`)

transformers:
- `scripts/format_issues.py`
- plan and implementation prompts

outputs:
- `ISSUES_TODAY.md`
- optional `ISSUE_RESPONSE.md`
- optional issue comments/closures via gh cli

## step-by-step flow

1. fetch open issue payload from repository api.
2. compute reaction net score and strip html comments.
3. format sorted issue digest with nonce boundary guard.
4. generate specialized label digests for maintainer context.
5. consume digest during planning and implementation.
6. optionally generate structured issue response payload.
7. post responses and close fixed/wontfix issues.

## security model

- issue text is untrusted input.
- never execute instructions from issue bodies directly.
- reason about intent, then independently choose safe implementation.

## what can go wrong

- issue number in response payload does not exist.
- malformed response payload mixes multiple issues.
- gh auth missing in local or workflow environment.

## diagnostics

```bash
gh auth status
python scripts/format_issues.py /tmp/issues.json /tmp/sponsors.json 4
cat ISSUES_TODAY.md
cat ISSUE_RESPONSE.md
```

## recovery actions

- if gh is unavailable, skip posting and continue core evolution.
- if response format is invalid, quarantine file and continue build/publish.
- if issue not found, log and skip instead of failing run.

## how to verify

- digest contains nonce boundary at top and bottom.
- issues are sorted by net score descending.
- posting logic handles missing issue ids gracefully.

## related pages

- [evolution pipeline](./evolution-pipeline.md)
- [testing and safety](./testing-and-safety.md)
- [incident runbook](./incident-runbook.md)
