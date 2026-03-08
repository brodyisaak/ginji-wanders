# contribution guidelines for agent safe changes

## purpose

set contributor rules that preserve agent reliability while allowing iteration.

## system boundaries

applies to:
- code changes in runtime, scripts, tests, docs, and wiki
- manual maintainer commits
- autonomous commits produced by evolution workflow

## step-by-step contribution flow

1. define one focused change.
2. add or update tests before behavior change when possible.
3. implement smallest viable diff.
4. run compile and tests.
5. update docs/wiki when behavior or operations change.
6. regenerate site if source state files or site builder changed.

## protected and sensitive zones

sensitive files include:
- `scripts/evolve.sh`
- `.github/workflows/*`
- `JOURNAL.md`
- `LEARNINGS.md`
- `DAY_COUNT`
- `LAST_POST_DATE_PST`

changes here require explicit rationale and verification notes in commit message or pr description.

## what can go wrong

- broad refactors hide regressions.
- docs drift from runtime behavior.
- generated outputs committed without source updates.

## diagnostics

```bash
git diff --stat
python -m py_compile src/ginji.py
python -m pytest tests/ -q
python scripts/build_site.py
```

## recovery actions

- split oversized changes into smaller commits.
- revert risky changes quickly when checks fail.
- backfill docs and wiki before merge when behavior changes.

## how to verify

- diff is focused and explainable.
- tests cover changed behavior.
- wiki links and site links still resolve.

## related pages

- [testing and safety](./testing-and-safety.md)
- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
- [maintainer playbook local ops](./maintainer-playbook-local-ops.md)
