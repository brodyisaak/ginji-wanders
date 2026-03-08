# ginji documentation

ginji is a python coding agent that runs in the terminal. it can read and edit files, run shell commands, search code, and evolve itself through a repeatable workflow.

every 6 hours, github actions runs an evolution session where ginji reviews itself, makes one small improvement, validates the build, journals the result, and ships forward.

## what makes ginji different

ginji is intentionally compact and transparent. most behavior lives in one runtime file, state is stored in plain markdown files, and evolution decisions stay visible in git history.

## quick example

```bash
export OPENAI_API_KEY=sk-...
python src/ginji.py
```

example prompts:

> read src/ginji.py and explain how the tool loop works

> add a new test for edit_file and run pytest

> inspect this repo and tell me what should improve next
