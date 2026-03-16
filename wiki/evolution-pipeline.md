# evolution pipeline

## purpose

document the exact autonomous session lifecycle in `scripts/evolve.sh`.

## system boundaries

in scope:
- preflight validation
- issue intake and planning
- implementation loop
- validation and fallback
- journaling and learnings
- site rebuild and publish

out of scope:
- manual contributor workflows not using `scripts/evolve.sh`

## step-by-step flow

1. verify environment and secrets.
2. run preflight checks:
   - `python -m py_compile src/ginji.py`
   - `python -m pytest tests/ -q`
3. enforce once-per-day guard using pacific date (`LAST_POST_DATE_PST`) so only one journal entry is published per day.
4. fetch issue data and format `ISSUES_TODAY.md`.
5. generate `SESSION_PLAN.md` through agent planning prompt with required fields:
   - `goal`
   - `benchmark_gap`
   - `scope`
   - `metric`
   - `direction`
   - `verify`
   - `guard`
   - `iteration_budget`
   - `stop_condition`
6. dry-run the verify command and capture a numeric baseline before any edits.
7. append a baseline row to `EVOLUTION_RESULTS.tsv`.
8. run a bounded metric loop, default `3` iterations:
   - snapshot the scoped files
   - ask ginji for one atomic change inside scope
   - rerun verify
   - compare against the current best metric
   - run guard
   - keep only improvements that pass the guard
   - restore scope state on discard or crash
9. rerun build checks; auto-fix up to three attempts if needed.
10. ensure journal entry exists, prepend fallback only when missing.
11. ensure learning entry exists, prepend fallback only when missing.
12. process `ISSUE_RESPONSE.md` if present.
13. rebuild site via `python scripts/build_site.py`.
14. write `DAY_COUNT` from latest journal day and persist `LAST_POST_DATE_PST`.
15. commit, tag, and push.

## what can go wrong

- plan generation fails and leaves weak task guidance.
- plan generation omits a required metric field or produces a verify command that cannot be parsed.
- planning chooses another low-leverage hygiene task even though the build is already green.
- verify command fails before baseline, leaving the session without a measurable starting point.
- scope restore fails and leaves discarded iteration changes in the worktree.
- implementation modifies protected files indirectly.
- build remains red after auto-fix loop.
- journal or learnings entry generation fails.

## diagnostics

```bash
bash -n scripts/evolve.sh
python scripts/metric_guard.py measure --command "printf 'score: 1\n'"
rg -n "metric|baseline|guard|iteration_budget|EVOLUTION_RESULTS" scripts/evolve.sh
cat SESSION_PLAN.md
tail -n 10 EVOLUTION_RESULTS.tsv
cat ISSUE_RESPONSE.md
```

## recovery actions

- if the plan is invalid, rewrite `SESSION_PLAN.md` or fall back to the default measured plan.
- if baseline capture fails, switch to the default verify command and regenerate the session plan.
- if an iteration crashes or fails the guard, restore the scoped snapshot before moving on.
- if validation fails repeatedly, restore `src/` and `tests/` and rerun checks.
- if journal generation fails, prepend fallback entry and log root cause.
- if issue processing fails, skip close/comment actions and preserve run health.
- if several sessions repeat the same maintenance class, encode prevention and raise the next session to a capability-level improvement.

## how to verify

```bash
python -m py_compile src/ginji.py
python -m pytest tests/ -q
python scripts/build_site.py
```

confirm:
- `SESSION_PLAN.md` contains the required machine-readable fields.
- `EVOLUTION_RESULTS.tsv` has a baseline row and per-iteration keep/discard/crash rows.
- `DAY_COUNT` matches newest journal day.
- site reflects newest journal content.
- only one post day increment per pacific day.

## related pages

- [github actions and scheduling](./github-actions-and-scheduling.md)
- [tagging versioning and day count](./tagging-versioning-and-day-count.md)
- [issue ingestion triage and response](./issue-ingestion-triage-and-response.md)
