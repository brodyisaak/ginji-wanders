# architecture

- main source file: `src/ginji.py`
- tool layer: bash, file read/write/edit, recursive listing, recursive search
- prompt/system layer: built-in system prompt plus optional cli and skill context
- skills loading layer: recursive `SKILL.md` discovery and prompt prepending
- test layer: pytest coverage focused on tool functions
- state files:
  - `IDENTITY.md`
  - `PERSONALITY.md`
  - `JOURNAL.md`
  - `LEARNINGS.md`
  - `DAY_COUNT`
- generated output: `docs/index.html`, `docs/style.css`, and `docs/.nojekyll`
