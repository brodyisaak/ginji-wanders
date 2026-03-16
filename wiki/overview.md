# overview

## purpose

ginji is a self-evolving python coding agent. this page defines system intent, operational scope, and the benchmark target: become better than codex cli one commit at a time.

## system boundaries

in scope:
- terminal runtime in `src/ginji.py`
- autonomous evolution pipeline in `scripts/evolve.sh`
- generated public site from `scripts/build_site.py`
- tests for tool functions in `tests/test_ginji.py`

out of scope:
- non-openai model providers
- hidden state stores outside repository files
- autonomous multi-repo mutation

## operating model

1. ginji receives a prompt from stdin, `--prompt`, or interactive repl input.
2. ginji calls the openai api with function tools.
3. ginji executes tool calls locally and returns string outputs.
4. ginji repeats until completion and prints the final response.
5. on scheduled evolution runs, ginji writes a measured session plan, captures a baseline, runs a bounded metric loop, journals, rebuilds site, commits, tags, and pushes.

## what can go wrong

- schedule runs too frequently and increments day count more than once per day.
- journal entries are overwritten instead of prepended.
- untrusted issue text injects misleading instructions into planning.
- a session runs without a usable metric and falls back to vague maintenance work.

## diagnostics

```bash
cat DAY_COUNT
head -n 40 JOURNAL.md
rg -n "schedule|cron|LAST_POST_DATE_PST" .github/workflows/evolve.yml scripts/evolve.sh
```

## recovery actions

- restore missing journal history from git history before next run.
- enforce once-per-day guard in `scripts/evolve.sh`.
- keep issue formatting and boundary guards active in `scripts/format_issues.py`.
- enforce metric, baseline, verify, and guard requirements in the session plan contract.

## how to verify

```bash
python -m py_compile src/ginji.py
python -m pytest tests/ -q
python scripts/build_site.py
```

site should show the latest day and full journal timeline.

## related pages

- [architecture](./architecture.md)
- [evolution pipeline](./evolution-pipeline.md)
- [state files](./state-files.md)
