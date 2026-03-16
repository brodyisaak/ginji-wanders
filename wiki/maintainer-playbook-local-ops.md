# maintainer playbook local ops

## purpose

provide a repeatable local workflow for maintainers to run, debug, and publish safe changes.

## system boundaries

local operations include:
- running ginji interactively
- running evolution locally
- rebuilding site
- checking workflows and git status

## standard local session

1. install dependencies.
2. run compile and tests.
3. run target command (`src/ginji.py` or `scripts/evolve.sh`).
4. inspect changed files and confirm whether a harness change belongs in the kernel or the runtime.
5. rebuild site and verify links.
6. commit and push.

## command checklist

```bash
pip install -r requirements.txt
python -m py_compile src/ginji.py
python -m py_compile scripts/evolve_runtime.py
python -m pytest tests/ -q
python scripts/build_site.py
OPENAI_API_KEY=sk-... ./scripts/evolve.sh
```

## what can go wrong

- local env differs from ci runner behavior.
- gh auth missing for issue steps.
- stale generated docs not rebuilt before commit.

## diagnostics

```bash
python --version
gh auth status
git status --short
rg -n "architecture wiki|documentation|github" docs/index.html
```

## recovery actions

- align python version with workflow (`3.11`).
- re-authenticate gh before testing issue response steps.
- rerun site build whenever journal, identity, or day count changes.
- prefer `scripts/evolve_runtime.py` for harness behavior changes and reserve kernel edits for invariant changes only.

## how to verify

- no unexpected files in git diff.
- tests and compile pass locally.
- generated site points to deep wiki entrypoint.

## related pages

- [incident runbook](./incident-runbook.md)
- [evolution pipeline](./evolution-pipeline.md)
- [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md)
