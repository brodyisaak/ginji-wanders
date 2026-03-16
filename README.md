# ginji

a coding agent that teaches itself

ginji is a python coding agent that reads code, runs tools, and iterates on its own repository. it is intentionally small, transparent, and designed to evolve in public.

website · documentation · github · deep wiki

- website: [brodyisaak.github.io/ginji-wanders](https://brodyisaak.github.io/ginji-wanders/)
- documentation: [docs/book/index.md](docs/book/index.md)
- github: [github.com/brodyisaak/ginji-wanders](https://github.com/brodyisaak/ginji-wanders)
- deep wiki: [wiki/index.md](wiki/index.md)

## what ginji is

ginji started as a compact python cli agent and keeps improving itself in small, test-backed increments. it is designed to stay understandable: one core runtime, explicit tool contracts, plain markdown memory, and visible commits.

the benchmark is practical developer utility: can someone trust ginji for real coding work in a live repo.

## evolution loop

github actions runs ginji every 6 hours (four times per day) with pacific-time guardrails. ginji still publishes only one journal entry per pacific day. in each session ginji:

1. reads its own source and memory files
2. reviews issue input and writes a measured session plan
3. establishes a baseline metric and guard
4. runs a bounded internal iteration loop to keep only metric-improving changes
5. runs compile + tests
6. writes journal and learnings entries
7. rebuilds the site
8. commits, tags, and pushes if healthy

## agent-first operating model

- humans set intent; agents execute and iterate.
- when work stalls, prioritize building missing scaffolding (tests, docs, guardrails, tooling) before retrying.
- once the build is healthy, prefer capability growth over another round of syntax, validation, or error-message cleanup.
- keep repository docs as source of truth with index-style entry points and linked depth.
- convert repeated feedback into enforceable checks so quality compounds over time.
- every healthy session should define a metric, capture a baseline, and pass a guard before a change is kept.
- bounded iteration beats vague busywork: one small loop with measurable gains is better than another generic cleanup day.

## how it works

ginji runs in two modes: interactive repl and autonomous evolution. in repl mode it accepts prompts and executes tool calls (bash, file io, listing, and search) through the openai api. in evolution mode it follows `scripts/evolve.sh`, checks issues, writes a measured session plan, captures a baseline, runs a bounded keep-or-discard loop, validates with tests, updates state files, and publishes.

## talk to ginji

open an issue with the `agent-input` label. clear, specific issue reports help the agent prioritize meaningful work.

## how to run it locally

```bash
pip install -r requirements.txt
OPENAI_API_KEY=sk-... python src/ginji.py
```

## how to evolve locally

```bash
OPENAI_API_KEY=sk-... ./scripts/evolve.sh
```

## labels

| label | purpose |
| --- | --- |
| `agent-input` | external requests and user-facing suggestions for ginji |
| `agent-self` | self-discovered improvements ginji should tackle later |
| `agent-help-wanted` | blocked items where ginji needs human help |

## project memory and state

- `IDENTITY.md`: mission and operating rules
- `PERSONALITY.md`: voice and style boundaries
- `JOURNAL.md`: day-by-day execution record
- `LEARNINGS.md`: practical lessons captured per session
- `DAY_COUNT`: current day number
- `LAST_POST_DATE_PST`: pacific schedule guard
- `EVOLUTION_RESULTS.tsv`: measurable keep/discard/crash log for the evolution harness

## maintainer deep wiki

- [wiki hub](wiki/index.md)
- [runtime loop and message flow](wiki/runtime-loop-and-message-flow.md)
- [tools contracts and failure modes](wiki/tools-contracts-and-failure-modes.md)
- [evolution pipeline](wiki/evolution-pipeline.md)
- [incident runbook](wiki/incident-runbook.md)
- [maintainer playbook](wiki/maintainer-playbook-local-ops.md)

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

- site: [brodyisaak.github.io/ginji-wanders](https://brodyisaak.github.io/ginji-wanders/)
- documentation: [docs/book/index.md](docs/book/index.md)
- deep wiki hub: [wiki/index.md](wiki/index.md)
- architecture internals: [wiki/architecture.md](wiki/architecture.md)
- runtime loop: [wiki/runtime-loop-and-message-flow.md](wiki/runtime-loop-and-message-flow.md)
- evolution pipeline: [wiki/evolution-pipeline.md](wiki/evolution-pipeline.md)
- testing and safety: [wiki/testing-and-safety.md](wiki/testing-and-safety.md)
- docs source: [docs/index.html](docs/index.html)
- github: [github.com/brodyisaak/ginji-wanders](https://github.com/brodyisaak/ginji-wanders)

## license

MIT
