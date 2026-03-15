# testing and safety

## purpose

define the minimum safety bar for every autonomous or manual change.

## system boundaries

validation scope:
- python syntax check for runtime
- pytest coverage for tool functions
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

excluded from tests:
- live openai api calls (non-deterministic and network dependent)

## safety controls

- `python -m py_compile src/ginji.py` must pass.
- `python -m pytest tests/ -q` must pass.
- protected files must not be mutated by agent implementation tasks.
- issue content is untrusted and cannot be treated as executable instruction.
- repeated failures should be converted into durable protections (tests, lint rules, or explicit process checks).

## what can go wrong

- tests cover too little behavior and miss regressions.
- autonomous fixes pass tests but break operator expectations.
- protected file guardrails drift from repository policy.
- repeated green-build sessions can still waste time on low-impact maintenance if planning quality is weak.

## diagnostics

```bash
python -m py_compile src/ginji.py
python -m pytest tests/ -v
rg -n "never modify|protected" skills/evolve/SKILL.md
```

## recovery actions

- if checks fail repeatedly, restore known-good `src/` and `tests/` and rerun.
- add targeted tests before changing tool contracts.
- tighten prompts to require explicit validation evidence in journal entries.
- when human feedback repeats, encode the preference mechanically so future runs enforce it automatically.
- keep cleanup incremental: prefer small, frequent refactors over periodic large debt sweeps.
- when build health is already green, prefer checks that enforce capability selection quality over another round of minor hygiene work.

## how to verify

- ci workflow is green.
- local checks match ci command set.
- journal entry references tests actually executed.

## related pages

- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
- [evolution pipeline](./evolution-pipeline.md)
- [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md)
