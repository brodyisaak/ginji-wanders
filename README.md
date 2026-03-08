# ginji

a coding agent that teaches itself

ginji is a python coding agent that reads code, runs tools, and iterates on its own repository. it is intentionally small, transparent, and designed to evolve in public.

## evolution loop

github actions runs ginji every 6 hours. in each session ginji reads itself, picks one small improvement, implements it, tests it, journals it, rebuilds the site, and pushes updates when healthy.

## how it works

ginji runs in two modes: interactive repl and autonomous evolution. in repl mode it accepts prompts and executes tool calls (bash, file io, listing, and search) through the openai api. in evolution mode it follows `scripts/evolve.sh`, checks issues, writes a plan, performs one focused improvement, validates with tests, updates the journal, and publishes.

## how to run it locally

```bash
pip install -r requirements.txt
OPENAI_API_KEY=sk-... python src/ginji.py
```

## how to evolve locally

```bash
OPENAI_API_KEY=sk-... ./scripts/evolve.sh
```

## how to talk to it

open a github issue with label `agent-input`.

## labels

| label | purpose |
| --- | --- |
| `agent-input` | external requests and user-facing suggestions for ginji |
| `agent-self` | self-discovered improvements ginji should tackle later |
| `agent-help-wanted` | blocked items where ginji needs human help |

## architecture tree

```text
src/
tests/
scripts/
skills/
docs/
wiki/
.github/workflows/
```

## links

- documentation: [docs/book/index.md](docs/book/index.md)
- architecture wiki: [wiki/overview.md](wiki/overview.md)
- site: [brodyisaak.github.io/ginji-wanders](https://brodyisaak.github.io/ginji-wanders/)
- docs source: [docs/index.html](docs/index.html)
- github: [github.com/brodyisaak/ginji-wanders](https://github.com/brodyisaak/ginji-wanders)

## license

MIT
