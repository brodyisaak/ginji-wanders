# testing and safety

- pytest coverage currently targets tool functions in `src/ginji.py`
- syntax validation runs with `python -m py_compile src/ginji.py`
- protected files are declared in evolution skill rules
- issue content is treated as untrusted input
- each session targets one focused change
- if build health fails repeatedly, revert strategy is available
- journaling is mandatory and should be honest about outcomes

## deep wiki

- [testing and safety](../../wiki/testing-and-safety.md)
- [tools contracts and failure modes](../../wiki/tools-contracts-and-failure-modes.md)
- [incident runbook](../../wiki/incident-runbook.md)
