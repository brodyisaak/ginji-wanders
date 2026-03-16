# architecture

- main source file: `src/ginji.py`
- tool layer: bash, file read/write/edit, recursive listing, recursive search
- prompt/system layer: built-in system prompt plus optional cli and skill context
- skills loading layer: recursive `SKILL.md` discovery and prompt prepending
- test layer: pytest coverage focused on tool functions
- evolution harness split:
  - `scripts/evolve.sh` protected kernel
  - `scripts/evolve_runtime.py` mutable strategy layer
- state files:
  - `IDENTITY.md`
  - `PERSONALITY.md`
  - `JOURNAL.md`
  - `LEARNINGS.md`
  - `DAY_COUNT`
  - `LAST_POST_DATE_PST`
- generated output: `docs/index.html`, `docs/style.css`, and `docs/.nojekyll`

## deep wiki

- [wiki hub](../../wiki/index.md)
- [architecture internals](../../wiki/architecture.md)
- [runtime loop and message flow](../../wiki/runtime-loop-and-message-flow.md)
- [prompts and skills system](../../wiki/prompts-and-skills-system.md)
