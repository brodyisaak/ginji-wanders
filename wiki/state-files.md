# state files

## purpose

define ownership, lifecycle, and invariants for persistent and ephemeral state files.

## system boundaries

persistent files are committed and provide memory. ephemeral files are session artifacts and may be regenerated.

## state contract table

| file | type | owner | lifecycle | invariant |
| --- | --- | --- | --- | --- |
| `IDENTITY.md` | persistent | maintainers | long-lived | mission text should remain stable and human-readable |
| `PERSONALITY.md` | persistent | maintainers | long-lived | voice rules stay lowercase and consistent |
| `JOURNAL.md` | persistent | agent + maintainers | append-only prepend model | newest entry at top, no deletion of prior days |
| `LEARNINGS.md` | persistent | agent + maintainers | append-only prepend model | at least one learning entry per day |
| `DAY_COUNT` | persistent | evolution pipeline | updated per successful session | matches newest journal day number |
| `LAST_POST_DATE_PST` | persistent | evolution pipeline | updated on publish | equals pacific date of latest posted session |
| `SESSION_PLAN.md` | ephemeral | evolution pipeline | regenerated each run | can be replaced safely |
| `ISSUES_TODAY.md` | ephemeral | evolution pipeline | regenerated each run | bounded formatted digest |
| `ISSUE_RESPONSE.md` | ephemeral | evolution pipeline | optional per run | strict key format when present |

## step-by-step state update order

1. run validations before mutating persistent state.
2. write session artifacts (`SESSION_PLAN.md`, implementation logs).
3. ensure journal and learnings are prepended.
4. derive `DAY_COUNT` from newest journal header.
5. write `LAST_POST_DATE_PST` with pacific date.
6. rebuild site from journal, identity, and day count.

## what can go wrong

- day count drifts from journal top entry.
- journal entry generation overwrites history.
- learnings file misses daily entry.

## diagnostics

```bash
head -n 30 JOURNAL.md
head -n 40 LEARNINGS.md
cat DAY_COUNT
cat LAST_POST_DATE_PST
```

## recovery actions

- recompute day count from journal and rewrite `DAY_COUNT`.
- recover deleted journal entries from git history.
- prepend fallback learning entry if daily generation fails.

## how to verify

- `DAY_COUNT` equals top journal day.
- `LAST_POST_DATE_PST` equals latest pacific publish date.
- site hero day and timeline align with journal top.

## related pages

- [tagging versioning and day count](./tagging-versioning-and-day-count.md)
- [evolution pipeline](./evolution-pipeline.md)
- [incident runbook](./incident-runbook.md)
