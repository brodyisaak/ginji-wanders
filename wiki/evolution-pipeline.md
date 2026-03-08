# evolution pipeline

`scripts/evolve.sh` runs the autonomous loop end-to-end.

1. preflight checks run `py_compile` and `pytest`
2. issue collection pulls open issues and formats `ISSUES_TODAY.md`
3. planning phase writes `SESSION_PLAN.md` with one focused improvement
4. implementation loop executes up to five task attempts
5. validation/recovery reruns build checks, attempts fixes, and can revert `src/` + `tests/`
6. journal fallback prepends an entry if missing
7. issue response handling posts comments and closes issues when status is fixed or wontfix
8. site rebuild runs `python scripts/build_site.py`
9. commit/tag/push finalizes the session

`DAY_COUNT` tracks day progression, while `JOURNAL.md` stores the narrative memory of each day.
