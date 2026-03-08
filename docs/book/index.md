# ginji documentation

ginji is a python coding agent that runs in the terminal. it can read and edit files, run shell commands, search code, and evolve itself through a repeatable workflow.

github actions runs a scheduled evolution session daily where ginji reviews itself, makes one small improvement, validates the build, journals the result, and ships forward.

## what makes ginji different

ginji is intentionally compact and transparent. most behavior lives in one runtime file, state is stored in plain markdown files, and evolution decisions stay visible in git history.

## at a glance

- language: python
- runtime: terminal cli + repl
- model provider: openai api
- evolution cadence: daily workflow with pacific guard
- safety gates: `py_compile` and `pytest`

## quick example

```bash
export OPENAI_API_KEY=sk-...
python src/ginji.py
```

example prompts:

> read src/ginji.py and explain how the tool loop works

> add a new test for edit_file and run pytest

> inspect this repo and tell me what should improve next

## deep wiki

- [wiki hub](../../wiki/index.md)
- [architecture](../../wiki/architecture.md)
- [runtime loop and message flow](../../wiki/runtime-loop-and-message-flow.md)
- [evolution pipeline](../../wiki/evolution-pipeline.md)

## where to go next

- [getting started](./getting-started.md)
- [how it works](./how-it-works.md)
- [skills](./skills.md)
- [testing and safety](./testing-and-safety.md)
