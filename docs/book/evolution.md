# evolution

`scripts/evolve.sh` is the autonomous pipeline entrypoint and protected kernel. github actions runs it every 6 hours and can also trigger it manually.

session flow:
- kernel: verify secrets, run preflight build, enforce pacific day guard, and preserve journal history
- runtime: `scripts/evolve_runtime.py` reads identity, personality, source, memory, and issue digest, then writes a measured session contract
- anti-stall planning: runtime reads recent journal history and should pivot when the same benchmark ability has stalled across multiple sessions
- baseline: runtime runs the verify command once and captures a numeric starting point
- implementation: runtime executes a bounded iteration loop and keeps only metric-improving changes that also pass the guard
- validation: kernel reruns `py_compile` and `pytest` before publish
- reporting: ensure journal coverage and process issue responses
- site rebuild: run `python scripts/build_site.py`
- publish: commit, tag, and push

guardrails include one-improvement-per-session, protected-kernel policy, metric-plus-guard validation, and a pacific once-per-day publish guard so only one journal entry is published each day.

## deep wiki

- [evolution pipeline](../../wiki/evolution-pipeline.md)
- [github actions and scheduling](../../wiki/github-actions-and-scheduling.md)
- [tagging versioning and day count](../../wiki/tagging-versioning-and-day-count.md)
- [testing and safety](../../wiki/testing-and-safety.md)
