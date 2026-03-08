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
5. generate `SESSION_PLAN.md` through agent planning prompt.
6. run implementation loop for up to five tasks.
7. rerun build checks; auto-fix up to three attempts if needed.
8. ensure journal entry exists, prepend fallback only when missing.
9. ensure learning entry exists, prepend fallback only when missing.
10. process `ISSUE_RESPONSE.md` if present.
11. rebuild site via `python scripts/build_site.py`.
12. write `DAY_COUNT` from latest journal day and persist `LAST_POST_DATE_PST`.
13. commit, tag, and push.

## what can go wrong

- plan generation fails and leaves weak task guidance.
- implementation modifies protected files indirectly.
- build remains red after auto-fix loop.
- journal or learnings entry generation fails.

## diagnostics

```bash
bash -n scripts/evolve.sh
rg -n "step [0-9]+|LAST_POST_DATE_PST|DAY_COUNT" scripts/evolve.sh
cat SESSION_PLAN.md
cat ISSUE_RESPONSE.md
```

## recovery actions

- if validation fails repeatedly, restore `src/` and `tests/` and rerun checks.
- if journal generation fails, prepend fallback entry and log root cause.
- if issue processing fails, skip close/comment actions and preserve run health.

## how to verify

```bash
python -m py_compile src/ginji.py
python -m pytest tests/ -q
python scripts/build_site.py
```

confirm:
- `DAY_COUNT` matches newest journal day.
- site reflects newest journal content.
- only one post day increment per pacific day.

## related pages

- [github actions and scheduling](./github-actions-and-scheduling.md)
- [tagging versioning and day count](./tagging-versioning-and-day-count.md)
- [issue ingestion triage and response](./issue-ingestion-triage-and-response.md)
