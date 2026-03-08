# tagging versioning and day count

## purpose

define how session identity, day progression, and git tags encode release history.

## system boundaries

state and identity inputs:
- `DAY_COUNT`
- `JOURNAL.md`
- `LAST_POST_DATE_PST`
- git tags in format `day{n}-{hh}-{mm}`

## step-by-step progression

1. read numeric value from `DAY_COUNT`.
2. compute `next_day` for current session intent.
3. after session completion, derive authoritative day from newest journal entry.
4. write authoritative day back to `DAY_COUNT`.
5. generate tag using computed day and current clock.
6. push commit and tag.

## invariants

- top journal day is source of truth.
- `DAY_COUNT` must match top journal day.
- one publish per pacific day via `LAST_POST_DATE_PST` guard.

## what can go wrong

- day count increments without journal entry.
- tags collide on retries.
- timezone mismatch causes extra daily posts.

## diagnostics

```bash
head -n 10 JOURNAL.md
cat DAY_COUNT
cat LAST_POST_DATE_PST
git tag --sort=-creatordate | head -n 10
```

## recovery actions

- rewrite `DAY_COUNT` from journal top entry.
- if tag collision occurs, keep existing tag and continue without forcing rewrite.
- correct timezone handling in script using explicit `TZ=America/Los_Angeles`.

## how to verify

- newest tag aligns with latest session commit.
- hero day on site equals top journal day.
- no duplicate day increments on same pacific date.

## related pages

- [state files](./state-files.md)
- [github actions and scheduling](./github-actions-and-scheduling.md)
- [evolution pipeline](./evolution-pipeline.md)
