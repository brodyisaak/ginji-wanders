# evolution

`scripts/evolve.sh` is the autonomous pipeline entrypoint. github actions runs it every 6 hours and can also trigger it manually.

session flow:
- planning: read identity, personality, source, memory, and issue digest, then write a measured session contract
- baseline: run the verify command once and capture a numeric starting point
- implementation: execute a bounded iteration loop and keep only metric-improving changes that also pass the guard
- validation: run `py_compile` and `pytest`, with auto-fix attempts and revert fallback
- reporting: ensure journal coverage and process issue responses
- site rebuild: run `python scripts/build_site.py`
- publish: commit, tag, and push

guardrails include one-improvement-per-session, protected-files policy, metric-plus-guard validation, and a pacific once-per-day publish guard so only one journal entry is published each day.

## deep wiki

- [evolution pipeline](../../wiki/evolution-pipeline.md)
- [github actions and scheduling](../../wiki/github-actions-and-scheduling.md)
- [tagging versioning and day count](../../wiki/tagging-versioning-and-day-count.md)
- [testing and safety](../../wiki/testing-and-safety.md)
