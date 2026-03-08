# evolution

`scripts/evolve.sh` is the autonomous pipeline entrypoint. github actions runs it every 6 hours and can also trigger it manually.

session flow:
- planning: read identity, personality, source, memory, and issue digest
- implementation: execute one focused improvement with small tasks
- validation: run `py_compile` and `pytest`, with auto-fix attempts and revert fallback
- reporting: ensure journal coverage and process issue responses
- site rebuild: run `python scripts/build_site.py`
- publish: commit, tag, and push

guardrails include one-improvement-per-session and a protected-files policy enforced by skill instructions.
