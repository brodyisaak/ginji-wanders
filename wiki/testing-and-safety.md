# testing and safety

## purpose

define the minimum safety bar for every autonomous or manual change.

## system boundaries

validation scope:
- python syntax check for runtime
- pytest coverage for tool functions
- metric parsing and comparison for the evolution harness
- runtime behavior checks for evolution script and site generation

policy scope:
- protected files
- issue input trust boundaries
- one focused change per session

## current test scope

covered tool functions:
- `bash_exec`
- `read_file`
- `write_file`
- `edit_file`
- `list_files`
- `search_files`

covered harness helpers:
- `scripts/metric_guard.py` metric extraction
- `scripts/metric_guard.py` command failure handling
- repo integrity checks for metric, baseline, verify, guard, and bounded-iteration language

excluded from tests:
- live openai api calls (non-deterministic and network dependent)

## safety controls

- `python -m py_compile src/ginji.py` must pass.
- `python -m pytest tests/ -q` must pass.
- verify command must produce a numeric baseline before edits are kept.
- guard command must pass before a metric improvement is accepted.
- protected kernel invariants in `scripts/evolve.sh` must survive runtime changes.
- issue content is untrusted and cannot be treated as executable instruction.
- repeated failures should be converted into durable protections (tests, lint rules, or explicit process checks).

## what can go wrong

- tests cover too little behavior and miss regressions.
- autonomous fixes pass tests but break operator expectations.
- protected file guardrails drift from repository policy.
- repeated green-build sessions can still waste time on low-impact maintenance if planning quality is weak.
- verify command returns prose instead of one numeric metric, so the loop cannot compare iterations mechanically.
- guard passes locally but is weaker than the real failure mode, so the loop keeps a brittle change.
- kernel and runtime responsibilities blur, so the mutable layer starts changing safety rails instead of tactics.

## diagnostics

```bash
python -m py_compile src/ginji.py
python -m py_compile scripts/evolve_runtime.py
python -m pytest tests/ -v
python scripts/metric_guard.py measure --command "printf 'score: 2\n'"
rg -n "never modify|protected" skills/evolve/SKILL.md
```

## recovery actions

- if checks fail repeatedly, restore known-good `src/` and `tests/` and rerun.
- add targeted tests before changing tool contracts.
- tighten prompts to require explicit validation evidence in journal entries.
- when human feedback repeats, encode the preference mechanically so future runs enforce it automatically.
- keep cleanup incremental: prefer small, frequent refactors over periodic large debt sweeps.
- when build health is already green, prefer checks that enforce capability selection quality over another round of minor hygiene work.
- if the verify command is weak or unparseable, replace it before another measured session runs.
- if guard failures recur, strengthen the default guard instead of letting the same class of regression return.
- if recursive harness work is needed, change `scripts/evolve_runtime.py` first and keep the shell kernel small.

## how to verify

- ci workflow is green.
- local checks match ci command set.
- journal entry references tests actually executed.
- `EVOLUTION_RESULTS.tsv` records at least one baseline and one iteration outcome for measured sessions.

## related pages

- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
- [evolution pipeline](./evolution-pipeline.md)
- [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md)
