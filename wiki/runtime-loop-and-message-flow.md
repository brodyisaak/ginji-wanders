# runtime loop and message flow

## purpose

document the exact request-response lifecycle in repl and single-shot modes.

## system boundaries

in scope:
- input mode detection
- message assembly
- tool call execution
- loop termination conditions

out of scope:
- evolution shell orchestration
- github issue processing

## step-by-step flow

1. resolve user task source in priority order:
   - piped stdin
   - `--prompt` flag
   - repl interactive input
2. assemble system context:
   - built-in system prompt
   - optional `--system`
   - optional `--system-file`
   - optional recursive skills payload
3. send messages to openai api with function tool definitions.
4. inspect response:
   - if tool calls exist, execute locally and append tool outputs.
   - if no tool calls exist, print final assistant response.
5. in repl mode, continue loop for next user input until `exit` or `quit`.

## message shape expectations

- tool call arguments must parse as json object.
- each tool output is appended as plain text content.
- malformed arguments are converted to readable error strings.

## what can go wrong

- stdin detection mistakes can accidentally open repl in ci contexts.
- malformed tool args can throw if not wrapped.
- long-running shell commands can block user feedback.

## diagnostics

```bash
printf "list files\n" | OPENAI_API_KEY=sk-... python src/ginji.py
OPENAI_API_KEY=sk-... python src/ginji.py -p "read DAY_COUNT"
OPENAI_API_KEY=sk-... python src/ginji.py
```

verify each mode is selected correctly.

## recovery actions

- normalize input detection logic and add regression tests.
- keep try/except around tool argument parsing and dispatch.
- keep ansi tool feedback visible for long operations.

## how to verify

- piped mode exits after one completion.
- `--prompt` mode exits after one completion.
- repl mode accepts multiple commands and exits cleanly on ctrl+c.

## related pages

- [architecture](./architecture.md)
- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
- [prompts and skills system](./prompts-and-skills-system.md)
